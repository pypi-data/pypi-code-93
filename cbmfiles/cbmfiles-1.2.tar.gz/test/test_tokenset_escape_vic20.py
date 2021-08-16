import unittest

from cbm_files.tokenset_escape_vic20 import TokenSet_EscapeVIC20


class TestEscapeVIC20(unittest.TestCase):
    def test_tokenize(self):
        tokenset = TokenSet_EscapeVIC20()
        self.assertEqual(tokenset.tokenize('{red}', 'ascii'), b'\x1c')
        self.assertEqual(tokenset.tokenize('{home}', 'ascii'), b'\x13')

    def test_expand(self):
        tokenset = TokenSet_EscapeVIC20()
        self.assertEqual(tokenset.expand(b'\x1c', 'ascii'), '{red}')
        self.assertEqual(tokenset.expand(b'\x13', 'ascii'), '{home}')
