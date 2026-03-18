import unittest

from fastapi.testclient import TestClient

from engine.server import create_app


class TestServerCors(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_preflight_allows_vite_localhost_origin(self) -> None:
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")

    def test_preflight_rejects_unlisted_origin(self) -> None:
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("access-control-allow-origin", response.headers)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
