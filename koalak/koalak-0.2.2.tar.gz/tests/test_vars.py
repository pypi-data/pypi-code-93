import koalak
import pytest


def test_create_variable():
    framework = koalak.mkframework()
    framework.create_variable("name", "test")
    assert framework.get_variable("name") == "test"


@pytest.mark.skip
def test_init_variable_in_mkframework():
    framework = koalak.mkframework(variables={"age": 30})
    assert framework.get_variable("age") == 30


def test_set_variable():
    framework = koalak.mkframework()
    framework.create_variable("name", "test")
    assert framework.get_variable("name") == "test"
    framework.set_variable("name", 30)
    assert framework.get_variable("name") == 30


# TODO: add list variables
