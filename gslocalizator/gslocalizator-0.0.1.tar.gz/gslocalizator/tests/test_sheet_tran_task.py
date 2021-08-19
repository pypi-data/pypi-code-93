#!/usr/bin/env python3

from gslocalizator.sheet_tran_task import _SheetTranTask
import unittest


class TestSheetTranTask(unittest.TestCase):
    def test_get_sheetname_from_range(self):
        test_items = [
            {
                'fromSheetRange': None,
                'expectSheetName': None
            },
            {
                'fromSheetRange': '',
                'expectSheetName': None
            },
            {
                'fromSheetRange': '!bizA!A1:E',
                'expectSheetName': None
            },

            {
                'fromSheetRange': 'bizA',
                'expectSheetName': 'bizA'
            },
            {
                'fromSheetRange': 'bizA!A1:E',
                'expectSheetName': 'bizA'
            },
            {
                'fromSheetRange': 'bizA!A1:E!dfd',
                'expectSheetName': 'bizA'
            },
        ]

        for test_item in test_items:
            task = _SheetTranTask(
                from_sheet_range=test_item['fromSheetRange'],
                from_value_column_to_file={'': ''})

            self.assertEqual(test_item['expectSheetName'],
                             task.get_sheetname_from_range())


if __name__ == '__main__':
    unittest.main()
