import random
import string

import pytest


@pytest.fixture(scope="function")
def test_dict() -> dict:
    data = {
        "KEY 0": random.randint(-(2 ** 51), 2 ** 51),
        "KEY 1": random.random(),
        "KEY 2": "".join(
            [random.choice(string.ascii_letters) for _ in range(random.randint(0, 512))]
        ),
    }
    return data


def test_constants_as_dict(constants, test_dict):
    """
    Given: a Constants object and a python dictionary
    When: treating the Constants object as a dict for getting and setting
    Then: the Constants object behaves like a dictionary
    """
    for key, value in test_dict.items():
        constants[key] = value

    assert len(constants) == len(test_dict)
    assert sorted(list(constants)) == sorted(list(test_dict.keys()))
    for key, value in test_dict.items():
        assert constants[key] == value


def test_key_exists(constants):
    """
    Given: a populated Constants object
    When: trying to set a key that already exists
    Then: an error is raised
    """
    constants["foo"] = "baz"
    with pytest.raises(ValueError):
        constants["foo"] = "baz2: electric bogaloo"


def test_replace_key(constants):
    """
    Given: a populated Constants object
    When: a constant key is deleted
    Then: the key is removed and no longer exists in the Constants object
    """
    constants["foo"] = "baz"
    del constants["foo"]
    assert "foo" not in constants
    constants["foo"] = "baz3: tokyo drift"
    assert constants["foo"] == "baz3: tokyo drift"


def test_key_does_not_exist(constants):
    """
    Given: a Constants object
    When: trying to get a constant value that doesn't exist
    Then: an error is raised
    """
    with pytest.raises(KeyError):
        _ = constants["foo"]
