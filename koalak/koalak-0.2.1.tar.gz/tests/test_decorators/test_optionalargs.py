import functools
import logging

import pytest
from koalak.decorators import optionalargs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_optionalargs_without_brackets():
    @optionalargs
    def add_attr(obj, attr="x", value=5):
        setattr(obj, attr, value)
        return obj

    @add_attr(attr="y", value=10)
    class A:
        pass

    assert A.y == 10

    @add_attr
    class A:
        pass

    assert A.x == 5

    assert add_attr.__name__ == "add_attr"


def test_optionalargs_with_brackets():
    @optionalargs()
    def add_attr(obj, attr="x", value=5):
        setattr(obj, attr, value)
        return obj

    @add_attr(attr="y", value=10)
    class A:
        pass

    assert A.y == 10

    @add_attr
    class A:
        pass

    assert A.x == 5

    assert add_attr.__name__ == "add_attr"


def test_optionalargs_firtsarg_is_str():
    @optionalargs(firstarg=str)
    def add_name_attr(obj, name="name"):
        obj.name = name
        return obj

    logger.debug("Before without brackets")

    @add_name_attr
    class A:
        pass

    assert A.name == "name"

    logger.debug("Before str as argument")

    @add_name_attr("test")
    class A:
        pass

    assert A.name == "test"


def test_optionalargs_firtsarg_is_str_two_positional_args():
    @optionalargs(firstarg=str)
    def add_attr(obj, attr="x", value=5):
        setattr(obj, attr, value)
        return obj

    logger.debug("Before without brackets")

    @add_attr
    class A:
        pass

    assert A.x == 5

    logger.debug("Before str as argument")

    @add_attr("y")
    class A:
        pass

    assert A.y == 5

    @add_attr("z", 10)
    class A:
        pass

    assert A.z == 10


@pytest.mark.skip(reason="Not implemented yet")
def test_defaultdecorator_decorated():
    # @defaultdecorator(decorated=types.FunctionType)
    def add_name_attr(obj, name="name"):
        obj.name = name
        return obj

    assert add_name_attr.__name__ == "add_name_attr"

    @add_name_attr
    def f():
        pass

    assert f.name == "name"

    @add_name_attr(name="yes")
    def f():
        pass

    assert f.name == "yes"

    # positional argument work because the decorated object
    # is a function type
    @add_name_attr("yy")
    def f():
        pass

    assert f.name == "yy"

    # kwargs always works
    @add_name_attr(name="y")
    class A:
        pass

    assert A.name == "y"

    with pytest.raises(Exception):
        # positional argument on class should not work
        # because we expect types.FunctionType
        @add_name_attr
        class A:
            pass

        assert A.name == "nn"


def test_optionalargs_method_in_cls():
    class Decorator:
        @optionalargs()
        def add_attr(self, obj, attr="x", value=5):
            setattr(obj, attr, value)
            return obj

    d = Decorator()

    @d.add_attr()
    class A:
        pass

    assert A.x == 5

    @d.add_attr
    class B:
        pass

    assert B.x == 5

    @d.add_attr(attr="y")
    class C:
        pass

    assert C.y == 5

    @d.add_attr(value=10)
    class D:
        pass

    assert D.x == 10


def test_optionalargs_modifying_function():
    @optionalargs
    def add_x_to_result(func, x=1):
        @functools.wraps(func)
        def _func(*args, **kwargs):
            result = func(*args, **kwargs)
            return result + x

        return _func

    # without brackets
    @add_x_to_result
    def ret_1():
        return 1

    assert ret_1() == 2

    # with brackets and no args
    @add_x_to_result()
    def ret_1():
        return 1

    assert ret_1() == 2

    # with brackets and optional arg
    @add_x_to_result(x=4)
    def ret_1():
        return 1

    assert ret_1() == 5
