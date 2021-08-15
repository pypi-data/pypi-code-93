import unittest

from Aspidites._vendor.contracts import (decorate, contract,
                                         ContractException, ContractNotRespected)

from Aspidites._vendor.contracts.interface import MissingContract

import sys
import doctest
import unittest
import decimal
import inspect
from asyncio import get_event_loop
from collections import defaultdict, ChainMap, abc as c
from Aspidites._vendor.decorator import dispatch_on, contextmanager, decorator
# try:
#     from . import decorator_documentation as doc  # good with pytest
# except ImportError:
#     import decorator_documentation as doc  # good with `python src/tests/test.py`


@contextmanager
def assertRaises(etype):
    """This works in Python 2.6 too"""
    try:
        yield
    except etype:
        pass
    else:
        raise Exception('Expected %s' % etype.__name__)


@decorator
async def before_after(coro, *args, **kwargs):
    return "<before>" + (await coro(*args, **kwargs)) + "<after>"


@decorator
def coro_to_func(coro, *args, **kw):
    return get_event_loop().run_until_complete(coro(*args, **kw))


class CoroutineTestCase(unittest.TestCase):
    def test_before_after(self):
        @before_after
        async def coro(x):
            return x
        self.assertTrue(inspect.iscoroutinefunction(coro))
        out = get_event_loop().run_until_complete(coro('x'))
        self.assertEqual(out, '<before>x<after>')

    def test_coro_to_func(self):
        @coro_to_func
        async def coro(x):
            return x
        self.assertFalse(inspect.iscoroutinefunction(coro))
        self.assertEqual(coro('x'), 'x')


def gen123():
    yield 1
    yield 2
    yield 3


class GeneratorCallerTestCase(unittest.TestCase):
    def test_gen123(self):
        @decorator
        def square(func, *args, **kw):
            for x in gen123():
                yield x * x
        new = square(gen123)
        self.assertTrue(inspect.isgeneratorfunction(new))
        self.assertEqual(list(new()), [1, 4, 9])


# class DocumentationTestCase(unittest.TestCase):
#     def test(self):
#         err = doctest.testmod(doc)[0]
#         self.assertEqual(err, 0)
#
#     def test_copy_dunder_attrs(self):
#         traced = doc.trace(doc.foo)
#         self.assertIn('documentation', traced.__module__)
#         self.assertEqual(traced.__annotations__, {})
#         self.assertEqual(traced.__defaults__, (None,))
#
#     def test_singledispatch1(self):
#         with assertRaises(RuntimeError):
#             doc.singledispatch_example1()
#
#     def test_singledispatch2(self):
#         doc.singledispatch_example2()
#
#     def test_context_manager(self):
#
#         @contextmanager
#         def before_after(before, after):
#             print(before)
#             yield
#             print(after)
#
#         @before_after('BEFORE', 'AFTER')
#         def hello_user(user):
#             print('hello %s' % user)
#
#         argspec = inspect.getfullargspec(hello_user)
#         self.assertEqual(argspec.args, ['user'])
#
#
# class ExtraTestCase(unittest.TestCase):
#     def test_qualname(self):
#         self.assertEqual(doc.operation1.__qualname__, 'operation1')
#
#     def test_signature(self):
#         sig = inspect.signature(doc.f1)
#         self.assertEqual(str(sig), '(x)')
#
#     def test_unique_filenames(self):
#         @decorator
#         def d1(f, *args, **kwargs):
#             return f(*args, **kwargs)
#
#         @decorator
#         def d2(f, *args, **kwargs):
#             return f(*args, **kwargs)
#
#         @d1
#         def f1(x, y, z):
#             pass
#
#         @d2
#         def f2(x, y, z):
#             pass
#
#         f1_orig = f1
#
#         @d1
#         def f1(x, y, z):
#             pass
#
#         self.assertEqual(d1.__code__.co_filename,
#                          d2.__code__.co_filename)
#         self.assertEqual(f1.__code__.co_filename,
#                          f2.__code__.co_filename)
#         self.assertEqual(f1_orig.__code__.co_filename,
#                          f1.__code__.co_filename)
#
#     def test_no_first_arg(self):
#         @decorator
#         def example(*args, **kw):
#             return args[0](*args[1:], **kw)
#
#         @example
#         def func(**kw):
#             "Docstring"
#             return kw
#
#         # there is no confusion when passing args as a keyword argument
#         self.assertEqual(func(args='a'), {'args': 'a'})
#         self.assertEqual(func.__doc__, "Docstring")
#
#     def test_decorator_factory(self):
#         # similar to what IPython is doing in traitlets.config.application
#         @decorator
#         def catch_config_error(method, app, *args, **kwargs):
#             return method(app)
#         catch_config_error(lambda app, **kw: None)(1)
#
#     def test_add1(self):
#         # similar to what IPython is doing in traitlets.config.application
#         @decorator
#         def add(func, const=1, *args, **kwargs):
#             return const + func(*args, **kwargs)
#
#         def f(x):
#             return x
#         self.assertEqual(add(f, 2)(0), 2)
#
#     def test_dan_schult(self):
#         # see https://github.com/micheles/decorator/issues/120
#         @decorator
#         def prnt(func, index=0, *args, **kw):
#             # print(args[index])
#             return func(*args, **kw)
#
#         @prnt(index=2)  # print the value of the third argument
#         def f(a, b, c=None):
#             return [a, b, c]
#
#         self.assertEqual(f(0, 1), [0, 1, None])
#
#     def test_slow_wrapper(self):
#         # see https://github.com/micheles/decorator/issues/123
#         dd = defaultdict(list)
#         doc.trace(defaultdict.__setitem__)(dd, 'x', [1])
#         self.assertEqual(dd['x'], [1])
#         doc.trace(defaultdict.__delitem__)(dd, 'x')
#         self.assertEqual(dd['x'], [])
#         # NB: defaultdict.__getitem__ has no signature and cannot be
#         # decorated in CPython, while it is regular in PyPy


# ################### test dispatch_on ############################# #
# adapted from test_functools in Python 3.5
singledispatch = dispatch_on('obj')


class TestSingleDispatch(unittest.TestCase):
    def test_simple_overloads(self):
        @singledispatch
        def g(obj):
            return "base"

        @g.register(int)
        def g_int(i):
            return "integer"

        self.assertEqual(g("str"), "base")
        self.assertEqual(g(1), "integer")
        self.assertEqual(g([1, 2, 3]), "base")

    def test_mro(self):
        @singledispatch
        def g(obj):
            return "base"

        class A(object):
            pass

        class C(A):
            pass

        class B(A):
            pass

        class D(C, B):
            pass

        @g.register(A)
        def g_A(a):
            return "A"

        @g.register(B)
        def g_B(b):
            return "B"

        self.assertEqual(g(A()), "A")
        self.assertEqual(g(B()), "B")
        self.assertEqual(g(C()), "A")
        self.assertEqual(g(D()), "B")

    def test_register_decorator(self):
        @singledispatch
        def g(obj):
            return "base"

        @g.register(int)
        def g_int(i):
            return "int %s" % (i,)
        self.assertEqual(g(""), "base")
        self.assertEqual(g(12), "int 12")

    def test_register_error(self):
        @singledispatch
        def g(obj):
            return "base"

        with assertRaises(TypeError):
            # wrong number of arguments
            @g.register(int)
            def g_int():
                return "int"

    def test_wrapping_attributes(self):
        @singledispatch
        def g(obj):
            "Simple test"
            return "Test"
        self.assertEqual(g.__name__, "g")
        if sys.flags.optimize < 2:
            self.assertEqual(g.__doc__, "Simple test")

    def test_c_classes(self):
        @singledispatch
        def g(obj):
            return "base"

        @g.register(decimal.DecimalException)
        def _(obj):
            return obj.args
        subn = decimal.Subnormal("Exponent < Emin")
        rnd = decimal.Rounded("Number got rounded")
        self.assertEqual(g(subn), ("Exponent < Emin",))
        self.assertEqual(g(rnd), ("Number got rounded",))

        @g.register(decimal.Subnormal)
        def _g(obj):
            return "Too small to care."
        self.assertEqual(g(subn), "Too small to care.")
        self.assertEqual(g(rnd), ("Number got rounded",))

    def test_register_abc(self):
        d = {"a": "b"}
        l = [1, 2, 3]
        s = set([object(), None])
        f = frozenset(s)
        t = (1, 2, 3)

        @singledispatch
        def g(obj):
            return "base"

        self.assertEqual(g(d), "base")
        self.assertEqual(g(l), "base")
        self.assertEqual(g(s), "base")
        self.assertEqual(g(f), "base")
        self.assertEqual(g(t), "base")

        g.register(c.Sized)(lambda obj: "sized")
        self.assertEqual(g(d), "sized")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.MutableMapping)(lambda obj: "mutablemapping")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(ChainMap)(lambda obj: "chainmap")
        # irrelevant ABCs registered
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.MutableSequence)(lambda obj: "mutablesequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.MutableSet)(lambda obj: "mutableset")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.Mapping)(lambda obj: "mapping")
        self.assertEqual(g(d), "mutablemapping")  # not specific enough
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.Sequence)(lambda obj: "sequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sequence")

        g.register(c.Set)(lambda obj: "set")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(dict)(lambda obj: "dict")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(list)(lambda obj: "list")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(set)(lambda obj: "concrete-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(frozenset)(lambda obj: "frozen-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "sequence")

        g.register(tuple)(lambda obj: "tuple")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "tuple")

    def test_mro_conflicts(self):
        @singledispatch
        def g(obj):
            return "base"

        class O(c.Sized):
            def __len__(self):
                return 0
        o = O()
        self.assertEqual(g(o), "base")
        g.register(c.Iterable)(lambda arg: "iterable")
        g.register(c.Container)(lambda arg: "container")
        g.register(c.Sized)(lambda arg: "sized")
        g.register(c.Set)(lambda arg: "set")
        self.assertEqual(g(o), "sized")
        c.Iterable.register(O)
        self.assertEqual(g(o), "sized")
        c.Container.register(O)
        with assertRaises(RuntimeError):  # was "sized" because in mro
            self.assertEqual(g(o), "sized")
        c.Set.register(O)
        self.assertEqual(g(o), "set")

        class P(object):
            pass
        p = P()
        self.assertEqual(g(p), "base")
        c.Iterable.register(P)
        self.assertEqual(g(p), "iterable")
        c.Container.register(P)

        with assertRaises(RuntimeError):
            self.assertEqual(g(p), "iterable")

        class Q(c.Sized):
            def __len__(self):
                return 0
        q = Q()
        self.assertEqual(g(q), "sized")
        c.Iterable.register(Q)
        self.assertEqual(g(q), "sized")
        c.Set.register(Q)
        self.assertEqual(g(q), "set")
        # because c.Set is a subclass of c.Sized and c.Iterable

        @singledispatch
        def h(obj):
            return "base"

        @h.register(c.Sized)
        def h_sized(arg):
            return "sized"

        @h.register(c.Container)
        def h_container(arg):
            return "container"
        # Even though Sized and Container are explicit bases of MutableMapping,
        # this ABC is implicitly registered on defaultdict which makes all of
        # MutableMapping's bases implicit as well from defaultdict's
        # perspective.
        with assertRaises(RuntimeError):
            self.assertEqual(h(defaultdict(lambda: 0)), "sized")

        class R(defaultdict):
            pass
        c.MutableSequence.register(R)

        @singledispatch
        def i(obj):
            return "base"

        @i.register(c.MutableMapping)
        def i_mapping(arg):
            return "mapping"

        @i.register(c.MutableSequence)
        def i_sequence(arg):
            return "sequence"
        r = R()
        with assertRaises(RuntimeError):  # was no error
            self.assertEqual(i(r), "sequence")

        class S(object):
            pass

        class T(S, c.Sized):
            def __len__(self):
                return 0
        t = T()
        self.assertEqual(h(t), "sized")
        c.Container.register(T)
        self.assertEqual(h(t), "sized")   # because it's explicitly in the MRO

        class U(object):
            def __len__(self):
                return 0
        u = U()
        self.assertEqual(h(u), "sized")
        # implicit Sized subclass inferred
        # from the existence of __len__()

        c.Container.register(U)
        # There is no preference for registered versus inferred ABCs.
        with assertRaises(RuntimeError):
            h(u)


class DecoratorTests(unittest.TestCase):

    def test_malformed(self):
        def f():
            """
                Wrong syntax

                :rtype okok
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_malformed2(self):
        def f():
            """
                Wrong syntax

                :rtype: okok
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_not_specified1(self):
        """ No docstring specified """
        def f():
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_not_specified2(self):
        def f():
            """ No types specified in the docstring """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_too_many(self):
        def f():
            """
                Too many rtype clauses.
                :rtype: int
                :rtype: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_invalid1(self):
        def f(a):
            """ Unknown b.
                :type a: int
                :type b: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_parse_error1(self):
        def f(a, b):
            """ Same with optional
                :type a: in
                :type b: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_parse_error2(self):
        def f(a, b):
            """ Same with optional
                :type a: int
                :type b: int
                :rtype: in
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def not_supported1(self):
        """ Support of *args """

        def f(a, *b):  # @UnusedVariable
            """
                :type a: int
                :type b: tuple(int)
                :rtype: int
            """
            pass

            decorate(f)

    def not_supported2(self):
        """ Support of **args """
        def f(a, **b):
            """
                :type a: int
                :type b: dict(int:int)
                :rtype: int
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_ok1(self):
        @contract
        def f(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            pass

    def test_ok3(self):
        """ Trying the quoting thing. """
        @contract
        def f(a, b):
            """ This is good
                :type a: ``int``
                :type b: ``int``
                :rtype: ``int``
            """
            pass

    def test_bad_quoting(self):
        def f(a, b):
            """
                :type a: ``int``
                :type b: ``int``
                :rtype: ``int`
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_bad_quoting2(self):
        def f(a, b):
            """
                :type a: ``int``
                :type b: `int``
                :rtype: ``int``
            """
            pass

        self.assertRaises(ContractException, decorate, f)

    def test_ok2(self):
        @contract(a='int', returns='int')
        def f(a, b):
            pass

    def test_invalid_args(self):
        def f():
            @contract(1)
            def g(a, b):
                return int(a + b)
        self.assertRaises(ContractException, f)

    def test_invalid_args2(self):
        """ unknown parameter """
        def f():
            @contract(c=2)
            def g(a, b):
                return int(a + b)
        self.assertRaises(ContractException, f)

    def test_check_it_works1(self):
        @contract(a='int', b='int', returns='int')
        def f(a, b):  # @UnusedVariable
            return 2.0
        self.assertRaises(ContractNotRespected, f, 1, 2)

    def test_check_it_works2(self):
        @contract(a='int', b='int', returns='int')
        def f(a, b):  # @UnusedVariable
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, 1, 2.0)

    def test_check_it_works2b(self):
        """ Nothing for b """
        @contract(a='int', returns='int')
        def f(a, b):  # @UnusedVariable
            return int(a + b)
        f(1, 2)
        f(1, 2.0)

    def test_check_it_works2c(self):
        """ Nothing for b """
        def f1(a, b):  # @UnusedVariable
            return int(a + b)

        f = decorate(f1, a='int', returns='int')

        f(1, 2)
        f(1, 2.0)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)

    # def test_module_as_decorator(self):
    #     import contracts as contract_module
    #
    #     @contract_module
    #     def f(a, b): #@UnusedVariable
    #         return a + b
    #     f(1, 2)
    #     self.assertRaises(ContractNotRespected, f, 1.0, 2)

    def test_check_it_works3(self):
        @contract
        def f(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, 1, 2.0)

    def test_inline_docstring_format_works(self):
        @contract
        def f(a, b):
            """ This is good
                :param int,>0 a: Description
                :param int,>0 b: Description
                :returns int,>0: Description
            """
            return a + b
        f(1, 2)
        self.assertRaises(ContractNotRespected, f, 1.0, 2)
        self.assertRaises(ContractNotRespected, f, -1, 2)

    def test_check_docstring_maintained(self):
        def f1(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b

        def f2(string):
            pass

        f1_dec = decorate(f1)
        self.assertNotEqual(f1.__doc__, f1_dec.__doc__)
        self.assertEqual(f1.__name__, f1_dec.__name__)
        self.assertEqual(f1.__module__, f1_dec.__module__)

        f2_dec = decorate(f2, string='str')
        self.assertNotEqual(f2.__doc__, f2_dec.__doc__)
        self.assertEqual(f2.__name__, f2_dec.__name__)
        self.assertEqual(f2.__module__, f2_dec.__module__)

        f1_dec_p = decorate(f1, modify_docstring=False)
        self.assertEqual(f1_dec_p.__doc__, f1.__doc__)

        f2_dec_p = decorate(f2, modify_docstring=False, string='str')
        self.assertEqual(f2.__doc__, f2_dec_p.__doc__)

        @contract
        def f1b(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b

        @contract(string='str')
        def f2b(string):
            pass

        @contract(modify_docstring=False)
        def f1b_p(a, b):
            """ This is good
                :type a: int
                :type b: int
                :rtype: int
            """
            return a + b

        @contract(modify_docstring=False, string='str')
        def f2b_p(string):
            pass

        self.assertNotEqual(f1.__doc__, f1b.__doc__)
        self.assertEqual(f1.__doc__, f1b_p.__doc__)
        self.assertNotEqual(f2.__doc__, f2b.__doc__)
        self.assertEqual(f2.__doc__, f2b_p.__doc__)

    def test_kwargs(self):
        def f(a, b, c=7):  # @UnusedVariable
            """ Same with optional
                :type a: int
                :type b: int
                :type c: int
            """
            if c != b:
                raise Exception()

        f2 = decorate(f)
        f2(0, 7)
        f2(0, 5, 5)
        self.assertRaises(Exception, f2, 0, 5, 4)
        self.assertRaises(Exception, f2, 0, 5)

    def test_varargs(self):
        def f(a, b, *c):
            """ Same with optional
                :type a: int
                :type b: int
                :type c: tuple
            """
            assert c == (a, b)

        f2 = decorate(f)
        f2(0, 7, 0, 7)

    def test_keywords(self):
        def f(A, B, **c):
            """ Same with optional
                :type A: int
                :type B: int
                :type c: dict
            """
            assert c['a'] == A
            assert c['b'] == B

        f2 = decorate(f)
        f(0, 7, a=0, b=7)
        f2(0, 7, a=0, b=7)

        self.assertRaises(Exception, f2, 0, 5, 0, 6)

    def test_same_signature(self):
        from inspect import getfullargspec

        def f(a):
            return a

        @contract(a='int')
        def f2(a):
            return a

        self.assertEqual(getfullargspec(f2), getfullargspec(f))


    def test_empty_types(self):

        def x():
            @contract
            def f(myparam):
                """
                :param myparam: something
                """

        self.assertRaises(MissingContract, x)

    def test_empty_types2(self):

        @contract
        def f(x):
            """
            :param x: something
            :type x: *
            """

        f(1)
