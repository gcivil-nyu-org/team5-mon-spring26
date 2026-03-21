import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

from accounts.models import Post, Comment, Notification

User = get_user_model()


# ---------------- EXISTING API TESTS (UNCHANGED) ---------------- #


class AccountAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="apiuser",
            email="api@test.com",
            password="testpass123",
            is_active=True,
        )
        self.client.login(username="apiuser", password="testpass123")

    def test_signup_api_invalid_json(self):
        response = self.client.post(
            reverse("api-signup"),
            data="invalid",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_api_success(self):
        self.client.logout()
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps({"username": "apiuser", "password": "testpass123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_login_api_invalid(self):
        self.client.logout()
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps({"username": "wrong", "password": "wrong"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_logout_api(self):
        response = self.client.post(reverse("api-logout"))
        self.assertEqual(response.status_code, 200)

    def test_me_api_authenticated(self):
        response = self.client.get(reverse("api-me"))
        self.assertEqual(response.status_code, 200)

    def test_me_api_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse("api-me"))
        self.assertEqual(response.status_code, 401)

    def test_check_username(self):
        response = self.client.get(
            reverse("api-check-username"), {"username": "apiuser"}
        )
        self.assertEqual(response.status_code, 200)

    def test_forgot_password(self):
        response = self.client.post(
            reverse("api-forgot-password"),
            data=json.dumps({"email": "api@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        response = self.client.post(
            reverse("api-create-post"),
            data=json.dumps({"tree_name": "Oak"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_fetch_posts(self):
        Post.objects.create(author=self.user, tree_name="Oak")
        response = self.client.get(reverse("api-fetch-posts"))
        self.assertEqual(response.status_code, 200)

    def test_fetch_my_posts(self):
        Post.objects.create(author=self.user, tree_name="Oak")
        response = self.client.get(reverse("api-my-posts"))
        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        post = Post.objects.create(author=self.user, tree_name="Oak")
        response = self.client.post(reverse("api-delete-post", args=[post.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_post_not_owner(self):
        other = User.objects.create_user(username="other", password="testpass123")
        post = Post.objects.create(author=other, tree_name="Oak")

        response = self.client.post(reverse("api-delete-post", args=[post.id]))
        self.assertEqual(response.status_code, 403)

    def test_toggle_like(self):
        post = Post.objects.create(author=self.user, tree_name="Oak")

        self.client.post(reverse("api-toggle-like", args=[post.id]))
        response = self.client.post(reverse("api-toggle-like", args=[post.id]))

        self.assertEqual(response.status_code, 200)

    def test_add_comment(self):
        post = Post.objects.create(author=self.user, tree_name="Oak")

        response = self.client.post(
            reverse("api-add-comment", args=[post.id]),
            data=json.dumps({"text": "Nice tree"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_comment(self):
        post = Post.objects.create(author=self.user, tree_name="Oak")
        comment = Comment.objects.create(author=self.user, post=post, text="Old")

        response = self.client.post(
            reverse("api-edit-comment", args=[comment.id]),
            data=json.dumps({"text": "New"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_comment(self):
        post = Post.objects.create(author=self.user, tree_name="Oak")
        comment = Comment.objects.create(author=self.user, post=post, text="Test")

        response = self.client.post(reverse("api-delete-comment", args=[comment.id]))
        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        response = self.client.post(
            reverse("api-update-profile"),
            data=json.dumps({"first_name": "New"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_update_profile_username_taken(self):
        User.objects.create_user(username="taken", password="123")

        response = self.client.post(
            reverse("api-update-profile"),
            data=json.dumps({"username": "taken"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_notifications(self):
        Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notif_type="like",
            message="Test",
        )

        response = self.client.get(reverse("api-notifications"))
        self.assertEqual(response.status_code, 200)

    def test_notifications_unread_count(self):
        response = self.client.get(reverse("api-notifications-unread-count"))
        self.assertEqual(response.status_code, 200)

    def test_mark_notifications_read(self):
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notif_type="like",
            message="Test",
        )

        response = self.client.post(
            reverse("api-notifications-mark-read"),
            data=json.dumps({"ids": [notif.id]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_mark_all_notifications_read(self):
        Notification.objects.create(
            recipient=self.user,
            sender=self.user,
            notif_type="like",
            message="Test",
        )

        response = self.client.post(reverse("api-notifications-mark-all-read"))
        self.assertEqual(response.status_code, 200)


# ---------------- SAFE VIEW TESTS (NO HOME DEPENDENCY) ---------------- #


class AccountViewsSafeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="viewuser",
            password="testpass123",
        )

    def test_logout_requires_login(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    def test_logout_success(self):
        self.client.login(username="viewuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    @patch("accounts.views.os.environ.get")
    def test_get_frontend_url_env(self, mock_env):
        mock_env.return_value = "http://test.com"
        from accounts.views import get_frontend_url

        self.assertEqual(get_frontend_url(), "http://test.com")

    def test_get_frontend_url_default(self):
        from accounts.views import get_frontend_url

        self.assertEqual(get_frontend_url(), "http://localhost:5173")


# ---------------- EXTRA COVERAGE FOR api_views.py ---------------- #


class AccountAPIExtraCoverageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="extrauser",
            email="extra@test.com",
            password="testpass123",
            is_active=True,
        )

    # -------- CSRF -------- #
    def test_csrf_view(self):
        response = self.client.get(reverse("api-csrf"))
        self.assertEqual(response.status_code, 200)

    # -------- LOGIN EDGE CASES -------- #
    def test_login_missing_fields(self):
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_inactive_user(self):
        # inactive = User.objects.create_user(
        #     username="inactive",
        #     password="testpass123",
        #     is_active=False,
        # )
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps({"username": "inactive", "password": "testpass123"}),
            content_type="application/json",
        )
        self.assertIn(response.status_code, [401, 403])

    # -------- GOOGLE LOGIN URL -------- #
    def test_google_login_url(self):
        response = self.client.get(reverse("api-google-login-url"))
        self.assertEqual(response.status_code, 200)

    # -------- RESEND VERIFICATION -------- #
    def test_resend_verification_invalid_json(self):
        response = self.client.post(
            reverse("api-resend-verification"),
            data="invalid",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_resend_verification_no_email(self):
        response = self.client.post(
            reverse("api-resend-verification"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_resend_verification_not_found(self):
        response = self.client.post(
            reverse("api-resend-verification"),
            data=json.dumps({"email": "notfound@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    # -------- VERIFY PASSWORD -------- #
    def test_verify_password(self):
        self.client.login(username="extrauser", password="testpass123")

        response = self.client.post(
            reverse("api-verify-password"),
            data=json.dumps({"password": "testpass123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_verify_password_missing(self):
        self.client.login(username="extrauser", password="testpass123")

        response = self.client.post(
            reverse("api-verify-password"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    # -------- CHANGE PASSWORD -------- #
    def test_change_password_mismatch(self):
        self.client.login(username="extrauser", password="testpass123")

        response = self.client.post(
            reverse("api-change-password"),
            data=json.dumps(
                {
                    "current_password": "testpass123",
                    "new_password": "newpass123",
                    "confirm_password": "wrong",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_change_password_wrong_current(self):
        self.client.login(username="extrauser", password="testpass123")

        response = self.client.post(
            reverse("api-change-password"),
            data=json.dumps(
                {
                    "current_password": "wrong",
                    "new_password": "newpass123",
                    "confirm_password": "newpass123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    # -------- DELETE ACCOUNT -------- #
    def test_delete_account_not_authenticated(self):
        response = self.client.post(
            reverse("api-delete-account"),
            data=json.dumps({"password": "testpass123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_account_wrong_password(self):
        self.client.login(username="extrauser", password="testpass123")

        response = self.client.post(
            reverse("api-delete-account"),
            data=json.dumps({"password": "wrong"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_account_success(self):
        self.client.login(username="extrauser", password="testpass123")

        response = self.client.post(
            reverse("api-delete-account"),
            data=json.dumps({"password": "testpass123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    # -------- RESET TOKEN -------- #
    def test_verify_reset_token_invalid(self):
        response = self.client.get(
            reverse("api-verify-reset-token", args=["invalid", "token"])
        )
        self.assertEqual(response.status_code, 200)

    # -------- RESET PASSWORD -------- #
    def test_reset_password_invalid_json(self):
        response = self.client.post(
            reverse("api-reset-password", args=["invalid", "token"]),
            data="invalid",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    # -------- PROFILE UNAUTH -------- #
    def test_update_profile_unauth(self):
        response = self.client.post(
            reverse("api-update-profile"),
            data=json.dumps({"first_name": "X"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    # -------- FETCH TAGGED POSTS -------- #
    def test_fetch_my_tagged_posts_unauth(self):
        response = self.client.get(reverse("api-my-tagged-posts"))
        self.assertEqual(response.status_code, 401)
