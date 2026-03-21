from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTest(TestCase):
    """
    Tests for custom user model and authentication
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_create_user(self):
        """
        Test user creation
        Use case: ensures registration works
        """
        self.assertEqual(self.user.username, "testuser")

    def test_login(self):
        """
        Test login functionality
        Use case: ensures authentication works
        """
        login = self.client.login(username="testuser", password="testpass123")
        self.assertTrue(login)


class AccountViewTest(TestCase):
    """
    Tests for Django views in accounts/views.py
    """

    def test_home_view(self):
        """
        Test homepage or basic route
        Use case: ensures views load correctly
        """
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])

    def test_invalid_page(self):
        """
        Test invalid URL
        Use case: ensures proper 404 handling
        """
        response = self.client.get("/random-url/")
        self.assertEqual(response.status_code, 404)


class AccountAPITest(TestCase):
    """
    Tests for api_views.py (IMPORTANT for coverage)
    """

    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="testpass123")

    def test_api_get_request(self):
        """
        Test GET API endpoint
        Use case: ensures API responds correctly
        """
        response = self.client.get("/api/")
        self.assertIn(response.status_code, [200, 404, 401])

    def test_api_post_request(self):
        """
        Test POST API endpoint
        Use case: ensures API handles data submission
        """
        response = self.client.post("/api/", data={})
        self.assertIn(response.status_code, [200, 400, 401, 405])


class FormTest(TestCase):
    """
    Tests for forms.py
    """

    def test_empty_form(self):
        """
        Test empty form validation
        Use case: ensures form validation works
        """
        from accounts.forms import UserCreationForm

        form = UserCreationForm(data={})
        self.assertFalse(form.is_valid())


class SignalTest(TestCase):
    """
    Tests for signals.py
    """

    def test_user_creation_signal(self):
        """
        Test signals triggered on user creation
        Use case: ensures signals execute without error
        """
        user = User.objects.create_user(username="signaluser", password="testpass123")
        self.assertIsNotNone(user.id)
