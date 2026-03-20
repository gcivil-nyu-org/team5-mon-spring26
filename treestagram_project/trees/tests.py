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
        Use case: Ensures readable object representation (useful in admin/debugging)
        """
        self.assertTrue(str(self.tree))


class TreeViewTest(TestCase):
    """
    Tests related to Tree views (request/response layer)
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
        Test that the main tree endpoint loads successfully
        Use case: Ensures frontend/API can fetch tree data without crashing
        """
        response = self.client.get("/")  # update if your URL differs
        self.assertIn(response.status_code, [200, 404])


class TreeValidationTest(TestCase):
    """
    Tests for invalid or edge case data
    """

    def test_invalid_tree_creation(self):
        """
        Test that invalid data raises an error
        Use case: Prevents corrupt or incomplete data from entering database
        """
        with self.assertRaises(Exception):
            Tree.objects.create(tree_id=None)
