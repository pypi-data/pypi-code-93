import os
import pytest
from prunner.util.expand import shellexpand_dependencies as deps
from prunner.util import shellexpand


def test_tilde():
    result = deps("~")
    assert result == {"HOME"}

    result2 = deps("~/blah")
    assert result2 == {"HOME"}


def test_complex_item():
    sample_list = ["$HOME/${FOO}", "${BAR:baz}"]
    sample_dict = {"list": sample_list, "unique": "$FROM_DICT"}
    sample_complex_list = ["$STRING", sample_dict]
    actual = deps(sample_complex_list)
    expected = {"HOME", "STRING", "FOO", "BAR", "FROM_DICT"}
    assert actual == expected


def test_escaped_variables():
    query1 = "$FOO.$$BAR"
    query2 = "${FOO}.$${BAR}"

    # Notice that BAR is listed as a dependency
    # Even though it won't actually be used in the full shellexpand
    d1 = deps(query1)
    d2 = deps(query2)
    assert d1 == {"FOO", "BAR"}
    assert d2 == {"FOO", "BAR"}

    # for your benefit, the full expansions look like this:
    # note that BAR is not even defined since it won't be used anyway
    vars = {"FOO": "bar"}
    actual1 = shellexpand(query1, vars)
    actual2 = shellexpand(query2, vars)
    assert actual1 == "bar.$BAR"
    assert actual2 == "bar.${BAR}"
