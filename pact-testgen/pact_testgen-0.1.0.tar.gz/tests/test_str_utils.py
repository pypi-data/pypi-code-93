import pytest
from pact_testgen.utils import to_camel_case


@pytest.mark.parametrize(
    "input,expected",
    [
        ("one two three", "OneTwoThree"),
        ("one 2", "One2"),
        ("one-two", "OneTwo"),
        ("one_two", "OneTwo"),
    ],
)
def test_to_camel_case(input, expected):
    assert to_camel_case(input) == expected
