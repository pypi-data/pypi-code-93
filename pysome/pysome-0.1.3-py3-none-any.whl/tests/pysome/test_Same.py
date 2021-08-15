import unittest

from pysome import expect, Same, SomeDict, Some, SameOutsideExpect, NotSame, SomeList, AllOf


class SameTest(unittest.TestCase):
    def test_basics(self):
        expect("abcs").to_be(Same())

        expect({
            "a": 12,
            "b": 12,
            "c": 14
        }).to_be({
            "a": Same(),
            "b": Same(),
            "c": 14
        }).to_be(
            SomeDict()
        ).not_to_be({
            "a": Some(int),
            "b": Some(str),
            "c": Some(int)
        }).not_to_be({
            "a": Same(),
            "b": Some(int),
            "c": Same()
        })

        expect({
            "a": 12,
            "b": 12
        }).not_to_be({
            "a": Same(str),
            "b": Same(str)
        })

        expect({
            "a": 12,
            "b": 13
        }).not_to_be({
            "a": Same(),
            "b": Same()
        }).to_be({
            "a": Same(name="s1"),
            "b": Same(name="s2")
        })

        s = Same()
        with self.assertRaises(SameOutsideExpect):
            assert s == 3
        with self.assertRaises(SameOutsideExpect):
            assert 3 == s

    def test_with_types(self):
        expect([12, 12]).to_be([Same(int), Same(int)])
        expect([12, 12.0]).not_to_be([Same(int), Same(int)])
        expect([12, 12.0]).to_be([Same(), Same()])

        expect(["abc", "dfg"]).to_be([Same(str), Some(str)])
        expect(["abc", "dfg"]).not_to_be([Same(str), Same(str)])
        expect(["abc", "dfg"]).to_be([Same(str), "dfg"])

        expect("abc").to_be(Same(int, str))
        expect("abc").not_to_be(Same(int, float))

    def test_with_func(self):
        def sum_to_5(x):
            return sum(x) == 5

        def sum_to_6(x):
            return sum(x) == 6

        expect({
            "a": [1, 4],
            "b": [1, 2, 2],
            "c": [1, 4]
        }).not_to_be({
            "a": Same(sum_to_5),
            "b": Same(sum_to_5),
            "c": SomeList(),
        }).to_be({
            "a": Same(sum_to_5, name="other name"),
            "b": Same(sum_to_5),
            "c": SomeList()
        }).to_be({
            "a": Same(sum_to_5),
            "b": SomeList(),
            "c": Same(sum_to_5),
        }).not_to_be({
            "a": Same(sum_to_6),
            "b": SomeList(),
            "c": Same(sum_to_6),
        })


class NotSameTest(unittest.TestCase):
    def test_basics(self):
        expect(12).to_be(NotSame())
        expect([1, 14, 1]).to_be([NotSame(), NotSame(), 1])
        expect([1, 14, 1]).to_be([NotSame(), 14, 1])
        expect([1, 14, 1]).not_to_be([NotSame(), 14, NotSame()])
        expect([1, 14, 1.0]).not_to_be([NotSame(), 14, NotSame()])
        expect([1, 14, 1.01]).to_be([NotSame(), 14, NotSame()])

        expect([1, 14, 1]).to_be([NotSame(name="other name"), 14, NotSame()])
        expect([1, 14, 1]).not_to_be([NotSame(name="other name"), 14, NotSame(name="other name")])
        expect([1, 14, 1]).to_be([NotSame(name="other name"), 14, NotSame(name="other name ")])

        ns = NotSame()

        with self.assertRaises(SameOutsideExpect):
            _ = ns == 1

    def test_with_some(self):
        # todo:
        pass

    def test_with_same(self):
        expect({
            "a": 12,
            "b": 14,
            "c": 12,
            "d": 12,
        }).to_be({
            "a": NotSame(),
            "b": NotSame(),
            "c": Same(),
            "d": Same(),
        })

        expect({
            "a": 12,
            "b": 14,
            "c": 12,
            "d": 14,
        }).not_to_be({
            "a": NotSame(),
            "b": NotSame(),
            "c": Same(),
            "d": Same(),
        })

        expect({
            "a": 12,
            "b": 14,
            "c": 12,
            "d": 12,
        }).not_to_be({
            "a": NotSame(),
            "b": Same(),
            "c": NotSame(),
            "d": Same(),
        })

    def test_multiple(self):
        def sum_to_5(x):
            return sum(x) == 5

        def includes_1(x):
            return 1 in x

        expect({
            "a": [1, 4],
            "b": (1, 4)
        }).to_be({
            "a": NotSame(sum_to_5),
            "b": NotSame(sum_to_5),
        }).to_be({
            "a": NotSame(sum_to_5),
            "b": NotSame(includes_1),
        })

        expect({
            "a": [1, 4],
            "b": [1, 4]
        }).to_be({
            "a": Same(sum_to_5),
            "b": Same(sum_to_5)
        }).not_to_be({
            "a": NotSame(sum_to_5),
            "b": NotSame(sum_to_5)
        })

        expect({
            "a": 5,
            "b": 5,
            "c": 6,
            "d": 7,
        }).to_be({
            "a": Same(name="n1"),
            "b": AllOf(Same(name="n1"), NotSame()),
            "c": NotSame(),
            "d": NotSame(),
        })

        expect({
            "a": 5,
            "b": 6,
            "c": 6,
            "d": 7,
        }).not_to_be({
            "a": Same(name="n1"),
            "b": AllOf(Same(name="n1"), NotSame()),
            "c": NotSame(),
            "d": NotSame(),
        })

        expect({
            "a": 5,
            "b": 5,
            "c": 5,
            "d": 7,
        }).not_to_be({
            "a": Same(name="n1"),
            "b": AllOf(Same(name="n1"), NotSame()),
            "c": NotSame(),
            "d": NotSame(),
        })
