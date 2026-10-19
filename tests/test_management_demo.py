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

    def validate_demo(self, cookie, csrf, *, corrupt=False):
        path = "/api/demo-bundle-corrupt" if corrupt else "/api/demo-bundle"
        status, _headers, bundle_bytes = self.request(
            "GET", path, headers={"Cookie": cookie}
        )
        self.assertEqual(status, 200)
        status, _headers, data = self.request(
            "POST",
            "/api/validate",
            body=bundle_bytes,
            headers={
                "Cookie": cookie,
                "X-CSRF-Token": csrf,
                "Content-Type": "application/octet-stream",
            },
        )
        return status, self.json_body(data)

    def action(self, cookie, csrf, action):
        status, _headers, data = self.request(
            "POST",
            "/api/action",
            body={"action": action},
            headers={"Cookie": cookie, "X-CSRF-Token": csrf},
        )
        return status, self.json_body(data)

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

    def test_bundle_routes_require_authentication_and_csrf(self):
        status, _headers, data = self.request("GET", "/api/demo-bundle")
        self.assertEqual(status, 401)
        self.assertEqual(self.json_body(data)["error"], "authentication_required")
        cookie, _csrf, _headers = self.login()
        bundle_bytes = self.application.demo_bundle()
        status, _headers, data = self.request(
            "POST",
            "/api/validate",
            body=bundle_bytes,
            headers={
                "Cookie": cookie,
                "Content-Type": "application/octet-stream",
            },
        )
        self.assertEqual(status, 403)
        self.assertEqual(self.json_body(data)["error"], "csrf_rejected")
        self.assertEqual(self.application.simulator.state, "idle")

    def test_valid_bundle_runs_b2_and_stops_before_authorization(self):
        cookie, csrf, _headers = self.login()
        status, value = self.validate_demo(cookie, csrf)
        self.assertEqual(status, 200)
        verification = value["verification"]
        self.assertTrue(verification["host_verification_passed"])
        self.assertFalse(verification["installation_authorized"])
        self.assertTrue(
            all(check["status"] == "pass" for check in verification["checks"].values())
        )
        self.assertEqual(value["status"]["simulator"]["state"], "verified")
        self.assertFalse(
            value["status"]["simulator"]["simulation_install_authorized"]
        )
        self.assertEqual(value["status"]["available_actions"], ["authorize"])

    def test_corrupt_bundle_fails_closed_without_state_change(self):
        cookie, csrf, _headers = self.login()
        status, value = self.validate_demo(cookie, csrf, corrupt=True)
        self.assertEqual(status, 200)
        verification = value["verification"]
        self.assertFalse(verification["host_verification_passed"])
        self.assertEqual(
            verification["checks"]["authenticity"]["code"],
            "component_hash_mismatch",
        )
        self.assertIsNone(verification["manifest"])
        self.assertEqual(value["status"]["simulator"]["state"], "idle")
        self.assertEqual(value["status"]["simulator"]["generation"], 0)

    def test_successful_simulation_commits_and_retains_previous_known_good(self):
        cookie, csrf, _headers = self.login()
        status, _value = self.validate_demo(cookie, csrf)
        self.assertEqual(status, 200)
        expected_states = [
            ("authorize", "verified"),
            ("stage", "staged"),
            ("begin_write", "writing_candidate"),
            ("pending_boot", "pending_boot"),
            ("healthy", "healthy"),
            ("commit", "committed"),
        ]
        for action, expected_state in expected_states:
            status, value = self.action(cookie, csrf, action)
            self.assertEqual(status, 200)
            self.assertEqual(value["simulator"]["state"], expected_state)
        self.assertEqual(value["simulator"]["known_good"]["release_sequence"], 2)
        self.assertEqual(
            value["simulator"]["previous_known_good"]["release_sequence"], 1
        )
        self.assertIsNone(value["simulator"]["candidate"])

    def test_invalid_action_is_rejected_without_persisted_change(self):
        cookie, csrf, _headers = self.login()
        before = self.application.simulator.snapshot
        status, value = self.action(cookie, csrf, "stage")
        self.assertEqual(status, 409)
        self.assertEqual(value["error"], "transition_rejected")
        self.assertEqual(self.application.simulator.snapshot, before)

    def test_boot_failure_supports_logical_rollback_or_recovery_required(self):
        cookie, csrf, _headers = self.login()

        def reach_boot_failure():
            status, _value = self.validate_demo(cookie, csrf)
            self.assertEqual(status, 200)
            for action in (
                "authorize",
                "stage",
                "begin_write",
                "pending_boot",
                "boot_failure",
            ):
                status, value = self.action(cookie, csrf, action)
                self.assertEqual(status, 200)
            self.assertEqual(value["simulator"]["state"], "failed")
            self.assertEqual(
                value["simulator"]["known_good"]["release_sequence"], 1
            )

        reach_boot_failure()
        status, value = self.action(cookie, csrf, "rollback")
        self.assertEqual(status, 200)
        self.assertEqual(value["simulator"]["state"], "rolled_back")
        self.assertEqual(value["simulator"]["known_good"]["release_sequence"], 1)

        status, value = self.action(cookie, csrf, "reset")
        self.assertEqual(status, 200)
        self.assertEqual(value["simulator"]["state"], "idle")
        reach_boot_failure()
        status, value = self.action(cookie, csrf, "recovery_required")
        self.assertEqual(status, 200)
        self.assertEqual(value["simulator"]["state"], "recovery_required")
        self.assertFalse(value["capabilities"]["hardware_recovery_verified"])
        self.assertIn("no physical rescue", value["recovery_explanation"].lower())


if __name__ == "__main__":
    unittest.main()
