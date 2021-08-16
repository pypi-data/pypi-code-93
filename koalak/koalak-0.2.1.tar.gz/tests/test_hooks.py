import koalak
import pytest
from koalak import exceptions


def test_mkhookmanager():
    framework = koalak.mkframework()

    @framework.mkhookmanager
    def hooka():
        pass

    assert framework.get_hook_manager("hooka") is hooka
    assert hooka.name == "hooka"

    @framework.mkhookmanager("hookb")
    def f():
        pass

    assert framework.get_hook_manager("hookb") is f
    assert f.name == "hookb"


def test_runall():
    framework = koalak.mkframework()

    @framework.mkhookmanager
    def binnary_opp(a, b):
        pass

    @binnary_opp.register
    def add(a, b):
        return a + b

    @binnary_opp.register
    def mult(a, b):
        return a * b

    results = binnary_opp.runall(3, 4)
    assert results == [7, 12]


def test_get_hook_manager():
    framework = koalak.mkframework()

    @framework.mkhookmanager
    def hm_a():
        pass

    @framework.mkhookmanager
    def hm_b():
        pass

    assert framework.get_hook_manager("hm_a") is hm_a
    assert framework.get_hook_manager("hm_b") is hm_b

    assert framework.get_hook_managers() == [hm_a, hm_b]


def test_get_hook():
    framework = koalak.mkframework()

    @framework.mkhookmanager
    def hm_a():
        pass

    @hm_a.register
    def f():
        pass

    @hm_a.register
    def f2():
        pass

    assert hm_a.get_hook("f") is f
    assert hm_a.get_hook("f2") is f2
    assert framework.get_hook("hm_a", "f") is f
    assert framework.get_hook("hm_a", "f2") is f2


def test_hook_already_exist():
    framework = koalak.mkframework()

    @framework.mkhookmanager
    def hm():
        pass

    @hm.register
    def f():  # noqa: F811
        pass

    with pytest.raises(exceptions.HookAlreadyExistException):

        @hm.register  # noqa: F811
        def f():  # noqa: F811
            pass


def test_hook_manager_already_exist():
    framework = koalak.mkframework()

    @framework.mkhookmanager("a")
    def a():
        pass

    with pytest.raises(exceptions.HookManagerAlreadyExistException):

        @framework.mkhookmanager("a")
        def b():
            pass
