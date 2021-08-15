# -*- coding: utf-8 -*-

"""Top-level package for MYSTRAN validation."""

__author__ = """Nicolas Cordier"""
__email__ = "nicolas.cordier@numeric-gmbh.ch"
__version__ = "0.4.0"


def assert_frame_equal(dfa, dfb, atol, rtol):
    """it's hard to understand how pandas tesing is actually working
    better to fall back to numpy testing, assuming we do not need to
    check columns, index, etc...
    """
    diff = abs(dfa - dfb)
    crit = atol + rtol * abs(dfb)
    failing = diff[diff > crit]
    # keep rows and columns where at least one failure occurs
    failures = failing.dropna(how="all").dropna(how="all", axis=1)
    abs_error = failing.max().max()
    rel_error = (failing / abs(dfb)).max().max()
    return failures, abs_error, rel_error
