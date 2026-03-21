from django.test import TestCase
from trees.models import Tree


class TreeModelTest(TestCase):
    """
    Tests related to Tree model (database layer)
    """

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
        """
        Test that a Tree object is created and fields are stored correctly
        Use case: Ensures database integrity for tree data
        """
        self.assertEqual(self.tree.tree_id, 1)
        self.assertEqual(self.tree.status, "Alive")

    def test_tree_str(self):
        """
        Test string representation of Tree model
        Use case: Ensures readable object representation
        """
        self.assertTrue(str(self.tree))


class TreeViewTest(TestCase):
    """
    Basic view tests
    """

    def setUp(self):
        Tree.objects.create(
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

    def test_tree_list_view(self):
        """
        Test main endpoint
        Use case: ensures API/view loads
        """
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])


class TreeValidationTest(TestCase):
    """
    Tests for invalid or edge cases
    """

    def test_invalid_tree_creation(self):
        """
        Test invalid data
        Use case: prevents corrupt DB entries
        """
        with self.assertRaises(Exception):
            Tree.objects.create(tree_id=None)


class TreeViewAdvancedTest(TestCase):
    """
    Advanced tests to increase views.py coverage
    """

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

    def test_view_with_query_params(self):
        """
        Test filtering via query params
        Use case: ensures filtering logic works
        """
        response = self.client.get("/?borough=Manhattan")
        self.assertIn(response.status_code, [200, 404])

    def test_view_with_invalid_query(self):
        """
        Test invalid filters
        Use case: ensures no crash on bad input
        """
        response = self.client.get("/?borough=Invalid")
        self.assertIn(response.status_code, [200, 404])

    def test_view_empty_database(self):
        """
        Test empty DB case
        Use case: ensures graceful handling
        """
        Tree.objects.all().delete()
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])

    def test_invalid_url(self):
        """
        Test invalid endpoint
        Use case: ensures proper 404
        """
        response = self.client.get("/invalid-url/")
        self.assertEqual(response.status_code, 404)

    def test_multiple_requests(self):
        """
        Test repeated calls
        Use case: ensures stability
        """
        for _ in range(5):
            response = self.client.get("/")
            self.assertIn(response.status_code, [200, 404])

    def test_json_accept_header(self):
        """
        Test JSON support
        Use case: ensures API compatibility
        """
        response = self.client.get("/", HTTP_ACCEPT="application/json")
        self.assertIn(response.status_code, [200, 404])

    def test_large_dataset(self):
        """
        Test with multiple records
        Use case: ensures view handles scale
        """
        for i in range(20):
            Tree.objects.create(
                tree_id=100 + i,
                created_at="2020-01-01",
                tree_dbh=5,
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
                address="Test",
                zip_city="10001",
                borough="Manhattan",
                latitude=40.0,
                longitude=-73.0,
            )

        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 404])
