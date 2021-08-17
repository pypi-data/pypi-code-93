import unittest

from cbm_files.tokenset_basic_v4 import TokenSet_BASICv4


class TestBasicV4(unittest.TestCase):
    def test_tokenize(self):
        tokenset = TokenSet_BASICv4()
        self.assertEqual(tokenset.tokenize('SYS', 'ascii'), b'\x9e')
        self.assertEqual(tokenset.tokenize('DIRECTORY', 'ascii'), b'\xda')

    def test_expand(self):
        tokenset = TokenSet_BASICv4()
        self.assertEqual(tokenset.expand(b'\x9e', 'ascii'), 'SYS')
        self.assertEqual(tokenset.expand(b'\xda', 'ascii'), 'DIRECTORY')
