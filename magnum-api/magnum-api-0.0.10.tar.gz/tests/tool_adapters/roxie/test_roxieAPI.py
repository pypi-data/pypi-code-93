import unittest

import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI

class MyTestCase(unittest.TestCase):
    def test_find_index_start_and_length_bottom_header_table(self):
        # arrange
        keyword = 'CABLE'

        # act
        # assert
        with self.assertRaises(Exception) as context:
            RoxieAPI.find_index_start_and_length_bottom_header_table('', keyword)

        self.assertTrue('Not found start index and length for keyword CABLE' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
