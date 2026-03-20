from django.test import TestCase
from django.contrib.auth.models import User


class UserTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(user.username, "testuser")

    def test_login(self):
        User.objects.create_user(username="testuser", password="testpass123")
        login = self.client.login(username="testuser", password="testpass123")
        self.assertTrue(login)
