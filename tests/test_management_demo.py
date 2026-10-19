import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import management_demo as demo  # noqa: E402


class ManagementDemoHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.application = demo.DemoApplication(self.temporary.name)
        self.server = demo.create_server(self.application, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temporary.cleanup()

    def request(self, method, path, *, body=None, headers=None):
        connection = http.client.HTTPConnection(self.host, self.port, timeout=3)
        if isinstance(body, dict):
            body = json.dumps(body).encode("utf-8")
            headers = {"Content-Type": "application/json", **(headers or {})}
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        result = (response.status, dict(response.getheaders()), data)
        connection.close()
        return result

    @staticmethod
    def json_body(data):
        return json.loads(data.decode("utf-8"))

    def login(self):
        status, headers, data = self.request(
            "POST",
            "/api/login",
            body={"username": "admin", "password": "slot20-demo"},
        )
        self.assertEqual(status, 200)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        return cookie, self.json_body(data)["csrf_token"], headers

    def test_server_binds_only_ipv4_loopback(self):
        self.assertEqual(self.host, "127.0.0.1")

    def test_shell_has_security_headers_and_simulation_labels(self):
        status, headers, data = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["Cache-Control"], "no-store")
        text = data.decode("utf-8")
        self.assertIn("Offline host simulation", text)
        self.assertIn("No camera is connected", text)

    def test_api_status_requires_authentication(self):
        status, _headers, data = self.request("GET", "/api/status")
        self.assertEqual(status, 401)
        self.assertEqual(self.json_body(data)["error"], "authentication_required")

    def test_bad_credentials_fail_without_cookie(self):
        status, headers, data = self.request(
            "POST",
            "/api/login",
            body={"username": "admin", "password": "wrong"},
        )
        self.assertEqual(status, 401)
        self.assertNotIn("Set-Cookie", headers)
        self.assertEqual(self.json_body(data)["error"], "invalid_credentials")

    def test_authenticated_status_is_sanitized_and_explicit(self):
        cookie, _csrf, login_headers = self.login()
        self.assertIn("HttpOnly", login_headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", login_headers["Set-Cookie"])
        status, _headers, data = self.request(
            "GET", "/api/status", headers={"Cookie": cookie}
        )
        self.assertEqual(status, 200)
        value = self.json_body(data)
        self.assertEqual(value["mode"], "offline_host_simulation")
        self.assertEqual(value["hardware_profile"], demo.TARGET_HARDWARE_PROFILE)
        self.assertEqual(value["simulator"]["state"], "idle")
        self.assertFalse(value["capabilities"]["camera_contact"])
        self.assertFalse(value["capabilities"]["flash_writing"])
        self.assertFalse(value["capabilities"]["hardware_recovery_verified"])
        self.assertNotIn(str(Path(self.temporary.name)), data.decode("utf-8"))

    def test_logout_requires_csrf_and_invalidates_session(self):
        cookie, csrf, _headers = self.login()
        status, _headers, data = self.request(
            "POST", "/api/logout", body=b"", headers={"Cookie": cookie}
        )
        self.assertEqual(status, 403)
        self.assertEqual(self.json_body(data)["error"], "csrf_rejected")

        status, headers, _data = self.request(
            "POST",
            "/api/logout",
            body=b"",
            headers={"Cookie": cookie, "X-CSRF-Token": csrf},
        )
        self.assertEqual(status, 200)
        self.assertIn("Max-Age=0", headers["Set-Cookie"])
        status, _headers, _data = self.request(
            "GET", "/api/status", headers={"Cookie": cookie}
        )
        self.assertEqual(status, 401)

    def test_routes_are_explicit_and_host_is_checked(self):
        status, _headers, data = self.request("GET", "/../AGENTS.md")
        self.assertEqual(status, 404)
        self.assertEqual(self.json_body(data)["error"], "route_not_found")
        status, _headers, data = self.request(
            "GET", "/", headers={"Host": "camera.example"}
        )
        self.assertEqual(status, 400)
        self.assertEqual(self.json_body(data)["error"], "invalid_host")


if __name__ == "__main__":
    unittest.main()
