from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTest(TestCase):
    """
    Tests for custom user model and authentication
    """

    def test_create_user(self):
        """
        Test user creation
        Use case: ensures users can register correctly
        """
        user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.assertEqual(user.username, "testuser")

    def test_login(self):
        """
        Test login functionality
        Use case: ensures authentication system works
        """
        User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        login = self.client.login(
            username="testuser",
            password="testpass123"
        )
        self.assertTrue(login)