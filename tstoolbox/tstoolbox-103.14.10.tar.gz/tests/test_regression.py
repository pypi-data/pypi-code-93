# -*- coding: utf-8 -*-

import shlex
import subprocess
import sys
from unittest import TestCase

import pandas
from pandas.testing import assert_frame_equal

from tstoolbox import tstoolbox, tsutils


class TestRegression(TestCase):
    def setUp(self):
        dr = pandas.date_range("2000-01-01", periods=2, freq="D")

        ts = pandas.Series([4.5, 4.6], index=dr)

        self.regression_direct = pandas.DataFrame(ts, columns=["Value"])
        self.regression_direct.index.name = "Datetime"
        self.regression_direct = tsutils.memory_optimize(self.regression_direct)

        self.regression_multiple_direct = pandas.DataFrame(ts, columns=["Value"])
        self.regression_multiple_direct = pandas.concat(
            [self.regression_multiple_direct, pandas.Series(ts, name="Value_r")],
            axis="columns",
        )
        self.regression_multiple_direct.index.name = "Datetime"
        self.regression_multiple_direct = tsutils.memory_optimize(
            self.regression_multiple_direct
        )

        self.regression_cli = b"""Datetime,Value
2000-01-01,4.5
2000-01-02,4.6
"""

        self.regression_multiple_cli = b"""Datetime,Value,Value_r
2000-01-01,4.5,4.5
2000-01-02,4.6,4.6
"""

        self.regression_tsstep_2_daily_cli = b"""Datetime,Value,Value1
2000-01-01,4.5,45.6
2000-01-03,4.7,34.2
2000-01-05,4.5,7.2
"""
        self.regression_tsstep_2_daily = pandas.DataFrame(
            [[4.5, 45.6], [4.7, 34.2], [4.5, 7.2]],
            columns=["Value", "Value1"],
            index=pandas.DatetimeIndex(["2000-01-01", "2000-01-03", "2000-01-05"]),
        )
        self.regression_tsstep_2_daily = tsutils.memory_optimize(
            self.regression_tsstep_2_daily
        )

        self.regression_tsstep_2_daily.index.name = "Datetime"

        self.regression_blanks = tsutils.read_iso_ts(
            b"""Datetime,Value::mean,Unnamed::mean,Unnamed.001::mean,Unnamed.002::mean,Unnamed.003::mean,Unnamed.004::mean,Unnamed.005::mean,Unnamed.006::mean,Unnamed.007::mean
2000-01-01,2.46667,,,,,,,,
2000-01-02,3.4,,,,,,,,
"""
        )

    def test_regression_direct(self):
        """Test regression API for single column - daily."""
        out = tstoolbox.regression(input_ts="tests/data_simple.csv")
        assert_frame_equal(out, self.regression_direct)

    def test_regression_mulitple_direct(self):
        """Test regression API for multiple columns - daily."""
        out = tstoolbox.regression(
            "tests/data_simple.csv tests/data_simple.csv", append=r"columns"
        )
        assert_frame_equal(out, self.regression_multiple_direct)

    def test_regression_mulitple_direct_list(self):
        """Test regression API for multiple columns - daily."""
        out = tstoolbox.regression(
            ["tests/data_simple.csv", "tests/data_simple.csv"], append=r"columns"
        )
        assert_frame_equal(out, self.regression_multiple_direct)

    def test_regression_bi_monthly(self):
        """Test regression API for bi monthly time series."""
        out = tstoolbox.regression("tests/data_bi_daily.csv")
        assert_frame_equal(out, self.regression_tsstep_2_daily)

    def test_regression_cli(self):
        """Test regression CLI for single column - daily."""
        args = "tstoolbox regression tests/data_simple.csv"
        args = shlex.split(args)
        out = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        self.assertEqual(out[0], self.regression_cli)

    def test_regression_multiple_cli(self):
        """Test regression CLI for multiple columns - daily."""
        args = "tstoolbox regression --append columns tests/data_simple.csv tests/data_simple.csv"
        args = shlex.split(args)
        out = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        self.assertEqual(out[0], self.regression_multiple_cli)

    def test_regression_multiple_cli_space(self):
        """Test regression CLI for multiple columns - daily."""
        args = "tstoolbox regression --append columns tests/data_simple.csv tests/data_simple.csv"
        args = shlex.split(args)
        out = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        self.assertEqual(out[0], self.regression_multiple_cli)

    def test_regression_bi_monthly_cli(self):
        """Test regression CLI for bi monthly time series."""
        args = "tstoolbox regression tests/data_bi_daily.csv"
        args = shlex.split(args)
        out = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        self.assertEqual(out[0], self.regression_tsstep_2_daily_cli)

    def test_regression_blank_header_cli(self):
        """Test regressioning of files with blank titles in header."""
        args = (
            "tstoolbox aggregate --agg_interval D --input_ts tests/data_empty_cols.csv"
        )
        args = shlex.split(args)
        out = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
        out = tsutils.memory_optimize(tsutils.read_iso_ts(out))
        assert_frame_equal(out, tsutils.memory_optimize(self.regression_blanks))

    def test_regression_multiple_spaces(self):
        """Test regressioning of files with multiple spaces in data."""
        args = "tstoolbox aggregate --agg_interval D --input_ts tests/data_spaces.csv"
        args = shlex.split(args)
        out = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
        out = tsutils.read_iso_ts(out)
        assert_frame_equal(out, self.regression_blanks)
