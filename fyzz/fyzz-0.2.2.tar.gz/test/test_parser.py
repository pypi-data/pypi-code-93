from logilab.common.testlib import TestCase, unittest_main

from fyzz.yappsparser import parse, FyzzParserPrefixError


class FyzzTester(TestCase):
    def test_prefix_error(self):
        req = (
            "PREFIX doap: <http://usefulinc.com/ns/doap#> "
            "SELECT ?project "
            "WHERE  { ?project a doa:Project }"
        )
        with self.assertRaises(FyzzParserPrefixError) as cm:
            parse(req)
        self.assertEqual(cm.exception.ns, "doa")
        self.assertEqual(cm.exception.valid_prefixes, ["doap"])


if __name__ == "__main__":
    unittest_main()
