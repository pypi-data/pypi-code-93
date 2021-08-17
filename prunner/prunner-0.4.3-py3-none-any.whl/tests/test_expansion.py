from prunner.util import shellexpand, VariableNotSet
import os
import pytest


@pytest.fixture
def home():
    return os.path.expanduser("~")


@pytest.fixture
def vars():
    return {"A": "AA", "B": "BBB", "FOO": "bar", "bool": True, "list": [1, 2, 3]}


def test_tilde_expansion_using_system_home(home, vars):
    result = shellexpand("~/a/b/c", vars)
    expected = home + "/a/b/c"
    assert result == expected


def test_tilde_expansion_using_overwritten_home(vars):
    custom_home = "/totally/different"
    vars["HOME"] = custom_home
    result = shellexpand("~/a/b/c", vars)
    expected = custom_home + "/a/b/c"
    assert result == expected


def test_single_variable_keep_native_type(vars):
    result = shellexpand("$bool", vars)
    expected = True
    assert result == expected

    result = shellexpand("$list", vars)
    expected = [1, 2, 3]
    assert result == expected


def test_single_variable_plus_other_string_convert_to_string(vars):
    # yes, whitespace counts as extra string
    result = shellexpand("$bool ", vars)
    expected = "True "
    assert result == expected

    result = shellexpand("$list ", vars)
    expected = "[1, 2, 3] "
    assert result == expected


def test_curly_variable(vars):
    result = shellexpand("${FOO}", vars)
    expected = "bar"
    assert result == expected


def test_curly_defaulted_variable(vars):
    result = shellexpand("${FOO}_${NOT_DEFINED_YET_HAS_DEFAULT:yes}", vars)
    expected = "bar_yes"
    assert result == expected


def test_full_expansion(home, vars):
    result = shellexpand("~/$A/${B}/${C:C}", vars)
    expected = f"{home}/AA/BBB/C"
    assert result == expected


def test_escaped_dollars(home, vars):
    result = shellexpand("~/$$A/$${B}/$$${C:C}/$$$$$B", vars)
    expected = home + "/$A/${B}/$C/$$BBB"
    assert result == expected


def test_missing_variable_throws_exception(vars):
    with pytest.raises(VariableNotSet):
        shellexpand("$NOT_DEFINED", vars)


def test_shellexpand_dict(vars):
    test_input = {
        "static": "This should not change.",
        "dynamic1": "${A}_$B",
        "dynamic2": "$FOO",
    }
    result = shellexpand(test_input, vars)
    expected = {
        "static": "This should not change.",
        "dynamic1": "AA_BBB",
        "dynamic2": "bar",
    }
    assert result == expected


def test_shellexpand_list(vars):
    input_list = ["same", "$FOO", "$A"]
    result = shellexpand(input_list, vars)
    expected = ["same", "bar", "AA"]
    assert result == expected


def test_shellexpand_bool(vars):
    input_value = True
    actual = shellexpand(input_value, vars)
    expected = True
    assert actual == expected


def test_shellexpand_complex(vars):
    input = {"list": ["$A", "${B}", "${B:99}", {"inner_dict": "$FOO"}]}
    actual = shellexpand(input, vars)
    expected = {"list": ["AA", "BBB", "BBB", {"inner_dict": "bar"}]}
    assert actual == expected
