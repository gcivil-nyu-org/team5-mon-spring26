import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.models import Post, Comment, Notification

User = get_user_model()


class AccountAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="apiuser",
            email="api@test.com",
            password="testpass123",
            is_active=True,
        )
        self.client.login(username="apiuser", password="testpass123")

    # ---------------- AUTH ---------------- #

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

    # ---------------- PASSWORD ---------------- #

    def test_forgot_password(self):
        response = self.client.post(
            reverse("api-forgot-password"),
            data=json.dumps({"email": "api@test.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    # ---------------- POSTS ---------------- #

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
        response = self.client.get(reverse("api-fetch-my-posts"))
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

    # ---------------- LIKES ---------------- #

    def test_toggle_like(self):
        post = Post.objects.create(author=self.user, tree_name="Oak")

        response = self.client.post(reverse("api-toggle-like", args=[post.id]))
        self.assertEqual(response.status_code, 200)

        # toggle again (unlike)
        response = self.client.post(reverse("api-toggle-like", args=[post.id]))
        self.assertEqual(response.status_code, 200)

    # ---------------- COMMENTS ---------------- #

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

    # ---------------- PROFILE ---------------- #

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

    # ---------------- NOTIFICATIONS ---------------- #

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
