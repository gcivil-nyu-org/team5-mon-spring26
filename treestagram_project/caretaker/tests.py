import json
from django.test import TestCase, Client
from accounts.models import User
from trees.models import Tree
from posts.models import TreeFollow
from caretaker.models import CaretakerApplication, CaretakerAssignment

class _BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice",
            password="pass1234",
            email="alice@test.com",
            role="user"
        )
        cls.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            email="admin@test.com",
            role="admin"
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

class CaretakerModelTests(_BaseTestCase):
    def test_create_application(self):
        app = CaretakerApplication.objects.create(
            user=self.alice,
            tree_id=str(self.tree.tree_id),
            motivation="I love trees",
        )
        self.assertEqual(app.status, "pending")
        self.assertEqual(app.user.username, "alice")
        self.assertTrue(str(app).startswith(f"alice - {app.tree_id}"))

    def test_create_assignment(self):
        assignment = CaretakerAssignment.objects.create(
            user=self.alice,
            tree_id=str(self.tree.tree_id)
        )
        self.assertEqual(assignment.user.username, "alice")
        self.assertTrue("taking care of" in str(assignment))

class CaretakerAPITests(_BaseTestCase):
    def test_apply_requires_authentication(self):
        c = Client()
        resp = c.post("/api/apply-for-caretaker/")
        self.assertEqual(resp.status_code, 401)

    def test_apply_requires_following(self):
        c = self._login(self.alice)
        resp = c.post(
            "/api/apply-for-caretaker/",
            data=json.dumps({"tree_id": str(self.tree.tree_id), "motivation": "Because"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn("must follow the tree", resp.json()["error"])

    def test_apply_success(self):
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        c = self._login(self.alice)
        resp = c.post(
            "/api/apply-for-caretaker/",
            data=json.dumps({"tree_id": str(self.tree.tree_id), "motivation": "Because I care"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(CaretakerApplication.objects.filter(user=self.alice, tree_id=str(self.tree.tree_id)).exists())

    def test_prevent_duplicate_application(self):
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        CaretakerApplication.objects.create(user=self.alice, tree_id=str(self.tree.tree_id), motivation="test")
        c = self._login(self.alice)
        resp = c.post(
            "/api/apply-for-caretaker/",
            data=json.dumps({"tree_id": str(self.tree.tree_id), "motivation": "reapply"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("already have a pending", resp.json()["error"])

    def test_prevent_apply_if_already_caretaker(self):
        TreeFollow.objects.create(user=self.alice, tree=self.tree)
        CaretakerAssignment.objects.create(user=self.alice, tree_id=str(self.tree.tree_id))
        c = self._login(self.alice)
        resp = c.post(
            "/api/apply-for-caretaker/",
            data=json.dumps({"tree_id": str(self.tree.tree_id), "motivation": "reapply"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("already a caretaker", resp.json()["error"])

    def test_get_pending_applications(self):
        CaretakerApplication.objects.create(user=self.alice, tree_id=str(self.tree.tree_id), motivation="pending test")
        c = self._login(self.admin)
        resp = c.get("/api/pending-applications/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["applications"]), 1)
        self.assertEqual(data["applications"][0]["motivation"], "pending test")

    def test_review_application_approve(self):
        app = CaretakerApplication.objects.create(user=self.alice, tree_id=str(self.tree.tree_id), motivation="review test")
        c = self._login(self.admin)
        resp = c.post(
            "/api/review-application/",
            data=json.dumps({"application_id": app.id, "action": "approved"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, "approved")
        self.assertEqual(app.reviewed_by, self.admin)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.role, "caretaker")
        self.assertTrue(CaretakerAssignment.objects.filter(user=self.alice, tree_id=str(self.tree.tree_id)).exists())

    def test_review_application_reject(self):
        app = CaretakerApplication.objects.create(user=self.alice, tree_id=str(self.tree.tree_id), motivation="review test 2")
        c = self._login(self.admin)
        resp = c.post(
            "/api/review-application/",
            data=json.dumps({"application_id": app.id, "action": "rejected"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, "rejected")
        self.assertFalse(CaretakerAssignment.objects.filter(user=self.alice, tree_id=str(self.tree.tree_id)).exists())

    def test_check_tree(self):
        c = Client()
        resp = c.get(f"/api/check-tree/?tree_id={self.tree.tree_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["exists"])

        resp = c.get("/api/check-tree/?tree_id=999999")
        self.assertFalse(resp.json()["exists"])
