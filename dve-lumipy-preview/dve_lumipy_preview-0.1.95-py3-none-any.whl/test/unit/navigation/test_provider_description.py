import unittest

from lumipy.common.string_utils import handle_available_string
from lumipy.navigation.field_metadata import FieldMetadata
from lumipy.navigation.provider_metadata import ProviderMetadata
from test.test_utils import get_atlas_test_data


class TestProviderDescription(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas_df = get_atlas_test_data()

    def test_provider_description_construction(self):

        for _, p_df in self.atlas_df.groupby('Name'):

            fields = [FieldMetadata.from_row(row) for _, row in p_df.iterrows()]

            p_row = p_df.iloc[0]
            provider = ProviderMetadata(
                table_name=p_row.Name,
                description=p_row.Description,
                provider_type=p_row.Type,
                category=p_row.Category,
                last_ping_at=p_row.LastPingAt,
                documentation=p_row.DocumentationLink,
                fields=fields,
                client="dummy client value"
            )

            self.assertEqual(len(provider.list_fields()), len(fields))
            self.assertEqual(len(provider.list_columns()), len([f for f in fields if f.field_type == 'Column']))
            self.assertEqual(len(provider.list_parameters()), len([f for f in fields if f.field_type == 'Parameter']))

            self.assertEqual(provider.get_name(), p_row.Name.replace('.', '_').lower())
            self.assertEqual(provider._client, "dummy client value")
            self.assertEqual(provider.get_table_name(), p_row.Name)
            self.assertEqual(provider._description, handle_available_string(p_row.Description))
            self.assertEqual(provider._provider_type, p_row.Type)
            self.assertEqual(provider._category, p_row.Category)
            self.assertEqual(provider._last_ping_at, p_row.LastPingAt)
            self.assertEqual(provider._documentation, handle_available_string(p_row.DocumentationLink))

            provider_str = str(provider)
            for field in fields:
                self.assertIn(field.get_name(), provider_str)
                self.assertTrue(hasattr(provider, field.get_name()))
