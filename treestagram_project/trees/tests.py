from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from trees.models import Tree

User = get_user_model()


# ---------------- EXISTING USER TESTS (UNCHANGED) ---------------- #


class UserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_create_user(self):
        self.assertEqual(self.user.username, "testuser")

    def test_login(self):
        login = self.client.login(username="testuser", password="testpass123")
        self.assertTrue(login)


class AccountViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])

    def test_invalid_page(self):
        response = self.client.get("/random-url/")
        self.assertIn(response.status_code, [200, 404])


# ---------------- TREE MODEL TESTS (UNCHANGED) ---------------- #


class TreeModelTest(TestCase):
    def setUp(self):
        self.tree = Tree.objects.create(
            tree_id=1,
            created_at="2020-01-01",
            tree_dbh=10,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            spc_latin="Acer",
            spc_common="Maple",
            sidewalk="NoDamage",
            problems="None",
            root_stone=False,
            root_grate=False,
            root_other=False,
            trunk_wire=False,
            trnk_light=False,
            trnk_other=False,
            brch_light=False,
            brch_shoe=False,
            brch_other=False,
            address="123 Street",
            zip_city="10001",
            borough="Manhattan",
            latitude=40.0,
            longitude=-73.0,
        )

    def test_tree_creation(self):
        self.assertEqual(self.tree.tree_id, 1)

    def test_tree_str(self):
        self.assertTrue(str(self.tree))


class TreeValidationTest(TestCase):
    def test_invalid_tree_creation(self):
        with self.assertRaises(Exception):
            Tree.objects.create(tree_id=None)


# ---------------- NEW: HIGH COVERAGE FOR views.py ---------------- #


class TreeViewsTest(TestCase):
    def setUp(self):
        self.tree = Tree.objects.create(
            tree_id=1,
            created_at="2020-01-01",
            tree_dbh=10,
            stump_diam=0,
            curb_loc="OnCurb",
            status="Alive",
            health="Good",
            spc_latin="Acer",
            spc_common="Maple",
            sidewalk="NoDamage",
            problems="None",
            root_stone=False,
            root_grate=False,
            root_other=False,
            trunk_wire=False,
            trnk_light=False,
            trnk_other=False,
            brch_light=False,
            brch_shoe=False,
            brch_other=False,
            address="123 Street",
            zip_city="10001",
            borough="Manhattan",
            latitude=40.0,
            longitude=-73.0,
        )

    # -------- tree_map_view -------- #
    def test_tree_map_view(self):
        response = self.client.get(reverse("tree_map"))
        self.assertEqual(response.status_code, 200)

    # -------- trees_api -------- #
    def test_trees_api_default(self):
        response = self.client.get(reverse("trees_api"))
        self.assertEqual(response.status_code, 200)

    def test_trees_api_with_limit(self):
        response = self.client.get(reverse("trees_api") + "?limit=5")
        self.assertEqual(response.status_code, 200)

    def test_trees_api_invalid_limit(self):
        response = self.client.get(reverse("trees_api") + "?limit=abc")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_trees_api_with_offset(self):
        response1 = self.client.get(reverse("trees_api") + "?limit=1&offset=0")
        response2 = self.client.get(reverse("trees_api") + "?limit=1&offset=1")
        self.assertNotEqual(response1.json(), response2.json())

    # -------- tree_detail_api -------- #
    def test_tree_detail_success(self):
        response = self.client.get(reverse("tree_detail_api", args=[self.tree.tree_id]))
        self.assertEqual(response.status_code, 200)

    def test_tree_detail_not_found(self):
        response = self.client.get(reverse("tree_detail_api", args=[999]))
        self.assertEqual(response.status_code, 404)

    # -------- search_trees_api -------- #
    def test_search_no_filters(self):
        response = self.client.get(reverse("search_trees_api"))
        self.assertEqual(response.status_code, 200)

    def test_search_tree_id_valid(self):
        response = self.client.get(reverse("search_trees_api") + "?tree_id=1")
        self.assertEqual(response.status_code, 200)

    def test_search_tree_id_invalid(self):
        response = self.client.get(reverse("search_trees_api") + "?tree_id=abc")
        self.assertEqual(response.status_code, 200)

    def test_search_species(self):
        response = self.client.get(reverse("search_trees_api") + "?spc_common=Maple")
        self.assertEqual(response.status_code, 200)

    def test_search_multiple_filters(self):
        response = self.client.get(
            reverse("search_trees_api") + "?spc_common=Maple&borough=Manhattan"
        )
        self.assertEqual(response.status_code, 200)

    def test_search_pagination(self):
        response = self.client.get(reverse("search_trees_api") + "?offset=0&limit=5")
        self.assertEqual(response.status_code, 200)

    # -------- stability / edge -------- #
    def test_empty_db(self):
        Tree.objects.all().delete()
        response = self.client.get(reverse("trees_api"))
        self.assertEqual(response.status_code, 200)

    def test_multiple_requests(self):
        for _ in range(5):
            response = self.client.get(reverse("trees_api"))
            self.assertEqual(response.status_code, 200)

    def test_json_header(self):
        response = self.client.get(reverse("trees_api"), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)


# ---------------- Testing Tree Update ---------------- #
class TreeUpdateApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin", password="TestPass123!", email="admin@test.com"
        )
        self.admin.role = "admin"
        self.admin.save()
        self.regular = User.objects.create_user(
            username="regular", password="TestPass123!", email="reg@test.com"
        )
        self.tree = Tree.objects.create(
            tree_id=88888,
            spc_common="Test Maple",
            spc_latin="Acer testus",
            created_at="2015",
            tree_dbh=5,
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
            address="456 Test Ave",
            zip_city="TestCity",
            borough="Brooklyn",
            latitude=40.6,
            longitude=-73.9,
        )

    def test_admin_can_update_health(self):
        self.client.force_login(self.admin)
        res = self.client.post(
            f"/trees/api/{self.tree.tree_id}/update/",
            data={"health": "Poor"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.tree.refresh_from_db()
        self.assertEqual(self.tree.health, "Poor")

    def test_admin_can_update_boolean_fields(self):
        self.client.force_login(self.admin)
        res = self.client.post(
            f"/trees/api/{self.tree.tree_id}/update/",
            data={"root_stone": True},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.tree.refresh_from_db()
        self.assertTrue(self.tree.root_stone)

    def test_admin_can_update_problems(self):
        self.client.force_login(self.admin)
        res = self.client.post(
            f"/trees/api/{self.tree.tree_id}/update/",
            data={"problems": ["Stones", "WiresRope"]},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.tree.refresh_from_db()
        self.assertIn("Stones", self.tree.problems)

    def test_invalid_health_value_rejected(self):
        self.client.force_login(self.admin)
        res = self.client.post(
            f"/trees/api/{self.tree.tree_id}/update/",
            data={"health": "Excellent"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_non_admin_rejected(self):
        self.client.force_login(self.regular)
        res = self.client.post(
            f"/trees/api/{self.tree.tree_id}/update/",
            data={"health": "Poor"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)

    def test_unauthenticated_rejected(self):
        res = self.client.post(
            f"/trees/api/{self.tree.tree_id}/update/",
            data={"health": "Poor"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 403)

    def test_nonexistent_tree_returns_404(self):
        self.client.force_login(self.admin)
        res = self.client.post(
            "/trees/api/00000/update/",
            data={"health": "Poor"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 404)
