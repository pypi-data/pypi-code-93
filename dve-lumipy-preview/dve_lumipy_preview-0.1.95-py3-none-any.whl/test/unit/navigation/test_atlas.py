import unittest

from lumipy.navigation.atlas import Atlas
from test.test_utils import make_test_atlas, assert_locked_lockable


class TestAtlas(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()

    def test_atlas_construction(self):

        # Given an atlas constructed from field table catalog and entitlement resources
        # When you try to add a new attribute then it should throw
        assert_locked_lockable(self, self.atlas)

        # The number of provider descriptions on the atlas should be the expected
        providers = self.atlas.list_providers()
        self.assertEqual(len(providers), 123)

        # Given the saved AppRequest provider info
        app_req = self.atlas.lusid_logs_apprequest
        # Should have the right number of columns
        cols = app_req.list_columns()
        self.assertEqual(len(cols), 30)
        # Should have the right number of params
        params = app_req.list_parameters()
        self.assertEqual(len(params), 5)
        # Should have the right number of fields overall (cols + params)
        self.assertEqual(len(app_req.list_fields()), 35)

        for prov_description in self.atlas.list_providers():
            # Check all providers have attached column descriptions
            self.assertTrue(
                len(prov_description.list_columns()) > 0,
                msg=f"Provider description {prov_description.get_name()} has no columns"
            )

            # Check attributes
            for field_description in prov_description.list_fields():
                self.assertEqual(field_description.table_name, prov_description._table_name)
                self.assertNotEqual(field_description.field_name, '')
                self.assertNotEqual(field_description.field_name, None)
                self.assertTrue(hasattr(prov_description, field_description.get_name()), msg=f'Field {field_description.get_name()} is missing')

    def test_atlas_search(self):

        result = self.atlas.search_providers('aws')

        self.assertEqual(type(result), Atlas)
        self.assertEqual(len(result.list_providers()), 12)
        for p_description in result.list_providers():
            self.assertTrue(
                'aws' in p_description.get_name()
                or 'aws' in p_description.get_table_name().lower()
                or 'aws' in p_description.get_description().lower()
                or any('aws' in f.get_name() for f in p_description.list_fields())
            )
