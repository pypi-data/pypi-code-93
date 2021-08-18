import inspect

import pytest
from koalak import add_post_init


def addx_post_init(self):
    self.x = True


def addy_post_init(self):
    self.y = True


def addz_post_init(self):
    self.z = True


def test_cls_with_simple_init():
    @add_post_init(addx_post_init)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert a.a is True
    assert a.x is True


def test_cls_with_complex_init():
    @add_post_init(addx_post_init)
    class A:
        def __init__(self, a, b, *, c, d):
            self.a = a
            self.b = b
            self.c = c
            self.d = d

    a = A(1, 2, c=3, d=4)
    assert a.a == 1
    assert a.b == 2
    assert a.c == 3
    assert a.d == 4
    assert a.x is True


def test_multiple_post_inits():
    # When the cls has multiple post_inits
    # execute them all
    @add_post_init(addx_post_init)
    @add_post_init(addy_post_init)
    @add_post_init(addz_post_init)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert a.a is True
    assert a.x is True
    assert a.y is True
    assert a.z is True


def test_inheritence():
    class A:
        def __init__(self):
            self.a = True

    @add_post_init(addx_post_init)
    class B(A):
        def __init__(self):
            super().__init__()
            self.b = True

    a = A()
    assert a.a is True
    assert not hasattr(a, "b")
    assert not hasattr(a, "x")

    b = B()
    assert b.a is True
    assert b.b is True
    assert b.x is True


def test_cls_without_init():
    @add_post_init(addx_post_init)
    class A:
        pass

    a = A()
    assert a.x is True


def test_cls_without_init_and_parent_init():
    # the add_post_init must not modify the parent init
    class A:
        def __init__(self):
            self.a = True

    @add_post_init(addx_post_init)
    class B(A):
        pass

    a = A()
    assert a.a is True
    assert not hasattr(a, "x")

    b = B()
    assert b.a is True
    assert b.x is True


def test_if_signature_changed():
    class A:
        def __init__(self, a: str, b: int, *, c: bool, d: str):
            """my init"""
            self.a = a
            self.b = b
            self.c = c
            self.d = d

    original_signature = inspect.signature(A)
    original_doc = A.__init__.__doc__
    # apply decorator dynamically
    A = add_post_init(addx_post_init)(A)

    assert inspect.signature(A) == original_signature
    assert A.__init__.__doc__ == original_doc

    a = A("a", 1, c=True, d="b")
    assert a.a == "a"
    assert a.b == 1
    assert a.c is True
    assert a.d == "b"
    assert a.x is True


def test_signature_of_created_init():
    class A:
        pass

    original_signature = inspect.signature(A)
    # apply decorator dynamically
    A = add_post_init(addx_post_init)(A)
    a = A()
    assert a.x is True

    with pytest.raises(TypeError):
        # Verify that signature is not *args, **kwargs
        A(1)

    assert inspect.signature(A) == original_signature
