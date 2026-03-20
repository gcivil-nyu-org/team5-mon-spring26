from django.test import TestCase


class BasicTest(TestCase):
    def test_homepage(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])
