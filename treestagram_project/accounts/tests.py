import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.core.signing import TimestampSigner

from posts.models import Post, Comment, Notification
from accounts.adapter import TreestagramAccountAdapter
from accounts.signals import activate_user_on_confirm
from accounts.forms import SignupForm, LoginForm

from caretaker.models import CaretakerAssignment
from trees.models import Tree

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
        from trees.models import Tree

        Tree.objects.create(
            tree_id=99999,
            spc_common="Oak",
            spc_latin="Quercus",
            created_at="2020-01-01",
            tree_dbh=10,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            sidewalk="NoDamage",
            root_stone=False,
            root_grate=False,
            root_other=False,
            trunk_wire=False,
            trnk_light=False,
            trnk_other=False,
            brch_light=False,
            brch_shoe=False,
            brch_other=False,
            address="123 Test St",
            zip_city="TestCity",
            borough="Manhattan",
            latitude=40.7,
            longitude=-73.9,
        )
        response = self.client.post(
            reverse("api-create-post"),
            data=json.dumps({"tree_id": "99999"}),
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


# ---------------- ADAPTER + SIGNAL TESTS ---------------- #


class AdapterSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="adapteruser",
            email="adapter@test.com",
            password="testpass123",
            is_active=False,
        )

        # Fake email address object (since allauth model is heavy)
        self.email_address = MagicMock()
        self.email_address.user = self.user

        self.adapter = TreestagramAccountAdapter()

    # -------- ADAPTER: confirm_email -------- #
    @patch("allauth.account.adapter.DefaultAccountAdapter.confirm_email")
    def test_confirm_email_already_active(self, mock_super):
        self.user.is_active = True
        self.user.save()

        self.adapter.confirm_email(request=None, email_address=self.email_address)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    # -------- ADAPTER: redirect URL -------- #
    @patch("accounts.adapter.os.environ.get")
    def test_redirect_url_with_env(self, mock_env):
        mock_env.return_value = "http://frontend.com"
        url = self.adapter.get_email_verification_redirect_url(email_address=None)
        self.assertIn("frontend.com", url)

    def test_redirect_url_default(self):
        url = self.adapter.get_email_verification_redirect_url(email_address=None)
        self.assertIn("localhost:5173", url)

    # -------- SIGNAL: activate_user_on_confirm -------- #
    def test_signal_activates_user(self):
        self.user.is_active = False
        self.user.save()

        activate_user_on_confirm(
            sender=None,
            request=None,
            email_address=self.email_address,
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_signal_user_already_active(self):
        self.user.is_active = True
        self.user.save()

        activate_user_on_confirm(
            sender=None,
            request=None,
            email_address=self.email_address,
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


# ---------------- FORMS COVERAGE ---------------- #


class FormsTest(TestCase):

    # -------- SIGNUP FORM VALID -------- #
    def test_signup_form_valid(self):
        form = SignupForm(
            data={
                "username": "formuser",
                "email": "form@test.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "borough": "Manhattan",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.email, "form@test.com")
        self.assertEqual(user.borough, "Manhattan")

    # -------- SIGNUP FORM INVALID -------- #
    def test_signup_form_password_mismatch(self):
        form = SignupForm(
            data={
                "username": "formuser2",
                "email": "form@test.com",
                "password1": "StrongPass123",
                "password2": "WrongPass",
            }
        )

        self.assertFalse(form.is_valid())

    # -------- SAVE commit=False -------- #
    def test_signup_form_commit_false(self):
        form = SignupForm(
            data={
                "username": "formuser3",
                "email": "form@test.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save(commit=False)
        self.assertEqual(user.email, "form@test.com")

    # -------- OPTIONAL FIELDS -------- #
    def test_signup_optional_fields(self):
        form = SignupForm(
            data={
                "username": "formuser4",
                "email": "form@test.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            }
        )

        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.borough, "")

    # -------- INIT CUSTOMIZATION -------- #
    def test_signup_form_init(self):
        form = SignupForm()

        # help_text removed
        for field in form.fields.values():
            self.assertIsNone(field.help_text)

        # placeholders exist
        self.assertIn("placeholder", form.fields["password1"].widget.attrs)
        self.assertIn("placeholder", form.fields["password2"].widget.attrs)

    # -------- LOGIN FORM -------- #
    def test_login_form_fields(self):
        form = LoginForm()

        self.assertIn("username", form.fields)
        self.assertIn("password", form.fields)

        self.assertEqual(
            form.fields["username"].widget.attrs.get("placeholder"), "Username"
        )
        self.assertEqual(
            form.fields["password"].widget.attrs.get("placeholder"), "Password"
        )


# ============================================================
# views.py coverage
# ============================================================


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="logoutuser", password="testpass123", is_active=True
        )

    def test_logout_success(self):
        self.client.login(username="logoutuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    def test_logout_requires_login(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)


class SvelteAppViewTest(TestCase):
    def test_svelte_app_renders(self):
        response = self.client.get("/")
        # Should serve index.html (200) or redirect
        self.assertIn(response.status_code, [200, 301, 302])

    @patch("accounts.views.os.environ.get")
    def test_get_frontend_url_from_env(self, mock_env):
        mock_env.return_value = "http://myapp.com"
        from accounts.views import get_frontend_url

        self.assertEqual(get_frontend_url(), "http://myapp.com")

    def test_get_frontend_url_default(self):
        from accounts.views import get_frontend_url

        with patch.dict("os.environ", {}, clear=True):
            url = get_frontend_url()
        self.assertEqual(url, "http://localhost:5173")


class CustomConfirmEmailViewTest(TestCase):
    def test_confirm_email_view_context(self):
        from accounts.views import CustomConfirmEmailView
        from allauth.account.views import ConfirmEmailView

        self.assertTrue(issubclass(CustomConfirmEmailView, ConfirmEmailView))


# ============================================================
# api_views.py coverage
# ============================================================


class SignupAPITest(TestCase):
    @patch("accounts.api_views.send_confirmation_email")
    def test_signup_success(self, mock_send):
        response = self.client.post(
            reverse("api-signup"),
            data=json.dumps(
                {
                    "username": "newuser",
                    "email": "new@test.com",
                    "password1": "StrongPass123",
                    "password2": "StrongPass123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["requires_verification"])
        mock_send.assert_called_once()

    @patch("accounts.api_views.send_confirmation_email")
    def test_signup_email_send_failure(self, mock_send):
        mock_send.side_effect = Exception("SMTP error")
        response = self.client.post(
            reverse("api-signup"),
            data=json.dumps(
                {
                    "username": "failuser",
                    "email": "fail@test.com",
                    "password1": "StrongPass123",
                    "password2": "StrongPass123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to send confirmation email", response.json()["error"])

    def test_signup_invalid_form(self):
        response = self.client.post(
            reverse("api-signup"),
            data=json.dumps(
                {
                    "username": "",
                    "email": "bad",
                    "password1": "x",
                    "password2": "y",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_invalid_json(self):
        response = self.client.post(
            reverse("api-signup"),
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class ConfirmEmailAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="confirmuser",
            email="confirm@test.com",
            password="testpass123",
            is_active=False,
        )

    def _make_token(self, user_pk):
        signer = TimestampSigner()
        return signer.sign(user_pk)

    def test_confirm_email_success(self):
        token = self._make_token(self.user.pk)
        response = self.client.get(reverse("confirm_email", kwargs={"token": token}))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_confirm_email_invalid_token(self):
        response = self.client.get(
            reverse("confirm_email", kwargs={"token": "invalid:token"})
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])

    def test_confirm_email_expired_token(self):
        signer = TimestampSigner()
        token = signer.sign(self.user.pk)
        with patch("accounts.api_views.TimestampSigner.unsign") as mock_unsign:
            from django.core.signing import SignatureExpired

            mock_unsign.side_effect = SignatureExpired("expired")
            response = self.client.get(
                reverse("confirm_email", kwargs={"token": token})
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("expired", response.json()["error"].lower())

    def test_confirm_email_user_not_found(self):
        signer = TimestampSigner()
        token = signer.sign(99999)  # non-existent pk
        response = self.client.get(reverse("confirm_email", kwargs={"token": token}))
        self.assertEqual(response.status_code, 400)


class LoginByEmailAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="emaillogin",
            email="emaillogin@test.com",
            password="testpass123",
            is_active=True,
        )

    def test_login_by_email(self):
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps(
                {
                    "username": "emaillogin@test.com",
                    "password": "testpass123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_login_inactive_user(self):
        User.objects.create_user(
            username="inactivelogin",
            email="inactive@test.com",
            password="testpass123",
            is_active=False,
        )
        response = self.client.post(
            reverse("api-login"),
            data=json.dumps(
                {
                    "username": "inactivelogin",
                    "password": "testpass123",
                }
            ),
            content_type="application/json",
        )
        # Django's authenticate() returns None for inactive users → 401
        # OR returns user but is_active=False check → 403
        self.assertIn(response.status_code, [401, 403])

    def test_login_invalid_json(self):
        response = self.client.post(
            reverse("api-login"),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class ResendVerificationAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resenduser",
            email="resend@test.com",
            password="testpass123",
            is_active=False,
        )

    @patch("accounts.api_views.send_confirmation_email")
    def test_resend_success(self, mock_send):
        response = self.client.post(
            reverse("api-resend-verification"),
            data=json.dumps({"email": "resend@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once_with(self.user)

    def test_resend_already_verified(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.post(
            reverse("api-resend-verification"),
            data=json.dumps({"email": "resend@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)


class ForgotPasswordAPITest(TestCase):
    def test_forgot_password_invalid_json(self):
        response = self.client.post(
            reverse("api-forgot-password"),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_forgot_password_missing_email(self):
        response = self.client.post(
            reverse("api-forgot-password"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_forgot_password_nonexistent_email(self):
        # Should still return 200 (don't leak user existence)
        response = self.client.post(
            reverse("api-forgot-password"),
            data=json.dumps({"email": "nobody@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)


class ResetPasswordAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser",
            email="reset@test.com",
            password="oldpass123",
            is_active=True,
        )

    def test_reset_password_missing_password(self):
        response = self.client.post(
            reverse("api-reset-password", args=["invalid", "token"]),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password_invalid_uid(self):
        response = self.client.post(
            reverse("api-reset-password", args=["invalid", "token"]),
            data=json.dumps({"password": "NewPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password_invalid_token(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.post(
            reverse("api-reset-password", args=[uid, "badtoken"]),
            data=json.dumps({"password": "NewPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password_weak_password(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            reverse("api-reset-password", args=[uid, token]),
            data=json.dumps({"password": "123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password_success(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            reverse("api-reset-password", args=[uid, token]),
            data=json.dumps({"password": "NewStrongPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])


class ChangePasswordAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="changepass",
            password="OldPass123!",
            is_active=True,
        )
        self.client.login(username="changepass", password="OldPass123!")

    def test_change_password_success(self):
        response = self.client.post(
            reverse("api-change-password"),
            data=json.dumps(
                {
                    "current_password": "OldPass123!",
                    "new_password": "NewPass456!",
                    "confirm_password": "NewPass456!",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_change_password_missing_fields(self):
        response = self.client.post(
            reverse("api-change-password"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_change_password_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse("api-change-password"),
            data=json.dumps(
                {
                    "current_password": "OldPass123!",
                    "new_password": "NewPass456!",
                    "confirm_password": "NewPass456!",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_change_password_invalid_json(self):
        response = self.client.post(
            reverse("api-change-password"),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class PostCommentAPIExtraTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="postuser",
            password="testpass123",
            is_active=True,
        )
        self.client.login(username="postuser", password="testpass123")
        self.post = Post.objects.create(author=self.user, tree_name="Maple")

    def test_create_post_invalid_json(self):
        response = self.client.post(
            reverse("api-create-post"),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_post_missing_tree_name(self):
        response = self.client.post(
            reverse("api-create-post"),
            data=json.dumps({"body": "no tree name"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_post_unauthenticated(self):
        self.client.logout()
        response = self.client.post(
            reverse("api-create-post"),
            data=json.dumps({"tree_name": "Oak"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_toggle_like_post_not_found(self):
        response = self.client.post(reverse("api-toggle-like", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_add_comment_invalid_json(self):
        response = self.client.post(
            reverse("api-add-comment", args=[self.post.id]),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_add_comment_empty_text(self):
        response = self.client.post(
            reverse("api-add-comment", args=[self.post.id]),
            data=json.dumps({"text": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_add_comment_post_not_found(self):
        response = self.client.post(
            reverse("api-add-comment", args=[99999]),
            data=json.dumps({"text": "hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_comment_not_owner(self):
        other = User.objects.create_user(username="other2", password="testpass123")
        comment = Comment.objects.create(author=other, post=self.post, text="Other")
        response = self.client.post(
            reverse("api-edit-comment", args=[comment.id]),
            data=json.dumps({"text": "hacked"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_comment_not_found(self):
        response = self.client.post(
            reverse("api-edit-comment", args=[99999]),
            data=json.dumps({"text": "test"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_comment_invalid_json(self):
        comment = Comment.objects.create(author=self.user, post=self.post, text="Old")
        response = self.client.post(
            reverse("api-edit-comment", args=[comment.id]),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_comment_empty_text(self):
        comment = Comment.objects.create(author=self.user, post=self.post, text="Old")
        response = self.client.post(
            reverse("api-edit-comment", args=[comment.id]),
            data=json.dumps({"text": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_comment_not_found(self):
        response = self.client.post(reverse("api-delete-comment", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_comment_permission_denied(self):
        other = User.objects.create_user(username="other3", password="testpass123")
        other_post = Post.objects.create(author=other, tree_name="Oak")
        comment = Comment.objects.create(author=other, post=other_post, text="Other")
        response = self.client.post(reverse("api-delete-comment", args=[comment.id]))
        self.assertEqual(response.status_code, 403)

    def test_delete_post_not_found(self):
        response = self.client.post(reverse("api-delete-post", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_fetch_my_tagged_posts(self):
        self.post.tagged_users.add(self.user)
        response = self.client.get(reverse("api-my-tagged-posts"))
        self.assertEqual(response.status_code, 200)


class NotificationsAPIExtraTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notifuser",
            password="testpass123",
            is_active=True,
        )

    def test_notifications_unauthenticated(self):
        response = self.client.get(reverse("api-notifications"))
        self.assertEqual(response.status_code, 401)

    def test_notifications_unread_count_unauthenticated(self):
        response = self.client.get(reverse("api-notifications-unread-count"))
        self.assertEqual(response.status_code, 401)

    def test_mark_notifications_read_unauthenticated(self):
        response = self.client.post(
            reverse("api-notifications-mark-read"),
            data=json.dumps({"ids": []}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_mark_all_notifications_read_unauthenticated(self):
        response = self.client.post(reverse("api-notifications-mark-all-read"))
        self.assertEqual(response.status_code, 401)

    def test_mark_notifications_read_invalid_json(self):
        self.client.login(username="notifuser", password="testpass123")
        response = self.client.post(
            reverse("api-notifications-mark-read"),
            data="bad json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


# ============================================================
# for becoming admins and such
# ============================================================
class BecomeAdminTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!", email="test@test.com"
        )
        self.client.force_login(self.user)

    def test_correct_answer_promotes_to_admin(self):
        res = self.client.post(
            "/api/become-admin/",
            data={"answer": "yEs i LOV3 trees"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "admin")

    def test_wrong_answer_rejected(self):
        res = self.client.post(
            "/api/become-admin/",
            data={"answer": "wrong answer"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.role, "admin")

    def test_unauthenticated_rejected(self):
        self.client.logout()
        res = self.client.post(
            "/api/become-admin/",
            data={"answer": "yEs i LOV3 trees"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)


class MyCaretakerTreesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="caretaker", password="TestPass123!", email="ct@test.com"
        )
        self.tree = Tree.objects.create(
            tree_id=99999,
            spc_common="Test Oak",
            spc_latin="Quercus testus",
            created_at="2015",
            tree_dbh=10,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            sidewalk="NoDamage",
            root_stone=False,
            root_grate=False,
            root_other=False,
            trunk_wire=False,
            trnk_light=False,
            trnk_other=False,
            brch_light=False,
            brch_shoe=False,
            brch_other=False,
            address="123 Test St",
            zip_city="TestCity",
            borough="Manhattan",
            latitude=40.7,
            longitude=-74.0,
        )
        CaretakerAssignment.objects.create(user=self.user, tree_id=99999)
        self.client.force_login(self.user)

    def test_returns_assigned_trees(self):
        res = self.client.get("/api/my-caretaker-trees/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["trees"]), 1)
        self.assertEqual(data["trees"][0]["tree_id"], "99999")
        self.assertEqual(data["trees"][0]["tree_name"], "Test Oak")

    def test_unauthenticated_rejected(self):
        self.client.logout()
        res = self.client.get("/api/my-caretaker-trees/")
        self.assertEqual(res.status_code, 401)

    def test_empty_if_no_assignments(self):
        CaretakerAssignment.objects.all().delete()
        res = self.client.get("/api/my-caretaker-trees/")
        data = res.json()
        self.assertEqual(data["trees"], [])
