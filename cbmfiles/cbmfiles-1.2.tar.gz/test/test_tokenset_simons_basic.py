import unittest

from cbm_files.tokenset_simons_basic import TokenSet_Simons_BASIC


class TestBasicV2(unittest.TestCase):
    def test_tokenize(self):
        tokenset = TokenSet_Simons_BASIC()
        self.assertEqual(tokenset.tokenize('SYS', 'ascii'), b'\x9e')
        self.assertEqual(tokenset.tokenize('COPY', 'ascii'), b'\x64\x77')
        self.assertEqual(tokenset.tokenize('LOW COL', 'ascii'), b'\x64\x76')

    def test_expand(self):
        tokenset = TokenSet_Simons_BASIC()
        self.assertEqual(tokenset.expand(b'\x9e', 'ascii'), 'SYS')
        self.assertEqual(tokenset.expand(b'\x64\x19', 'ascii'), 'MULTI')
