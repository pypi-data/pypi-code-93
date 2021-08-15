import unittest

from pysome import *


class SomeTests(unittest.TestCase):
    def test_init(self):
        s1 = Some()
        self.assertEqual(s1.types, None)

        s2 = Some(int)
        self.assertEqual(s2.types, [int])

        s3 = Some(int, str)
        self.assertEqual(s3.types, [int, str])

        def func(_):
            return True

        s3 = Some(int, str, func)
        self.assertEqual(s3.types, [int, str, func])

        with self.assertRaises(InvalidArgument):
            _ = Some(int, "a")

        with self.assertRaises(InvalidFunction):
            def func(_, __):
                return True

            _ = Some(int, func)

        class Foo:
            pass

        s4 = Some(Foo)
        self.assertEqual(s4.types, [Foo])

        self.assertTrue(Some(int, str) == 1)
        self.assertTrue(Some(str, int) == 1)
        self.assertTrue(Some(str, int) == "ab")
        self.assertTrue(Some(int, str) == "ab")

    def test_some_func(self):
        def invalid_validator_func(arg):
            return "False"

        s1 = Some(invalid_validator_func)
        with self.assertRaises(MustReturnBool):
            _ = s1 == ""

        def is_png(file: str):
            if not isinstance(file, str):
                return False
            return file.endswith(".png")

        self.assertTrue(Some(is_png) == "image.png")
        self.assertTrue(Some(is_png) == "cat.png")
        self.assertTrue(Some(is_png) == "dog.png")
        self.assertFalse(Some(is_png) == 12)
        self.assertFalse(Some(is_png) == "image.jpg")
        self.assertTrue(Some(is_png, int) == "image.png")

    def test_correct_args(self):
        _ = Some(int, str, dict)
        _ = Some(int, Some())

        with self.assertRaises(InvalidArgument):
            _ = Some(1)

        with self.assertRaises(InvalidArgument):
            _ = Some(str, 2)

        with self.assertRaises(InvalidArgument):
            _ = Some(Some(str), "x")


class AllOfTests(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(AllOf(str) == "abc")
        self.assertTrue(AllOf(int) == 13)
        self.assertTrue(AllOf(str, int) != 13)
        self.assertTrue(AllOf(str, Some()) == "abc")
        self.assertTrue(AllOf(str, Some(int)) != "abc")

        self.assertTrue(AllOf(Iterable, list) == [1, 2, 3])
        self.assertTrue(AllOf(Iterable, tuple) != [1, 2, 3])

        def sum_is_5(x):
            return sum(x) == 5

        self.assertTrue(AllOf(tuple, sum_is_5) == (1, 2, 2))
        self.assertTrue(AllOf(tuple, sum_is_5, has_len(2)) != (1, 2, 2))
        self.assertTrue(AllOf(tuple, sum_is_5) != (1, 3, 3))
        self.assertTrue(AllOf(tuple, sum_is_5, has_len(2)) == (0, 5))


class SomeOrNoneTests(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeOrNone() == 3)
        self.assertTrue(SomeOrNone() == None)
        self.assertTrue(SomeOrNone(int) == None)
        self.assertTrue(SomeOrNone(int) != "ab")
        self.assertTrue(SomeOrNone(str) == "ab")


class SomeIterableTests(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeIterable() == [4, "a", 3])
        self.assertTrue(SomeIterable() == ())
        self.assertTrue(SomeIterable() != 14)
        self.assertTrue(SomeIterable() == "abc")

        self.assertTrue(SomeIterable(int, str) == [4, "a", 3, 0])
        self.assertTrue(SomeIterable(int, str) != [4, "a", None, 0])

        def a_is_1(x):
            if not hasattr(x, "__contains__"):
                return False
            if "a" not in x:
                return False
            return x["a"] == 1

        self.assertTrue(SomeIterable(a_is_1) == [{"a": 1}, {"b": 12, "a": 1}])
        self.assertTrue(SomeIterable(a_is_1) != [{"a": 1}, {"b": 12, "a": 2}])
        self.assertTrue(SomeIterable(a_is_1) != [{"c": 1}, {"b": 12, "a": 1}])
        self.assertTrue(SomeIterable(a_is_1) != [{"c": 1}, "a1"])

        class Foo:
            def __contains__(self, item):
                return True

            def __getitem__(self, item):
                return 1

        self.assertTrue(SomeIterable(a_is_1) == [{"a": 1, "x": 4}, Foo(), Foo()])

    def test_length(self):
        self.assertTrue(SomeIterable(length=3) == (1, 2, 3))
        self.assertTrue(SomeIterable(length=3) == [1, 2, 3])
        self.assertTrue(SomeIterable(length=4) != (1, 2, 3))
        self.assertTrue(SomeIterable(length=4) != [1, 2, 3])

    def test_is_type(self):
        self.assertTrue(SomeIterable(is_type=tuple) == (1, 2, 3))
        self.assertTrue(SomeIterable(is_type=list) == [1, 2, 3])
        self.assertTrue(SomeIterable(is_type=list) != (1, 2, 3))
        self.assertTrue(SomeIterable(is_type=tuple) != [1, 2, 3])


class SomeListTests(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeList() == [4, "a", 3])
        self.assertTrue(SomeList() != (4, 5))
        self.assertTrue(SomeList() != 14)
        self.assertTrue(SomeList() != "abc")

    def test_length(self):
        self.assertTrue(SomeList(length=3) != (1, 2, 3))
        self.assertTrue(SomeList(length=3) == [1, 2, 3])
        self.assertTrue(SomeList(length=4) != [1, 2, 3])

    def test_all(self):
        self.assertTrue(SomeList(int) == [1, 2, 3])
        self.assertTrue(SomeList(int) != [1, 2.5, 3])

        self.assertTrue(SomeList(SomeList()) == [["a", 2], [4.5, 4.2]])
        self.assertTrue(SomeList(SomeList()) != [[], 5])


class SomeDictTests(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeDict() == {})
        self.assertTrue(SomeDict() == {"a": 12, "b": 42})
        self.assertTrue(SomeDict() != {"a", "b", 42})

        self.assertTrue(SomeDict() == {})
        self.assertTrue(SomeDict() == {"a": 12, "b": 42})
        self.assertTrue(SomeDict({"a": 12}) == {"a": 12, "b": 42})
        self.assertTrue(SomeDict({"a": 11}) != {"a": 12, "b": 42})
        self.assertTrue(SomeDict({"a": 12, "b": 42}) == {"a": 12, "b": 42})
        self.assertTrue(SomeDict({"a": 12, "c": 42}) != {"a": 12, "b": 42})

        self.assertTrue(SomeDict(a=12) == {"a": 12, "b": 42})
        self.assertTrue(SomeDict(b=42) == {"a": 12, "b": 42})
        self.assertTrue(SomeDict(a=12, b=42) == {"a": 12, "b": 42})
        self.assertTrue(SomeDict(a=12, c=42) != {"a": 12, "b": 42})

        with self.assertRaises(InvalidArgument):
            _ = SomeDict(12)


class SomeInTest(unittest.TestCase):
    def test_alias(self):
        self.assertTrue(SomeIn is is_in)

    def test_basics(self):
        self.assertTrue(SomeIn([1, 2, 3]) == 1)
        self.assertTrue(SomeIn([1, 2, 3]) != 4)
        self.assertTrue(SomeIn({"a", "b"}) == "a")
        self.assertTrue(SomeIn({"a", "b"}) != "ab")
        self.assertTrue(SomeIn("abcdefg") == "ab")
        self.assertTrue(SomeIn("abcdefg") == "b")
        self.assertTrue(SomeIn("abcdefg") != "ac")

        with self.assertRaises(InvalidArgument):
            _ = SomeIn(42)

    def test_empyt(self):
        with self.assertRaises(TypeError):
            self.assertTrue(SomeIn() == 1)

        self.assertTrue(SomeIn({}) != 0)
        self.assertTrue(SomeIn({}) != None)


class SomeWithLenTest(unittest.TestCase):
    def test_alias(self):
        self.assertTrue(SomeWithLen is has_len)

    def test_basics(self):
        self.assertTrue(SomeWithLen(3) == [1, 2, 3])
        self.assertTrue(SomeWithLen(2) == [1, "a"])
        self.assertTrue(SomeWithLen(2) == {"a": 1, "b": 2})
        self.assertTrue(SomeWithLen(4) == {1, 2, 3, 4})
        self.assertTrue(SomeWithLen(0) == [])

        self.assertFalse(SomeWithLen(2) == [1, "a", str])
        self.assertFalse(SomeWithLen(2) == [])
        self.assertFalse(SomeWithLen(5) == {"a": 1, "b": 2})

        self.assertFalse(SomeWithLen(5) == 1)  # 1 has no __len__

    def test_min_max(self):
        self.assertTrue(SomeWithLen(min_length=2) != [])
        self.assertTrue(SomeWithLen(min_length=2) != [1])
        self.assertTrue(SomeWithLen(min_length=2) == [1, 2])
        self.assertTrue(SomeWithLen(min_length=2) == [1, 2, 3])

        self.assertTrue(SomeWithLen(max_length=2) == [])
        self.assertTrue(SomeWithLen(max_length=2) == [1])
        self.assertTrue(SomeWithLen(max_length=2) == [1, 2])
        self.assertTrue(SomeWithLen(max_length=2) != [1, 2, 3])

        self.assertTrue(SomeWithLen(min_length=1, max_length=2) != [])
        self.assertTrue(SomeWithLen(min_length=1, max_length=2) == [1])
        self.assertTrue(SomeWithLen(min_length=1, max_length=2) == [1, 2])
        self.assertTrue(SomeWithLen(min_length=1, max_length=2) != [1, 2, 3])


class NotSomeTest(unittest.TestCase):
    def test_alias(self):
        self.assertTrue(NotSome is is_not)

    def test_basics(self):
        self.assertTrue(NotSome(str) == 12)
        self.assertTrue(NotSome(str) != "ab")
        self.assertTrue(NotSome(str, int) != 12)
        self.assertTrue(NotSome(str, int) != "ab")
        self.assertTrue(NotSome(str, int) == [12, "ab"])

        def sum_is_5(x):
            return sum(x) == 5
        self.assertTrue(NotSome(sum_is_5) == [3,3])
        self.assertTrue(NotSome(sum_is_5) != [3,2])


class SomeStrTest(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeStr() == "abc")
        self.assertTrue(SomeStr() != 42)
        self.assertTrue(SomeStr() != ["a42"])

    def test_regex(self):
        reg = "a[0-9]z"
        self.assertTrue(SomeStr(regex=reg) == "a8z")
        self.assertTrue(SomeStr(regex=reg) == "a0z")
        self.assertTrue(SomeStr(regex=reg) != "abz")
        self.assertTrue(SomeStr(regex=reg) != "a99z")
        reg = "a[0-9]*z"
        self.assertTrue(SomeStr(regex=reg) == "a8z")
        self.assertTrue(SomeStr(regex=reg) == "a043z")
        self.assertTrue(SomeStr(regex=reg) != "a0o0z")
        self.assertTrue(SomeStr(regex=reg) == "a999z")

    def test_pattern(self):
        self.assertTrue(SomeStr(pattern="py_om_") == "pysome")
        self.assertTrue(SomeStr(pattern="py_om_") == "pyxomx")
        self.assertTrue(SomeStr(pattern="py_om_") != "pxsome")
        self.assertTrue(SomeStr(pattern="py_om_") != "pysome ")
        self.assertTrue(SomeStr(pattern="py_om_") != " pysome")

    def test_endswith(self):
        self.assertTrue(SomeStr(endswith="some") == "pysome")
        self.assertTrue(SomeStr(endswith="some") == "handsome")
        self.assertTrue(SomeStr(endswith="some") != "handsom")
        self.assertTrue(SomeStr(endswith="some") != "handsome ")

    def test_startswith(self):
        self.assertTrue(SomeStr(startswith="py") == "pysome")
        self.assertTrue(SomeStr(startswith="py") == "python")
        self.assertTrue(SomeStr(startswith="py") != " python")
        self.assertTrue(SomeStr(startswith="py") != " pysome")
        self.assertTrue(SomeStr(startswith="py") != "pxthon")


class SomeEmailTest(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeEmail() == "john.doe@web.com")
        self.assertTrue(SomeEmail() != "john.doeweb.com")
        self.assertTrue(SomeEmail() == "johdo@eweb.com")
        self.assertTrue(SomeEmail() != "j.d@ewebcom")


class SomeUuidTest(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(SomeUuid() == "3a01a28d-c79a-4bfa-b190-44a454d3cacb")
        self.assertTrue(SomeUuid() == "7de52743-8a1a-4782-9877-b10bf792172f")
        self.assertTrue(SomeUuid() != "7de52743-8a1a-4782-9877-b10bf792172")
        self.assertTrue(SomeUuid() != "de52743-8a1a-4782-9877-b10bf792172f")
        self.assertTrue(SomeUuid() != "not a uuid")
