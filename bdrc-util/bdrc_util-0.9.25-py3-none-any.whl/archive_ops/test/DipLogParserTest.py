"""
Test the permutations of the sour
"""
import unittest

from archive_ops.DipLog import DipLogParser


class DipLogParserTest(unittest.TestCase):
    """
    Test parsing of DipLog arguments
    """
    def TestWhenAllRequiredGivenThenNameSpaceFilled(self):
        dlp = DipLogParser()
        test_ns = dlp.parse_args()
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
