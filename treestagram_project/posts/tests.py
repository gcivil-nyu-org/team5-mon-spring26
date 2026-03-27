"""
Tests for the Posts app.

Covers: Post CRUD, Like toggle, Comment CRUD, Notification generation,
        Tree validation, Tree following, and Feed personalisation.

Run with:
    python manage.py test posts -v2
"""

import json
from django.test import TestCase, Client
from accounts.models import User
from trees.models import Tree
from posts.models import Post, Like, Comment, Notification, TreeFollow


# ─── Shared Helpers ─────────────────────────────────────────────────────────


class _BaseTestCase(TestCase):
    """Shared fixtures for every test class in this module."""

    @classmethod
    def setUpTestData(cls):
        """Create reusable users and a tree — runs once per TestCase class."""
        cls.alice = User.objects.create_user(
            username="alice",
            password="pass1234",
            email="alice@test.com",
            borough="Queens",
        )
        cls.bob = User.objects.create_user(
            username="bob",
            password="pass1234",
            email="bob@test.com",
            borough="Brooklyn",
        )
        cls.tree = Tree.objects.create(
            tree_id=180683,
            created_at="2015-08-01",
            tree_dbh=12,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            spc_latin="Acer rubrum",
            spc_common="red maple",
            sidewalk="NoDamage",
            problems="",
            root_stone=False,
            root_grate=False,
            root_other=False,
            trunk_wire=False,
            trnk_light=False,
            trnk_other=False,
            brch_light=False,
            brch_shoe=False,
            brch_other=False,
            address="123 MAIN ST",
            zip_city="New York",
            borough="Queens",
            latitude=40.7128,
            longitude=-74.0060,
        )

    def _login(self, user):
        """Return an authenticated Django test client."""
        c = Client()
        c.login(username=user.username, password="pass1234")
        return c


# ═══════════════════════════════════════════════════════════════════════════
#  MODEL LAYER TESTS
# ═══════════════════════════════════════════════════════════════════════════


class PostModelTests(_BaseTestCase):
    """Unit tests for the Post model."""

    def test_create_post(self):
        """A post can be created with all required fields."""
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
            body="Beautiful tree!",
        )
        self.assertEqual(post.tree_name, "red maple")
        self.assertEqual(post.author.username, "alice")

    def test_str_representation(self):
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
        )
        self.assertEqual(str(post), "red maple by alice")

    def test_default_health(self):
        """Health defaults to 'Good' when not specified."""
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
        )
        self.assertEqual(post.health, "Good")

    def test_ordering_newest_first(self):
        """Posts are ordered by newest first (Meta.ordering = ['-created_at'])."""
        p1 = Post.objects.create(author=self.alice, tree=self.tree, tree_name="first")
        p2 = Post.objects.create(author=self.alice, tree=self.tree, tree_name="second")
        posts = list(Post.objects.all())
        self.assertEqual(posts[0].id, p2.id)
        self.assertEqual(posts[1].id, p1.id)


class LikeModelTests(_BaseTestCase):
    """Unit tests for the Like model."""

    def test_unique_like_per_user_post(self):
        """A user cannot like the same post twice (unique_together constraint)."""
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
        )
        Like.objects.create(user=self.bob, post=post)
        with self.assertRaises(Exception):
            Like.objects.create(user=self.bob, post=post)

    def test_different_users_can_like(self):
        """Different users can like the same post."""
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
        )
        Like.objects.create(user=self.alice, post=post)
        Like.objects.create(user=self.bob, post=post)
        self.assertEqual(post.likes.count(), 2)


class CommentModelTests(_BaseTestCase):
    """Unit tests for the Comment model."""

    def test_create_comment(self):
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
        )
        comment = Comment.objects.create(
            author=self.bob,
            post=post,
            text="Looks great!",
        )
        self.assertEqual(comment.text, "Looks great!")
        self.assertEqual(comment.post.id, post.id)

    def test_comment_ordering_oldest_first(self):
        """Comments are ordered oldest-first (Meta.ordering = ['created_at'])."""
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
        )
        c1 = Comment.objects.create(author=self.bob, post=post, text="First")
        Comment.objects.create(author=self.alice, post=post, text="Second")
        comments = list(post.comments.all())
        self.assertEqual(comments[0].id, c1.id)


class TreeFollowModelTests(_BaseTestCase):
    """Unit tests for the TreeFollow model."""

    def test_follow_tree(self):
        follow = TreeFollow.objects.create(user=self.alice, tree=self.tree)
        self.assertTrue(follow.notify)  # default is True
        self.assertEqual(follow.tree.tree_id, 180683)

    def test_unique_follow(self):
        """A user cannot follow the same tree twice."""
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        with self.assertRaises(Exception):
            TreeFollow.objects.create(user=self.alice, tree=self.tree)


class NotificationModelTests(_BaseTestCase):
    """Unit tests for the Notification model."""

    def test_create_notification(self):
        notif = Notification.objects.create(
            recipient=self.alice,
            sender=self.bob,
            notif_type="like",
            message="Bob liked your post",
        )
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.notif_type, "like")


# ═══════════════════════════════════════════════════════════════════════════
#  API / VIEW LAYER TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TreeValidationAPITests(_BaseTestCase):
    """Tests for GET /api/validate-tree/."""

    def test_valid_tree_id(self):
        c = self._login(self.alice)
        resp = c.get("/api/validate-tree/", {"tree_id": "180683"})
        data = resp.json()
        self.assertTrue(data["exists"])
        self.assertEqual(data["tree"]["spc_common"], "red maple")

    def test_invalid_tree_id(self):
        c = self._login(self.alice)
        resp = c.get("/api/validate-tree/", {"tree_id": "999999"})
        data = resp.json()
        self.assertFalse(data["exists"])

    def test_missing_tree_id(self):
        c = self._login(self.alice)
        resp = c.get("/api/validate-tree/")
        data = resp.json()
        self.assertFalse(data["exists"])


class PostCreateAPITests(_BaseTestCase):
    """Tests for POST /api/posts/create/."""

    def test_create_post_success(self):
        c = self._login(self.alice)
        resp = c.post(
            "/api/posts/create/",
            data=json.dumps(
                {"tree_id": "180683", "body": "Hello tree!", "health": "Good"}
            ),
            content_type="application/json",
        )
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["post"]["tree_name"], "red maple")

    def test_create_post_invalid_tree(self):
        c = self._login(self.alice)
        resp = c.post(
            "/api/posts/create/",
            data=json.dumps({"tree_id": "999999", "body": "Oops"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()["success"])

    def test_create_post_unauthenticated(self):
        c = Client()
        resp = c.post(
            "/api/posts/create/",
            data=json.dumps({"tree_id": "180683", "body": "Nope"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_create_post_missing_tree_id(self):
        c = self._login(self.alice)
        resp = c.post(
            "/api/posts/create/",
            data=json.dumps({"body": "No tree given"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


class PostFetchAPITests(_BaseTestCase):
    """Tests for GET /api/posts/."""

    def test_fetch_posts(self):
        Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
            body="Test",
        )
        c = self._login(self.alice)
        resp = c.get("/api/posts/")
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["posts"]), 1)

    def test_followed_trees_appear_first(self):
        """Posts from followed trees should appear before other posts."""
        tree2 = Tree.objects.create(
            tree_id=999001,
            created_at="2018-01-01",
            tree_dbh=8,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Fair",
            spc_latin="Quercus rubra",
            spc_common="northern red oak",
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
            address="456 OAK AVE",
            zip_city="New York",
            borough="Brooklyn",
            latitude=40.6782,
            longitude=-73.9442,
        )
        # Alice follows tree2 but NOT self.tree
        TreeFollow.objects.create(user=self.alice, tree=tree2)

        # Create posts on both trees
        Post.objects.create(
            author=self.bob, tree=self.tree, tree_name="red maple", body="Unfollowed"
        )
        Post.objects.create(
            author=self.bob, tree=tree2, tree_name="northern red oak", body="Followed"
        )

        c = self._login(self.alice)
        resp = c.get("/api/posts/")
        posts = resp.json()["posts"]

        # The followed tree's post should appear first
        self.assertEqual(posts[0]["tree_name"], "northern red oak")


class LikeToggleAPITests(_BaseTestCase):
    """Tests for POST /api/posts/<id>/like/."""

    def setUp(self):
        self.post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
            body="Like me",
        )

    def test_like_post(self):
        c = self._login(self.bob)
        resp = c.post(f"/api/posts/{self.post.id}/like/")
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["liked"])
        self.assertEqual(data["likes_count"], 1)

    def test_unlike_post(self):
        """Liking a post twice should toggle it off."""
        c = self._login(self.bob)
        c.post(f"/api/posts/{self.post.id}/like/")  # like
        resp = c.post(f"/api/posts/{self.post.id}/like/")  # unlike
        data = resp.json()
        self.assertFalse(data["liked"])
        self.assertEqual(data["likes_count"], 0)

    def test_like_creates_notification(self):
        """Liking someone else's post should create a notification."""
        c = self._login(self.bob)
        c.post(f"/api/posts/{self.post.id}/like/")
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.alice,
                notif_type="like",
            ).exists()
        )


class CommentAPITests(_BaseTestCase):
    """Tests for POST /api/posts/<id>/comment/."""

    def setUp(self):
        self.post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
            body="Comment on me",
        )

    def test_add_comment(self):
        c = self._login(self.bob)
        resp = c.post(
            f"/api/posts/{self.post.id}/comment/",
            data=json.dumps({"text": "Nice tree!"}),
            content_type="application/json",
        )
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["comment"]["text"], "Nice tree!")

    def test_empty_comment_rejected(self):
        c = self._login(self.bob)
        resp = c.post(
            f"/api/posts/{self.post.id}/comment/",
            data=json.dumps({"text": ""}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_comment_creates_notification(self):
        c = self._login(self.bob)
        c.post(
            f"/api/posts/{self.post.id}/comment/",
            data=json.dumps({"text": "Great shot!"}),
            content_type="application/json",
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.alice,
                notif_type="comment",
            ).exists()
        )

    def test_edit_own_comment(self):
        c = self._login(self.bob)
        resp = c.post(
            f"/api/posts/{self.post.id}/comment/",
            data=json.dumps({"text": "Original"}),
            content_type="application/json",
        )
        comment_id = resp.json()["comment"]["id"]
        resp2 = c.post(
            f"/api/comments/{comment_id}/edit/",
            data=json.dumps({"text": "Edited"}),
            content_type="application/json",
        )
        self.assertEqual(resp2.json()["comment"]["text"], "Edited")

    def test_cannot_edit_others_comment(self):
        c_bob = self._login(self.bob)
        resp = c_bob.post(
            f"/api/posts/{self.post.id}/comment/",
            data=json.dumps({"text": "Bob wrote this"}),
            content_type="application/json",
        )
        comment_id = resp.json()["comment"]["id"]

        c_alice = self._login(self.alice)
        resp2 = c_alice.post(
            f"/api/comments/{comment_id}/edit/",
            data=json.dumps({"text": "Alice hijacking"}),
            content_type="application/json",
        )
        self.assertEqual(resp2.status_code, 403)

    def test_delete_own_comment(self):
        c = self._login(self.bob)
        resp = c.post(
            f"/api/posts/{self.post.id}/comment/",
            data=json.dumps({"text": "To be deleted"}),
            content_type="application/json",
        )
        comment_id = resp.json()["comment"]["id"]
        resp2 = c.post(f"/api/comments/{comment_id}/delete/")
        self.assertTrue(resp2.json()["success"])
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())


class PostDeleteAPITests(_BaseTestCase):
    """Tests for POST /api/posts/<id>/delete/."""

    def test_delete_own_post(self):
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
            body="Delete me",
        )
        c = self._login(self.alice)
        resp = c.post(f"/api/posts/{post.id}/delete/")
        self.assertTrue(resp.json()["success"])
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_cannot_delete_others_post(self):
        post = Post.objects.create(
            author=self.alice,
            tree=self.tree,
            tree_name="red maple",
            body="Not yours",
        )
        c = self._login(self.bob)
        resp = c.post(f"/api/posts/{post.id}/delete/")
        self.assertEqual(resp.status_code, 403)


class TreeFollowAPITests(_BaseTestCase):
    """Tests for POST /api/trees/<tree_id>/follow/."""

    def test_follow_tree(self):
        c = self._login(self.alice)
        resp = c.post(f"/api/trees/{self.tree.tree_id}/follow/")
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["following"])
        self.assertEqual(data["follower_count"], 1)

    def test_unfollow_tree(self):
        """Following a tree twice should toggle it off."""
        c = self._login(self.alice)
        c.post(f"/api/trees/{self.tree.tree_id}/follow/")  # follow
        resp = c.post(f"/api/trees/{self.tree.tree_id}/follow/")  # unfollow
        data = resp.json()
        self.assertFalse(data["following"])
        self.assertEqual(data["follower_count"], 0)

    def test_follow_nonexistent_tree(self):
        c = self._login(self.alice)
        resp = c.post("/api/trees/999999/follow/")
        self.assertEqual(resp.status_code, 404)


class NotificationAPITests(_BaseTestCase):
    """Tests for notification endpoints."""

    def test_fetch_notifications(self):
        Notification.objects.create(
            recipient=self.alice,
            sender=self.bob,
            notif_type="like",
            message="Bob liked your post",
        )
        c = self._login(self.alice)
        resp = c.get("/api/notifications/")
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["notifications"]), 1)
        self.assertEqual(data["unread_count"], 1)

    def test_mark_all_read(self):
        Notification.objects.create(
            recipient=self.alice,
            sender=self.bob,
            notif_type="like",
            message="Test",
        )
        c = self._login(self.alice)
        c.post("/api/notifications/mark-all-read/")
        resp = c.get("/api/notifications/unread-count/")
        self.assertEqual(resp.json()["unread_count"], 0)

    def test_mark_specific_read(self):
        n = Notification.objects.create(
            recipient=self.alice,
            sender=self.bob,
            notif_type="comment",
            message="Test",
        )
        c = self._login(self.alice)
        c.post(
            "/api/notifications/mark-read/",
            data=json.dumps({"ids": [n.id]}),
            content_type="application/json",
        )
        n.refresh_from_db()
        self.assertTrue(n.is_read)


class MyFollowedTreesAPITests(_BaseTestCase):
    """Tests for GET /api/my-followed-trees/."""

    def test_returns_followed_trees(self):
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        c = self._login(self.alice)
        resp = c.get("/api/my-followed-trees/")
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["trees"]), 1)
        self.assertEqual(data["trees"][0]["tree_id"], 180683)

    def test_empty_when_not_following(self):
        c = self._login(self.alice)
        resp = c.get("/api/my-followed-trees/")
        self.assertEqual(len(resp.json()["trees"]), 0)

    def test_unauthenticated_rejected(self):
        c = Client()
        resp = c.get("/api/my-followed-trees/")
        self.assertEqual(resp.status_code, 401)
