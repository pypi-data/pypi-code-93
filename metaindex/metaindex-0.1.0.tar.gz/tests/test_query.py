import unittest

from metaindex.query import tokenize, Query


class TestTokenizer(unittest.TestCase):
    def test_simple_words(self):
        text = '\\(there\\) once "was a"  \\"lady (in riga )'
        expected = ['(there)', 'once', 'was a', '\"lady', '(in', 'riga', ')']
        self.assertEqual(expected, tokenize(text))


class TestQueryParser(unittest.TestCase):
    def test_simple(self):
        text = "look, albatross"
        query = Query.parse(text)

        self.assertEqual(2, len(query.root.terms))

    def test_keyvalue(self):
        text = "title:albatross"
        query = Query.parse(text)

        self.assertEqual(query.root.terms[0].key, "title")
        self.assertEqual(query.root.terms[0].regex, "albatross")

