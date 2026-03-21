from django.test import TestCase
from unittest.mock import patch


class BasicTest(TestCase):
    def test_homepage(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])


# ---------------- URLS.PY COVERAGE ---------------- #


class URLCoverageTest(TestCase):

    def test_admin_url(self):
        response = self.client.get("/admin/")
        self.assertIn(response.status_code, [200, 302])

    def test_trees_include(self):
        response = self.client.get("/trees/")
        self.assertIn(response.status_code, [200, 404])

    def test_accounts_include(self):
        response = self.client.get("/signup/")
        self.assertIn(response.status_code, [200, 302])

    def test_api_include(self):
        response = self.client.get("/api/")
        self.assertIn(response.status_code, [200, 404, 405])

    # -------- RESET PASSWORD REDIRECT -------- #
    def test_reset_password_redirect_default(self):
        response = self.client.get("/reset-password/abc123/token123/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("localhost:5173", response.url)

    @patch("treestagram.urls.os.environ.get")
    def test_reset_password_redirect_env(self, mock_env):
        mock_env.return_value = "http://frontend.com"

        response = self.client.get("/reset-password/abc/token/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("frontend.com", response.url)

    # -------- MEDIA SERVE -------- #
    def test_media_serve(self):
        response = self.client.get("/media/test.jpg")
        self.assertIn(response.status_code, [200, 404])

    # -------- CATCH-ALL ROUTE -------- #
    def test_catch_all_route(self):
        response = self.client.get("/some/random/frontend/route/")
        self.assertEqual(response.status_code, 200)
