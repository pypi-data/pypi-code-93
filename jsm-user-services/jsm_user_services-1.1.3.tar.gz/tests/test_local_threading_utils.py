from jsm_user_services import local_threading
from jsm_user_services.support.local_threading_utils import add_to_local_threading
from jsm_user_services.support.local_threading_utils import get_from_local_threading
from jsm_user_services.support.local_threading_utils import remove_from_local_threading


def test_should_set_local_threading_attribute_to_the_given_value():
    add_to_local_threading("new_attribute", "abc")

    assert hasattr(local_threading, "new_attribute")
    assert local_threading.new_attribute == "abc"

    del local_threading.new_attribute


def test_should_get_from_local_threading_attribute_value():
    local_threading.new_attribute = "abc"

    assert get_from_local_threading("new_attribute") == "abc"

    del local_threading.new_attribute


def test_should_remove_from_local_threading_attribute():
    local_threading.new_attribute = "abc"

    remove_from_local_threading("new_attribute")

    assert not hasattr(local_threading, "new_attribute")
