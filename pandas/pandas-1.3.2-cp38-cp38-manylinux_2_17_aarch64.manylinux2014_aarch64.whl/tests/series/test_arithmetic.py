from datetime import timedelta
import operator

import numpy as np
import pytest
import pytz

from pandas._libs.tslibs import IncompatibleFrequency

from pandas.core.dtypes.common import (
    is_datetime64_dtype,
    is_datetime64tz_dtype,
)

import pandas as pd
from pandas import (
    Categorical,
    Index,
    IntervalIndex,
    Series,
    Timedelta,
    bdate_range,
    date_range,
    isna,
)
import pandas._testing as tm
from pandas.core import (
    nanops,
    ops,
)
from pandas.core.computation import expressions as expr


@pytest.fixture(
    autouse=True, scope="module", params=[0, 1000000], ids=["numexpr", "python"]
)
def switch_numexpr_min_elements(request):
    _MIN_ELEMENTS = expr._MIN_ELEMENTS
    expr._MIN_ELEMENTS = request.param
    yield request.param
    expr._MIN_ELEMENTS = _MIN_ELEMENTS


def _permute(obj):
    return obj.take(np.random.permutation(len(obj)))


class TestSeriesFlexArithmetic:
    @pytest.mark.parametrize(
        "ts",
        [
            (lambda x: x, lambda x: x * 2, False),
            (lambda x: x, lambda x: x[::2], False),
            (lambda x: x, lambda x: 5, True),
            (lambda x: tm.makeFloatSeries(), lambda x: tm.makeFloatSeries(), True),
        ],
    )
    @pytest.mark.parametrize(
        "opname", ["add", "sub", "mul", "floordiv", "truediv", "pow"]
    )
    def test_flex_method_equivalence(self, opname, ts):
        # check that Series.{opname} behaves like Series.__{opname}__,
        tser = tm.makeTimeSeries().rename("ts")

        series = ts[0](tser)
        other = ts[1](tser)
        check_reverse = ts[2]

        op = getattr(Series, opname)
        alt = getattr(operator, opname)

        result = op(series, other)
        expected = alt(series, other)
        tm.assert_almost_equal(result, expected)
        if check_reverse:
            rop = getattr(Series, "r" + opname)
            result = rop(series, other)
            expected = alt(other, series)
            tm.assert_almost_equal(result, expected)

    def test_flex_method_subclass_metadata_preservation(self, all_arithmetic_operators):
        # GH 13208
        class MySeries(Series):
            _metadata = ["x"]

            @property
            def _constructor(self):
                return MySeries

        opname = all_arithmetic_operators
        op = getattr(Series, opname)
        m = MySeries([1, 2, 3], name="test")
        m.x = 42
        result = op(m, 1)
        assert result.x == 42

    def test_flex_add_scalar_fill_value(self):
        # GH12723
        s = Series([0, 1, np.nan, 3, 4, 5])

        exp = s.fillna(0).add(2)
        res = s.add(2, fill_value=0)
        tm.assert_series_equal(res, exp)

    pairings = [(Series.div, operator.truediv, 1), (Series.rdiv, ops.rtruediv, 1)]
    for op in ["add", "sub", "mul", "pow", "truediv", "floordiv"]:
        fv = 0
        lop = getattr(Series, op)
        lequiv = getattr(operator, op)
        rop = getattr(Series, "r" + op)
        # bind op at definition time...
        requiv = lambda x, y, op=op: getattr(operator, op)(y, x)
        pairings.append((lop, lequiv, fv))
        pairings.append((rop, requiv, fv))

    @pytest.mark.parametrize("op, equiv_op, fv", pairings)
    def test_operators_combine(self, op, equiv_op, fv):
        def _check_fill(meth, op, a, b, fill_value=0):
            exp_index = a.index.union(b.index)
            a = a.reindex(exp_index)
            b = b.reindex(exp_index)

            amask = isna(a)
            bmask = isna(b)

            exp_values = []
            for i in range(len(exp_index)):
                with np.errstate(all="ignore"):
                    if amask[i]:
                        if bmask[i]:
                            exp_values.append(np.nan)
                            continue
                        exp_values.append(op(fill_value, b[i]))
                    elif bmask[i]:
                        if amask[i]:
                            exp_values.append(np.nan)
                            continue
                        exp_values.append(op(a[i], fill_value))
                    else:
                        exp_values.append(op(a[i], b[i]))

            result = meth(a, b, fill_value=fill_value)
            expected = Series(exp_values, exp_index)
            tm.assert_series_equal(result, expected)

        a = Series([np.nan, 1.0, 2.0, 3.0, np.nan], index=np.arange(5))
        b = Series([np.nan, 1, np.nan, 3, np.nan, 4.0], index=np.arange(6))

        result = op(a, b)
        exp = equiv_op(a, b)
        tm.assert_series_equal(result, exp)
        _check_fill(op, equiv_op, a, b, fill_value=fv)
        # should accept axis=0 or axis='rows'
        op(a, b, axis=0)


class TestSeriesArithmetic:
    # Some of these may end up in tests/arithmetic, but are not yet sorted

    def test_add_series_with_period_index(self):
        rng = pd.period_range("1/1/2000", "1/1/2010", freq="A")
        ts = Series(np.random.randn(len(rng)), index=rng)

        result = ts + ts[::2]
        expected = ts + ts
        expected.iloc[1::2] = np.nan
        tm.assert_series_equal(result, expected)

        result = ts + _permute(ts[::2])
        tm.assert_series_equal(result, expected)

        msg = "Input has different freq=D from Period\\(freq=A-DEC\\)"
        with pytest.raises(IncompatibleFrequency, match=msg):
            ts + ts.asfreq("D", how="end")

    @pytest.mark.parametrize(
        "target_add,input_value,expected_value",
        [
            ("!", ["hello", "world"], ["hello!", "world!"]),
            ("m", ["hello", "world"], ["hellom", "worldm"]),
        ],
    )
    def test_string_addition(self, target_add, input_value, expected_value):
        # GH28658 - ensure adding 'm' does not raise an error
        a = Series(input_value)

        result = a + target_add
        expected = Series(expected_value)
        tm.assert_series_equal(result, expected)

    def test_divmod(self):
        # GH#25557
        a = Series([1, 1, 1, np.nan], index=["a", "b", "c", "d"])
        b = Series([2, np.nan, 1, np.nan], index=["a", "b", "d", "e"])

        result = a.divmod(b)
        expected = divmod(a, b)
        tm.assert_series_equal(result[0], expected[0])
        tm.assert_series_equal(result[1], expected[1])

        result = a.rdivmod(b)
        expected = divmod(b, a)
        tm.assert_series_equal(result[0], expected[0])
        tm.assert_series_equal(result[1], expected[1])

    @pytest.mark.parametrize("index", [None, range(9)])
    def test_series_integer_mod(self, index):
        # GH#24396
        s1 = Series(range(1, 10))
        s2 = Series("foo", index=index)

        msg = "not all arguments converted during string formatting"

        with pytest.raises(TypeError, match=msg):
            s2 % s1

    def test_add_with_duplicate_index(self):
        # GH14227
        s1 = Series([1, 2], index=[1, 1])
        s2 = Series([10, 10], index=[1, 2])
        result = s1 + s2
        expected = Series([11, 12, np.nan], index=[1, 1, 2])
        tm.assert_series_equal(result, expected)

    def test_add_na_handling(self):
        from datetime import date
        from decimal import Decimal

        s = Series(
            [Decimal("1.3"), Decimal("2.3")], index=[date(2012, 1, 1), date(2012, 1, 2)]
        )

        result = s + s.shift(1)
        result2 = s.shift(1) + s
        assert isna(result[0])
        assert isna(result2[0])

    def test_add_corner_cases(self, datetime_series):
        empty = Series([], index=Index([]), dtype=np.float64)

        result = datetime_series + empty
        assert np.isnan(result).all()

        result = empty + empty.copy()
        assert len(result) == 0

        # FIXME: dont leave commented-out
        # TODO: this returned NotImplemented earlier, what to do?
        # deltas = Series([timedelta(1)] * 5, index=np.arange(5))
        # sub_deltas = deltas[::2]
        # deltas5 = deltas * 5
        # deltas = deltas + sub_deltas

        # float + int
        int_ts = datetime_series.astype(int)[:-5]
        added = datetime_series + int_ts
        expected = Series(
            datetime_series.values[:-5] + int_ts.values,
            index=datetime_series.index[:-5],
            name="ts",
        )
        tm.assert_series_equal(added[:-5], expected)

    def test_mul_empty_int_corner_case(self):
        s1 = Series([], [], dtype=np.int32)
        s2 = Series({"x": 0.0})
        tm.assert_series_equal(s1 * s2, Series([np.nan], index=["x"]))

    def test_sub_datetimelike_align(self):
        # GH#7500
        # datetimelike ops need to align
        dt = Series(date_range("2012-1-1", periods=3, freq="D"))
        dt.iloc[2] = np.nan
        dt2 = dt[::-1]

        expected = Series([timedelta(0), timedelta(0), pd.NaT])
        # name is reset
        result = dt2 - dt
        tm.assert_series_equal(result, expected)

        expected = Series(expected, name=0)
        result = (dt2.to_frame() - dt.to_frame())[0]
        tm.assert_series_equal(result, expected)

    def test_alignment_doesnt_change_tz(self):
        # GH#33671
        dti = date_range("2016-01-01", periods=10, tz="CET")
        dti_utc = dti.tz_convert("UTC")
        ser = Series(10, index=dti)
        ser_utc = Series(10, index=dti_utc)

        # we don't care about the result, just that original indexes are unchanged
        ser * ser_utc

        assert ser.index is dti
        assert ser_utc.index is dti_utc

    def test_arithmetic_with_duplicate_index(self):

        # GH#8363
        # integer ops with a non-unique index
        index = [2, 2, 3, 3, 4]
        ser = Series(np.arange(1, 6, dtype="int64"), index=index)
        other = Series(np.arange(5, dtype="int64"), index=index)
        result = ser - other
        expected = Series(1, index=[2, 2, 3, 3, 4])
        tm.assert_series_equal(result, expected)

        # GH#8363
        # datetime ops with a non-unique index
        ser = Series(date_range("20130101 09:00:00", periods=5), index=index)
        other = Series(date_range("20130101", periods=5), index=index)
        result = ser - other
        expected = Series(Timedelta("9 hours"), index=[2, 2, 3, 3, 4])
        tm.assert_series_equal(result, expected)


# ------------------------------------------------------------------
# Comparisons


class TestSeriesFlexComparison:
    @pytest.mark.parametrize("axis", [0, None, "index"])
    def test_comparison_flex_basic(self, axis, all_compare_operators):
        op = all_compare_operators.strip("__")
        left = Series(np.random.randn(10))
        right = Series(np.random.randn(10))
        result = getattr(left, op)(right, axis=axis)
        expected = getattr(operator, op)(left, right)
        tm.assert_series_equal(result, expected)

    def test_comparison_bad_axis(self, all_compare_operators):
        op = all_compare_operators.strip("__")
        left = Series(np.random.randn(10))
        right = Series(np.random.randn(10))

        msg = "No axis named 1 for object type"
        with pytest.raises(ValueError, match=msg):
            getattr(left, op)(right, axis=1)

    @pytest.mark.parametrize(
        "values, op",
        [
            ([False, False, True, False], "eq"),
            ([True, True, False, True], "ne"),
            ([False, False, True, False], "le"),
            ([False, False, False, False], "lt"),
            ([False, True, True, False], "ge"),
            ([False, True, False, False], "gt"),
        ],
    )
    def test_comparison_flex_alignment(self, values, op):
        left = Series([1, 3, 2], index=list("abc"))
        right = Series([2, 2, 2], index=list("bcd"))
        result = getattr(left, op)(right)
        expected = Series(values, index=list("abcd"))
        tm.assert_series_equal(result, expected)

    @pytest.mark.parametrize(
        "values, op, fill_value",
        [
            ([False, False, True, True], "eq", 2),
            ([True, True, False, False], "ne", 2),
            ([False, False, True, True], "le", 0),
            ([False, False, False, True], "lt", 0),
            ([True, True, True, False], "ge", 0),
            ([True, True, False, False], "gt", 0),
        ],
    )
    def test_comparison_flex_alignment_fill(self, values, op, fill_value):
        left = Series([1, 3, 2], index=list("abc"))
        right = Series([2, 2, 2], index=list("bcd"))
        result = getattr(left, op)(right, fill_value=fill_value)
        expected = Series(values, index=list("abcd"))
        tm.assert_series_equal(result, expected)


class TestSeriesComparison:
    def test_comparison_different_length(self):
        a = Series(["a", "b", "c"])
        b = Series(["b", "a"])
        msg = "only compare identically-labeled Series"
        with pytest.raises(ValueError, match=msg):
            a < b

        a = Series([1, 2])
        b = Series([2, 3, 4])
        with pytest.raises(ValueError, match=msg):
            a == b

    @pytest.mark.parametrize("opname", ["eq", "ne", "gt", "lt", "ge", "le"])
    def test_ser_flex_cmp_return_dtypes(self, opname):
        # GH#15115
        ser = Series([1, 3, 2], index=range(3))
        const = 2
        result = getattr(ser, opname)(const).dtypes
        expected = np.dtype("bool")
        assert result == expected

    @pytest.mark.parametrize("opname", ["eq", "ne", "gt", "lt", "ge", "le"])
    def test_ser_flex_cmp_return_dtypes_empty(self, opname):
        # GH#15115 empty Series case
        ser = Series([1, 3, 2], index=range(3))
        empty = ser.iloc[:0]
        const = 2
        result = getattr(empty, opname)(const).dtypes
        expected = np.dtype("bool")
        assert result == expected

    @pytest.mark.parametrize(
        "op",
        [operator.eq, operator.ne, operator.le, operator.lt, operator.ge, operator.gt],
    )
    @pytest.mark.parametrize(
        "names", [(None, None, None), ("foo", "bar", None), ("baz", "baz", "baz")]
    )
    def test_ser_cmp_result_names(self, names, op):
        # datetime64 dtype
        dti = date_range("1949-06-07 03:00:00", freq="H", periods=5, name=names[0])
        ser = Series(dti).rename(names[1])
        result = op(ser, dti)
        assert result.name == names[2]

        # datetime64tz dtype
        dti = dti.tz_localize("US/Central")
        dti = pd.DatetimeIndex(dti, freq="infer")  # freq not preserved by tz_localize
        ser = Series(dti).rename(names[1])
        result = op(ser, dti)
        assert result.name == names[2]

        # timedelta64 dtype
        tdi = dti - dti.shift(1)
        ser = Series(tdi).rename(names[1])
        result = op(ser, tdi)
        assert result.name == names[2]

        # interval dtype
        if op in [operator.eq, operator.ne]:
            # interval dtype comparisons not yet implemented
            ii = pd.interval_range(start=0, periods=5, name=names[0])
            ser = Series(ii).rename(names[1])
            result = op(ser, ii)
            assert result.name == names[2]

        # categorical
        if op in [operator.eq, operator.ne]:
            # categorical dtype comparisons raise for inequalities
            cidx = tdi.astype("category")
            ser = Series(cidx).rename(names[1])
            result = op(ser, cidx)
            assert result.name == names[2]

    def test_comparisons(self):
        left = np.random.randn(10)
        right = np.random.randn(10)
        left[:3] = np.nan

        result = nanops.nangt(left, right)
        with np.errstate(invalid="ignore"):
            expected = (left > right).astype("O")
        expected[:3] = np.nan

        tm.assert_almost_equal(result, expected)

        s = Series(["a", "b", "c"])
        s2 = Series([False, True, False])

        # it works!
        exp = Series([False, False, False])
        tm.assert_series_equal(s == s2, exp)
        tm.assert_series_equal(s2 == s, exp)

    # -----------------------------------------------------------------
    # Categorical Dtype Comparisons

    def test_categorical_comparisons(self):
        # GH#8938
        # allow equality comparisons
        a = Series(list("abc"), dtype="category")
        b = Series(list("abc"), dtype="object")
        c = Series(["a", "b", "cc"], dtype="object")
        d = Series(list("acb"), dtype="object")
        e = Categorical(list("abc"))
        f = Categorical(list("acb"))

        # vs scalar
        assert not (a == "a").all()
        assert ((a != "a") == ~(a == "a")).all()

        assert not ("a" == a).all()
        assert (a == "a")[0]
        assert ("a" == a)[0]
        assert not ("a" != a)[0]

        # vs list-like
        assert (a == a).all()
        assert not (a != a).all()

        assert (a == list(a)).all()
        assert (a == b).all()
        assert (b == a).all()
        assert ((~(a == b)) == (a != b)).all()
        assert ((~(b == a)) == (b != a)).all()

        assert not (a == c).all()
        assert not (c == a).all()
        assert not (a == d).all()
        assert not (d == a).all()

        # vs a cat-like
        assert (a == e).all()
        assert (e == a).all()
        assert not (a == f).all()
        assert not (f == a).all()

        assert (~(a == e) == (a != e)).all()
        assert (~(e == a) == (e != a)).all()
        assert (~(a == f) == (a != f)).all()
        assert (~(f == a) == (f != a)).all()

        # non-equality is not comparable
        msg = "can only compare equality or not"
        with pytest.raises(TypeError, match=msg):
            a < b
        with pytest.raises(TypeError, match=msg):
            b < a
        with pytest.raises(TypeError, match=msg):
            a > b
        with pytest.raises(TypeError, match=msg):
            b > a

    def test_unequal_categorical_comparison_raises_type_error(self):
        # unequal comparison should raise for unordered cats
        cat = Series(Categorical(list("abc")))
        msg = "can only compare equality or not"
        with pytest.raises(TypeError, match=msg):
            cat > "b"

        cat = Series(Categorical(list("abc"), ordered=False))
        with pytest.raises(TypeError, match=msg):
            cat > "b"

        # https://github.com/pandas-dev/pandas/issues/9836#issuecomment-92123057
        # and following comparisons with scalars not in categories should raise
        # for unequal comps, but not for equal/not equal
        cat = Series(Categorical(list("abc"), ordered=True))

        msg = "Invalid comparison between dtype=category and str"
        with pytest.raises(TypeError, match=msg):
            cat < "d"
        with pytest.raises(TypeError, match=msg):
            cat > "d"
        with pytest.raises(TypeError, match=msg):
            "d" < cat
        with pytest.raises(TypeError, match=msg):
            "d" > cat

        tm.assert_series_equal(cat == "d", Series([False, False, False]))
        tm.assert_series_equal(cat != "d", Series([True, True, True]))

    # -----------------------------------------------------------------

    def test_comparison_tuples(self):
        # GH#11339
        # comparisons vs tuple
        s = Series([(1, 1), (1, 2)])

        result = s == (1, 2)
        expected = Series([False, True])
        tm.assert_series_equal(result, expected)

        result = s != (1, 2)
        expected = Series([True, False])
        tm.assert_series_equal(result, expected)

        result = s == (0, 0)
        expected = Series([False, False])
        tm.assert_series_equal(result, expected)

        result = s != (0, 0)
        expected = Series([True, True])
        tm.assert_series_equal(result, expected)

        s = Series([(1, 1), (1, 1)])

        result = s == (1, 1)
        expected = Series([True, True])
        tm.assert_series_equal(result, expected)

        result = s != (1, 1)
        expected = Series([False, False])
        tm.assert_series_equal(result, expected)

        s = Series([frozenset([1]), frozenset([1, 2])])

        result = s == frozenset([1])
        expected = Series([True, False])
        tm.assert_series_equal(result, expected)

    def test_comparison_operators_with_nas(self, all_compare_operators):
        op = all_compare_operators
        ser = Series(bdate_range("1/1/2000", periods=10), dtype=object)
        ser[::2] = np.nan

        f = getattr(operator, op)

        # test that comparisons work
        val = ser[5]

        result = f(ser, val)
        expected = f(ser.dropna(), val).reindex(ser.index)

        if op == "__ne__":
            expected = expected.fillna(True).astype(bool)
        else:
            expected = expected.fillna(False).astype(bool)

        tm.assert_series_equal(result, expected)

        # FIXME: dont leave commented-out
        # result = f(val, ser)
        # expected = f(val, ser.dropna()).reindex(ser.index)
        # tm.assert_series_equal(result, expected)

    def test_ne(self):
        ts = Series([3, 4, 5, 6, 7], [3, 4, 5, 6, 7], dtype=float)
        expected = [True, True, False, True, True]
        assert tm.equalContents(ts.index != 5, expected)
        assert tm.equalContents(~(ts.index == 5), expected)

    @pytest.mark.parametrize(
        "left, right",
        [
            (
                Series([1, 2, 3], index=list("ABC"), name="x"),
                Series([2, 2, 2], index=list("ABD"), name="x"),
            ),
            (
                Series([1, 2, 3], index=list("ABC"), name="x"),
                Series([2, 2, 2, 2], index=list("ABCD"), name="x"),
            ),
        ],
    )
    def test_comp_ops_df_compat(self, left, right, frame_or_series):
        # GH 1134
        msg = f"Can only compare identically-labeled {frame_or_series.__name__} objects"
        if frame_or_series is not Series:
            left = left.to_frame()
            right = right.to_frame()

        with pytest.raises(ValueError, match=msg):
            left == right
        with pytest.raises(ValueError, match=msg):
            right == left

        with pytest.raises(ValueError, match=msg):
            left != right
        with pytest.raises(ValueError, match=msg):
            right != left

        with pytest.raises(ValueError, match=msg):
            left < right
        with pytest.raises(ValueError, match=msg):
            right < left

    def test_compare_series_interval_keyword(self):
        # GH#25338
        s = Series(["IntervalA", "IntervalB", "IntervalC"])
        result = s == "IntervalA"
        expected = Series([True, False, False])
        tm.assert_series_equal(result, expected)


# ------------------------------------------------------------------
# Unsorted
#  These arithmetic tests were previously in other files, eventually
#  should be parametrized and put into tests.arithmetic


class TestTimeSeriesArithmetic:
    # TODO: De-duplicate with test below
    def test_series_add_tz_mismatch_converts_to_utc_duplicate(self):
        rng = date_range("1/1/2011", periods=10, freq="H", tz="US/Eastern")
        ser = Series(np.random.randn(len(rng)), index=rng)

        ts_moscow = ser.tz_convert("Europe/Moscow")

        result = ser + ts_moscow
        assert result.index.tz is pytz.utc

        result = ts_moscow + ser
        assert result.index.tz is pytz.utc

    def test_series_add_tz_mismatch_converts_to_utc(self):
        rng = date_range("1/1/2011", periods=100, freq="H", tz="utc")

        perm = np.random.permutation(100)[:90]
        ser1 = Series(
            np.random.randn(90), index=rng.take(perm).tz_convert("US/Eastern")
        )

        perm = np.random.permutation(100)[:90]
        ser2 = Series(
            np.random.randn(90), index=rng.take(perm).tz_convert("Europe/Berlin")
        )

        result = ser1 + ser2

        uts1 = ser1.tz_convert("utc")
        uts2 = ser2.tz_convert("utc")
        expected = uts1 + uts2

        assert result.index.tz == pytz.UTC
        tm.assert_series_equal(result, expected)

    def test_series_add_aware_naive_raises(self):
        rng = date_range("1/1/2011", periods=10, freq="H")
        ser = Series(np.random.randn(len(rng)), index=rng)

        ser_utc = ser.tz_localize("utc")

        msg = "Cannot join tz-naive with tz-aware DatetimeIndex"
        with pytest.raises(Exception, match=msg):
            ser + ser_utc

        with pytest.raises(Exception, match=msg):
            ser_utc + ser

    def test_datetime_understood(self):
        # Ensures it doesn't fail to create the right series
        # reported in issue#16726
        series = Series(date_range("2012-01-01", periods=3))
        offset = pd.offsets.DateOffset(days=6)
        result = series - offset
        expected = Series(pd.to_datetime(["2011-12-26", "2011-12-27", "2011-12-28"]))
        tm.assert_series_equal(result, expected)

    def test_align_date_objects_with_datetimeindex(self):
        rng = date_range("1/1/2000", periods=20)
        ts = Series(np.random.randn(20), index=rng)

        ts_slice = ts[5:]
        ts2 = ts_slice.copy()
        ts2.index = [x.date() for x in ts2.index]

        result = ts + ts2
        result2 = ts2 + ts
        expected = ts + ts[5:]
        expected.index = expected.index._with_freq(None)
        tm.assert_series_equal(result, expected)
        tm.assert_series_equal(result2, expected)


class TestNamePreservation:
    @pytest.mark.parametrize("box", [list, tuple, np.array, Index, Series, pd.array])
    @pytest.mark.parametrize("flex", [True, False])
    def test_series_ops_name_retention(
        self, request, flex, box, names, all_binary_operators
    ):
        # GH#33930 consistent name renteiton
        op = all_binary_operators

        if op is ops.rfloordiv and box in [list, tuple] and not flex:
            request.node.add_marker(
                pytest.mark.xfail(
                    reason="op fails because of inconsistent ndarray-wrapping GH#28759"
                )
            )

        left = Series(range(10), name=names[0])
        right = Series(range(10), name=names[1])

        name = op.__name__.strip("_")
        is_logical = name in ["and", "rand", "xor", "rxor", "or", "ror"]
        is_rlogical = is_logical and name.startswith("r")

        right = box(right)
        if flex:
            if is_logical:
                # Series doesn't have these as flex methods
                return
            result = getattr(left, name)(right)
        else:
            # GH#37374 logical ops behaving as set ops deprecated
            warn = FutureWarning if is_rlogical and box is Index else None
            msg = "operating as a set operation is deprecated"
            with tm.assert_produces_warning(warn, match=msg, check_stacklevel=False):
                # stacklevel is correct for Index op, not reversed op
                result = op(left, right)

        if box is Index and is_rlogical:
            # Index treats these as set operators, so does not defer
            assert isinstance(result, Index)
            return

        assert isinstance(result, Series)
        if box in [Index, Series]:
            assert result.name == names[2]
        else:
            assert result.name == names[0]

    def test_binop_maybe_preserve_name(self, datetime_series):
        # names match, preserve
        result = datetime_series * datetime_series
        assert result.name == datetime_series.name
        result = datetime_series.mul(datetime_series)
        assert result.name == datetime_series.name

        result = datetime_series * datetime_series[:-2]
        assert result.name == datetime_series.name

        # names don't match, don't preserve
        cp = datetime_series.copy()
        cp.name = "something else"
        result = datetime_series + cp
        assert result.name is None
        result = datetime_series.add(cp)
        assert result.name is None

        ops = ["add", "sub", "mul", "div", "truediv", "floordiv", "mod", "pow"]
        ops = ops + ["r" + op for op in ops]
        for op in ops:
            # names match, preserve
            ser = datetime_series.copy()
            result = getattr(ser, op)(ser)
            assert result.name == datetime_series.name

            # names don't match, don't preserve
            cp = datetime_series.copy()
            cp.name = "changed"
            result = getattr(ser, op)(cp)
            assert result.name is None

    def test_scalarop_preserve_name(self, datetime_series):
        result = datetime_series * 2
        assert result.name == datetime_series.name


class TestInplaceOperations:
    @pytest.mark.parametrize(
        "dtype1, dtype2, dtype_expected, dtype_mul",
        (
            ("Int64", "Int64", "Int64", "Int64"),
            ("float", "float", "float", "float"),
            ("Int64", "float", "Float64", "Float64"),
            ("Int64", "Float64", "Float64", "Float64"),
        ),
    )
    def test_series_inplace_ops(self, dtype1, dtype2, dtype_expected, dtype_mul):
        # GH 37910

        ser1 = Series([1], dtype=dtype1)
        ser2 = Series([2], dtype=dtype2)
        ser1 += ser2
        expected = Series([3], dtype=dtype_expected)
        tm.assert_series_equal(ser1, expected)

        ser1 -= ser2
        expected = Series([1], dtype=dtype_expected)
        tm.assert_series_equal(ser1, expected)

        ser1 *= ser2
        expected = Series([2], dtype=dtype_mul)
        tm.assert_series_equal(ser1, expected)


def test_none_comparison(series_with_simple_index):
    series = series_with_simple_index
    if isinstance(series.index, IntervalIndex):
        # IntervalIndex breaks on "series[0] = np.nan" below
        pytest.skip("IntervalIndex doesn't support assignment")
    if len(series) < 1:
        pytest.skip("Test doesn't make sense on empty data")

    # bug brought up by #1079
    # changed from TypeError in 0.17.0
    series[0] = np.nan

    # noinspection PyComparisonWithNone
    result = series == None  # noqa
    assert not result.iat[0]
    assert not result.iat[1]

    # noinspection PyComparisonWithNone
    result = series != None  # noqa
    assert result.iat[0]
    assert result.iat[1]

    result = None == series  # noqa
    assert not result.iat[0]
    assert not result.iat[1]

    result = None != series  # noqa
    assert result.iat[0]
    assert result.iat[1]

    if is_datetime64_dtype(series.dtype) or is_datetime64tz_dtype(series.dtype):
        # Following DatetimeIndex (and Timestamp) convention,
        # inequality comparisons with Series[datetime64] raise
        msg = "Invalid comparison"
        with pytest.raises(TypeError, match=msg):
            None > series
        with pytest.raises(TypeError, match=msg):
            series > None
    else:
        result = None > series
        assert not result.iat[0]
        assert not result.iat[1]

        result = series < None
        assert not result.iat[0]
        assert not result.iat[1]


def test_series_varied_multiindex_alignment():
    # GH 20414
    s1 = Series(
        range(8),
        index=pd.MultiIndex.from_product(
            [list("ab"), list("xy"), [1, 2]], names=["ab", "xy", "num"]
        ),
    )
    s2 = Series(
        [1000 * i for i in range(1, 5)],
        index=pd.MultiIndex.from_product([list("xy"), [1, 2]], names=["xy", "num"]),
    )
    result = s1.loc[pd.IndexSlice["a", :, :]] + s2
    expected = Series(
        [1000, 2001, 3002, 4003],
        index=pd.MultiIndex.from_tuples(
            [("a", "x", 1), ("a", "x", 2), ("a", "y", 1), ("a", "y", 2)],
            names=["ab", "xy", "num"],
        ),
    )
    tm.assert_series_equal(result, expected)
