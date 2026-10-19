#!/usr/bin/env python3
"""Loopback-only Slot-20 management interface demonstration.

This is a PC-hosted offline demo. It has no camera, device-node, partition,
installer, network-discovery, or flash-writing interface.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import hmac
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import tempfile
import threading
import time
from typing import Any
from urllib.parse import urlsplit

from update_state_simulator import TARGET_HARDWARE_PROFILE, UpdateStateSimulator, VersionRef


LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_DEMO_USERNAME = "admin"
DEFAULT_DEMO_PASSWORD = "slot20-demo"
SESSION_COOKIE = "slot20_demo_session"
SESSION_TTL_SECONDS = 30 * 60
MAX_SESSIONS = 8
MAX_JSON_BYTES = 4_096
MAX_CREDENTIAL_BYTES = 128
PASSWORD_ROUNDS = 120_000
ASSET_DIR = Path(__file__).with_name("management_demo_assets")
ASSET_ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}
DEMO_LIMITATION = (
    "Offline host simulation only. No camera was contacted, no firmware is "
    "installed, and rollback or independent hardware recovery is not proven."
)


class RequestError(ValueError):
    """A bounded client-request failure with a safe public code."""

    def __init__(self, status: HTTPStatus, code: str):
        super().__init__(code)
        self.status = status
        self.code = code


@dataclass(frozen=True)
class DemoSession:
    csrf_token: str
    expires_at: float
    created_at: float


class DemoApplication:
    """In-memory auth boundary plus one bounded file-backed simulator record."""

    def __init__(
        self,
        data_dir: str | os.PathLike[str],
        *,
        password: str = DEFAULT_DEMO_PASSWORD,
        clock=time.monotonic,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.data_dir.is_dir():
            raise ValueError("demo data path must be a directory")
        if not isinstance(password, str) or not 1 <= len(password.encode("utf-8")) <= MAX_CREDENTIAL_BYTES:
            raise ValueError("demo password length is invalid")
        self._clock = clock
        self._password_salt = secrets.token_bytes(16)
        self._password_digest = self._derive_password(password)
        self._sessions: dict[str, DemoSession] = {}
        self._lock = threading.RLock()
        self.state_path = self.data_dir / "update-state.json"
        if self.state_path.exists():
            self.simulator = UpdateStateSimulator.load(self.state_path)
        else:
            self.simulator = UpdateStateSimulator.create(
                self.state_path,
                VersionRef(
                    hardware_profile=TARGET_HARDWARE_PROFILE,
                    release_version="1.0.0-demo",
                    release_sequence=1,
                    security_epoch=1,
                    bundle_sha256="1" * 64,
                ),
            )

    def _derive_password(self, password: str) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self._password_salt, PASSWORD_ROUNDS
        )

    def authenticate(self, username: Any, password: Any) -> tuple[str, DemoSession] | None:
        if not isinstance(username, str) or not isinstance(password, str):
            return None
        if len(username.encode("utf-8")) > MAX_CREDENTIAL_BYTES:
            return None
        if not 1 <= len(password.encode("utf-8")) <= MAX_CREDENTIAL_BYTES:
            return None
        supplied = self._derive_password(password)
        if username != DEFAULT_DEMO_USERNAME or not hmac.compare_digest(
            supplied, self._password_digest
        ):
            return None
        with self._lock:
            self._purge_sessions()
            while len(self._sessions) >= MAX_SESSIONS:
                oldest = min(
                    self._sessions,
                    key=lambda token: self._sessions[token].created_at,
                )
                del self._sessions[oldest]
            now = self._clock()
            token = secrets.token_urlsafe(32)
            session = DemoSession(
                csrf_token=secrets.token_urlsafe(24),
                created_at=now,
                expires_at=now + SESSION_TTL_SECONDS,
            )
            self._sessions[token] = session
            return token, session

    def get_session(self, token: str | None) -> DemoSession | None:
        if token is None:
            return None
        with self._lock:
            self._purge_sessions()
            return self._sessions.get(token)

    def logout(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)

    def status(self) -> dict[str, Any]:
        with self._lock:
            snapshot = self.simulator.snapshot
        return {
            "mode": "offline_host_simulation",
            "hardware_profile": TARGET_HARDWARE_PROFILE,
            "limitation": DEMO_LIMITATION,
            "simulator": snapshot,
            "capabilities": {
                "camera_contact": False,
                "flash_writing": False,
                "hardware_recovery_verified": False,
                "bundle_verifier": "C3.3 pending",
            },
        }

    def _purge_sessions(self) -> None:
        now = self._clock()
        expired = [
            token for token, session in self._sessions.items() if session.expires_at <= now
        ]
        for token in expired:
            del self._sessions[token]


class DemoHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, handler_class, application: DemoApplication):
        self.application = application
        super().__init__(server_address, handler_class)


class ManagementDemoHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "Slot20OfflineDemo/1"
    sys_version = ""

    @property
    def application(self) -> DemoApplication:
        return self.server.application  # type: ignore[attr-defined]

    def log_message(self, format_string: str, *args: Any) -> None:
        # Keep diagnostics concise and omit bodies, cookies, and credentials.
        message = format_string % args
        print(f"[{self.log_date_time_string()}] {self.client_address[0]} {message}")

    def do_GET(self) -> None:
        try:
            self._validate_host()
            path = urlsplit(self.path).path
            if path in ASSET_ROUTES:
                self._serve_asset(path)
                return
            if path == "/api/status":
                self._require_session()
                self._send_json(HTTPStatus.OK, self.application.status())
                return
            self._send_error(HTTPStatus.NOT_FOUND, "route_not_found")
        except RequestError as error:
            self._send_error(error.status, error.code)

    def do_POST(self) -> None:
        try:
            self._validate_host()
            path = urlsplit(self.path).path
            if path == "/api/login":
                self._login()
                return
            if path == "/api/logout":
                token, _session = self._require_session(require_csrf=True)
                self._require_empty_body()
                self.application.logout(token)
                self._send_json(
                    HTTPStatus.OK,
                    {"ok": True},
                    cookie=f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0",
                )
                return
            self._send_error(HTTPStatus.NOT_FOUND, "route_not_found")
        except RequestError as error:
            self._send_error(error.status, error.code)

    def _login(self) -> None:
        value = self._read_json()
        if not isinstance(value, dict) or set(value) != {"username", "password"}:
            raise RequestError(HTTPStatus.BAD_REQUEST, "invalid_login_request")
        result = self.application.authenticate(value["username"], value["password"])
        if result is None:
            raise RequestError(HTTPStatus.UNAUTHORIZED, "invalid_credentials")
        token, session = result
        cookie = (
            f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; "
            f"Max-Age={SESSION_TTL_SECONDS}"
        )
        self._send_json(
            HTTPStatus.OK,
            {
                "authenticated": True,
                "csrf_token": session.csrf_token,
                "mode": "offline_host_simulation",
            },
            cookie=cookie,
        )

    def _serve_asset(self, path: str) -> None:
        filename, content_type = ASSET_ROUTES[path]
        asset_path = ASSET_DIR / filename
        try:
            data = asset_path.read_bytes()
        except OSError as exc:
            raise RequestError(HTTPStatus.INTERNAL_SERVER_ERROR, "asset_unavailable") from exc
        self._send_bytes(HTTPStatus.OK, data, content_type)

    def _validate_host(self) -> None:
        host = self.headers.get("Host", "")
        hostname = host.rsplit(":", 1)[0].lower()
        if hostname not in {"127.0.0.1", "localhost"}:
            raise RequestError(HTTPStatus.BAD_REQUEST, "invalid_host")

    def _session_token(self) -> str | None:
        raw = self.headers.get("Cookie")
        if not raw or len(raw) > 1_024:
            return None
        cookie = SimpleCookie()
        try:
            cookie.load(raw)
        except Exception:
            return None
        morsel = cookie.get(SESSION_COOKIE)
        return morsel.value if morsel is not None else None

    def _require_session(self, *, require_csrf: bool = False) -> tuple[str, DemoSession]:
        token = self._session_token()
        session = self.application.get_session(token)
        if token is None or session is None:
            raise RequestError(HTTPStatus.UNAUTHORIZED, "authentication_required")
        if require_csrf and not hmac.compare_digest(
            self.headers.get("X-CSRF-Token", ""), session.csrf_token
        ):
            raise RequestError(HTTPStatus.FORBIDDEN, "csrf_rejected")
        return token, session

    def _read_json(self) -> Any:
        if self.headers.get_content_type() != "application/json":
            raise RequestError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "json_required")
        data = self._read_body(MAX_JSON_BYTES)
        try:
            return json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "invalid_json") from exc

    def _require_empty_body(self) -> None:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            return
        try:
            length = int(raw_length, 10)
        except ValueError as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "invalid_content_length") from exc
        if length != 0:
            raise RequestError(HTTPStatus.BAD_REQUEST, "request_body_not_allowed")

    def _read_body(self, maximum: int) -> bytes:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise RequestError(HTTPStatus.LENGTH_REQUIRED, "content_length_required")
        try:
            length = int(raw_length, 10)
        except ValueError as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "invalid_content_length") from exc
        if not 0 < length <= maximum:
            raise RequestError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "request_size_limit")
        data = self.rfile.read(length)
        if len(data) != length:
            raise RequestError(HTTPStatus.BAD_REQUEST, "truncated_request")
        return data

    def _send_error(self, status: HTTPStatus, code: str) -> None:
        self._send_json(status, {"error": code})

    def _send_json(
        self, status: HTTPStatus, value: Any, *, cookie: str | None = None
    ) -> None:
        data = json.dumps(
            value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self._send_bytes(status, data, "application/json; charset=utf-8", cookie=cookie)

    def _send_bytes(
        self,
        status: HTTPStatus,
        data: bytes,
        content_type: str,
        *,
        cookie: str | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'",
        )
        if cookie is not None:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)


def create_server(
    application: DemoApplication, *, port: int = DEFAULT_PORT
) -> DemoHTTPServer:
    if type(port) is not int or not 0 <= port <= 65_535:
        raise ValueError("port must be between 0 and 65535")
    return DemoHTTPServer((LOOPBACK_HOST, port), ManagementDemoHandler, application)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="local demo state directory; defaults to a temporary directory",
    )
    args = parser.parse_args()
    password = os.environ.get("SLOT20_DEMO_PASSWORD", DEFAULT_DEMO_PASSWORD)
    temporary = None
    if args.data_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="slot20-management-demo-")
        data_dir = Path(temporary.name)
    else:
        data_dir = args.data_dir
    application = DemoApplication(data_dir, password=password)
    server = create_server(application, port=args.port)
    host, port = server.server_address
    print(f"Slot-20 OFFLINE HOST SIMULATION: http://{host}:{port}/")
    print(f"Demo user: {DEFAULT_DEMO_USERNAME}")
    if password == DEFAULT_DEMO_PASSWORD:
        print("Demo password: slot20-demo (not a production credential)")
    print(DEMO_LIMITATION)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if temporary is not None:
            temporary.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
