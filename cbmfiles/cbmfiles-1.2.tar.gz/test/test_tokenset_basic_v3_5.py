import unittest

from cbm_files.tokenset_basic_v3_5 import TokenSet_BASICv3_5


class TestBasicV3_5(unittest.TestCase):
    def test_tokenize(self):
        tokenset = TokenSet_BASICv3_5()
        self.assertEqual(tokenset.tokenize('SYS', 'ascii'), b'\x9e')
        self.assertEqual(tokenset.tokenize('DIRECTORY', 'ascii'), b'\xee')

    def test_expand(self):
        tokenset = TokenSet_BASICv3_5()
        self.assertEqual(tokenset.expand(b'\x9e', 'ascii'), 'SYS')
        self.assertEqual(tokenset.expand(b'\xee', 'ascii'), 'DIRECTORY')
