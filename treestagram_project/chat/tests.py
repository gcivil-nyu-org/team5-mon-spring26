"""
Tests for the Chat app.

Covers: ChatMessage model, message ordering, cascade deletes,
        and the /api/my-followed-trees/ chat-status integration.

Run with:
    python manage.py test chat -v2
"""

from django.test import TestCase, Client
from accounts.models import User
from trees.models import Tree
from chat.models import ChatMessage
from posts.models import TreeFollow


# ─── Shared Helpers ─────────────────────────────────────────────────────────


class _BaseTestCase(TestCase):
    """Shared fixtures for every test class in this module."""

    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice",
            password="pass1234",
            email="alice@test.com",
        )
        cls.bob = User.objects.create_user(
            username="bob",
            password="pass1234",
            email="bob@test.com",
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
        c = Client()
        c.login(username=user.username, password="pass1234")
        return c


# ═══════════════════════════════════════════════════════════════════════════
#  MODEL LAYER TESTS
# ═══════════════════════════════════════════════════════════════════════════


class ChatMessageModelTests(_BaseTestCase):
    """Unit tests for the ChatMessage model."""

    def test_create_message(self):
        """A chat message can be created with required fields."""
        msg = ChatMessage.objects.create(
            tree=self.tree,
            user=self.alice,
            content="Hello tree!",
        )
        self.assertEqual(msg.content, "Hello tree!")
        self.assertEqual(msg.user.username, "alice")
        self.assertEqual(msg.tree.tree_id, 180683)

    def test_str_representation(self):
        msg = ChatMessage.objects.create(
            tree=self.tree,
            user=self.alice,
            content="Short msg",
        )
        self.assertIn("red maple", str(msg))
        self.assertIn("alice", str(msg))

    def test_ordering_oldest_first(self):
        """Messages are ordered by timestamp ascending (oldest first)."""
        m1 = ChatMessage.objects.create(
            tree=self.tree,
            user=self.alice,
            content="First",
        )
        m2 = ChatMessage.objects.create(
            tree=self.tree,
            user=self.bob,
            content="Second",
        )
        messages = list(ChatMessage.objects.all())
        self.assertEqual(messages[0].id, m1.id)
        self.assertEqual(messages[1].id, m2.id)

    def test_db_table_name(self):
        """The model should use the legacy table name 'posts_chatmessage'."""
        self.assertEqual(ChatMessage._meta.db_table, "posts_chatmessage")

    def test_auto_timestamp(self):
        """Timestamp is automatically set on creation."""
        msg = ChatMessage.objects.create(
            tree=self.tree,
            user=self.alice,
            content="Timestamp test",
        )
        self.assertIsNotNone(msg.timestamp)

    def test_long_message(self):
        """Messages can contain long text (TextField)."""
        long_text = "x" * 5000
        msg = ChatMessage.objects.create(
            tree=self.tree,
            user=self.alice,
            content=long_text,
        )
        msg.refresh_from_db()
        self.assertEqual(len(msg.content), 5000)


# ═══════════════════════════════════════════════════════════════════════════
#  CASCADE / RELATIONSHIP TESTS
# ═══════════════════════════════════════════════════════════════════════════


class ChatMessageCascadeTests(TestCase):
    """Tests that messages are properly cleaned up when parent objects are deleted."""

    def test_delete_tree_cascades_messages(self):
        """Deleting a tree should delete all its chat messages."""
        user = User.objects.create_user(username="temp", password="pass1234")
        tree = Tree.objects.create(
            tree_id=999001,
            created_at="2020-01-01",
            tree_dbh=10,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            spc_latin="Test",
            spc_common="test tree",
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
            address="1 TEST ST",
            zip_city="NY",
            borough="Manhattan",
            latitude=40.0,
            longitude=-74.0,
        )
        ChatMessage.objects.create(tree=tree, user=user, content="Goodbye")
        self.assertEqual(ChatMessage.objects.filter(tree=tree).count(), 1)

        tree.delete()
        self.assertEqual(ChatMessage.objects.filter(tree__tree_id=999001).count(), 0)

    def test_delete_user_cascades_messages(self):
        """Deleting a user should delete all their chat messages."""
        user = User.objects.create_user(username="temp2", password="pass1234")
        tree = Tree.objects.create(
            tree_id=999002,
            created_at="2020-01-01",
            tree_dbh=10,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            spc_latin="Test",
            spc_common="test tree",
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
            address="2 TEST ST",
            zip_city="NY",
            borough="Manhattan",
            latitude=40.0,
            longitude=-74.0,
        )
        ChatMessage.objects.create(tree=tree, user=user, content="Goodbye user")
        user.delete()
        self.assertEqual(ChatMessage.objects.filter(user__username="temp2").count(), 0)


# ═══════════════════════════════════════════════════════════════════════════
#  CHAT STATUS INTEGRATION TESTS (via /api/my-followed-trees/)
# ═══════════════════════════════════════════════════════════════════════════


class ChatStatusIntegrationTests(_BaseTestCase):
    """
    Tests the chat-status fields (has_messages, last_message, last_message_time)
    returned by the /api/my-followed-trees/ endpoint.
    """

    def test_followed_tree_with_no_messages(self):
        """A followed tree with no chat messages should show has_messages=False."""
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        c = self._login(self.alice)
        resp = c.get("/api/my-followed-trees/")
        tree_data = resp.json()["trees"][0]
        self.assertFalse(tree_data["has_messages"])
        self.assertIsNone(tree_data["last_message"])
        self.assertIsNone(tree_data["last_message_time"])

    def test_followed_tree_with_messages(self):
        """A followed tree with chat activity should show has_messages=True."""
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        ChatMessage.objects.create(
            tree=self.tree,
            user=self.bob,
            content="Hey everyone!",
        )
        c = self._login(self.alice)
        resp = c.get("/api/my-followed-trees/")
        tree_data = resp.json()["trees"][0]
        self.assertTrue(tree_data["has_messages"])
        self.assertEqual(tree_data["last_message"], "Hey everyone!")
        self.assertIsNotNone(tree_data["last_message_time"])

    def test_last_message_is_most_recent(self):
        """last_message should reflect the newest message in the chat."""
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        ChatMessage.objects.create(tree=self.tree, user=self.bob, content="Old message")
        ChatMessage.objects.create(
            tree=self.tree, user=self.alice, content="New message"
        )

        c = self._login(self.alice)
        resp = c.get("/api/my-followed-trees/")
        tree_data = resp.json()["trees"][0]
        self.assertEqual(tree_data["last_message"], "New message")

    def test_unfollowed_trees_not_included(self):
        """Trees the user doesn't follow should not appear in the response."""
        c = self._login(self.alice)
        resp = c.get("/api/my-followed-trees/")
        self.assertEqual(len(resp.json()["trees"]), 0)


# ═══════════════════════════════════════════════════════════════════════════
#  MULTIPLE TREE CHAT ISOLATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class ChatIsolationTests(_BaseTestCase):
    """Tests that messages are properly isolated between different tree chats."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tree2 = Tree.objects.create(
            tree_id=999003,
            created_at="2018-06-01",
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
            address="789 OAK BLVD",
            zip_city="New York",
            borough="Brooklyn",
            latitude=40.678,
            longitude=-73.944,
        )

    def test_messages_isolated_per_tree(self):
        """Messages sent to one tree's chat should not appear in another's."""
        ChatMessage.objects.create(tree=self.tree, user=self.alice, content="For maple")
        ChatMessage.objects.create(tree=self.tree2, user=self.alice, content="For oak")

        maple_msgs = ChatMessage.objects.filter(tree=self.tree)
        oak_msgs = ChatMessage.objects.filter(tree=self.tree2)

        self.assertEqual(maple_msgs.count(), 1)
        self.assertEqual(oak_msgs.count(), 1)
        self.assertEqual(maple_msgs.first().content, "For maple")
        self.assertEqual(oak_msgs.first().content, "For oak")

    def test_message_count_per_tree(self):
        """Each tree should independently track its message count."""
        for i in range(5):
            ChatMessage.objects.create(
                tree=self.tree, user=self.alice, content=f"Maple #{i}"
            )
        for i in range(3):
            ChatMessage.objects.create(
                tree=self.tree2, user=self.bob, content=f"Oak #{i}"
            )

        self.assertEqual(ChatMessage.objects.filter(tree=self.tree).count(), 5)
        self.assertEqual(ChatMessage.objects.filter(tree=self.tree2).count(), 3)
