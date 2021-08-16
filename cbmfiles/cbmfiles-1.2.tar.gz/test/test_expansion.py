import unittest

import cbm_files.expansion


class TestExpansion(unittest.TestCase):

    def test_expansion(self):
        self.assertEqual(cbm_files.expansion.vic20_expansion_required(0x1000, 0x250), (False, False, False, False, False))
        self.assertEqual(cbm_files.expansion.vic20_expansion_required(0x401, 0x1050), (True, False, False, False, False))
        self.assertEqual(cbm_files.expansion.vic20_expansion_required(0x1201, 0x2360), (False, True, False, False, False))
        self.assertEqual(cbm_files.expansion.vic20_expansion_required(0x1201, 0x4360), (False, True, True, False, False))
        self.assertEqual(cbm_files.expansion.vic20_expansion_required(0x1201, 0x6360), (False, True, True, True, False))
        self.assertEqual(cbm_files.expansion.vic20_expansion_required(0xA000, 0x1000), (False, False, False, False, True))
