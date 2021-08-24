"""Tests for trading.datasets.dataset_info."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from dateutil import relativedelta
import pytest

from trading.datasets import errors
from trading.datasets import dataset_info


@pytest.fixture(name='metadata', scope="class")
def fixture_metadata():
    metadata = dataset_info.OHLCVMetadata()
    metadata.exchange = 'Bitmex'
    metadata.symbol = 'BTCUSDT'

    return metadata


@pytest.fixture(name='timeframe', scope="class")
def fixture_timeframe():
    return dataset_info.Timeframe('3d')


@pytest.fixture(name='timeframe_unit', scope="class")
def fixture_timeframe_unit():
    return dataset_info.TimeframeUnit('ms')


class TestOHLCVMetadata:

    def test_initialization(self, metadata):
        metadata.exchange = 'Bitmex'
        metadata.symbol = 'BTCUSDT'

        assert isinstance(metadata, dataset_info.OHLCVMetadata)
        assert metadata.exchange == 'Bitmex'
        assert metadata.symbol == 'BTCUSDT'

        metadata = dataset_info.OHLCVMetadata(exchange='Test', symbol='TE/ST')
        assert isinstance(metadata, dataset_info.OHLCVMetadata)
        assert metadata.exchange == 'Test'
        assert metadata.symbol == 'TE/ST'

        metadata = dataset_info.OHLCVMetadata(metadata)
        assert isinstance(metadata, dataset_info.OHLCVMetadata)
        assert metadata.exchange == 'Test'
        assert metadata.symbol == 'TE/ST'

        metadata = dataset_info.OHLCVMetadata()
        assert isinstance(metadata, dataset_info.OHLCVMetadata)
        assert not metadata.exchange
        assert not metadata.symbol

        metadata = dataset_info.OHLCVMetadata([], '')
        assert isinstance(metadata, dataset_info.OHLCVMetadata)
        assert not metadata.exchange
        assert not metadata.symbol

        metadata = dataset_info.OHLCVMetadata(exchange='Test2', symbol=123)
        assert isinstance(metadata, dataset_info.OHLCVMetadata)
        assert metadata.exchange == 'Test2'
        assert metadata.symbol == '123'

    def test_exchange_property(self, metadata):
        metadata.exchange = 1
        assert isinstance(metadata.exchange, str)
        assert metadata.exchange == '1'

        metadata.exchange = 'Binance'
        assert isinstance(metadata.exchange, str)
        assert metadata.exchange == 'Binance'

        metadata.exchange = None
        assert metadata.exchange is None

        metadata.exchange = []
        assert metadata.exchange is None

        metadata.exchange = ''
        assert metadata.exchange is None

        metadata.exchange = 0
        assert metadata.exchange is None

    def test_symbol_property(self, metadata):
        metadata.symbol = 1
        assert isinstance(metadata.symbol, str)
        assert metadata.symbol == '1'

        metadata.symbol = 'ETH/USD'
        assert isinstance(metadata.symbol, str)
        assert metadata.symbol == 'ETH/USD'

        metadata.symbol = None
        assert metadata.symbol is None

        metadata.symbol = []
        assert metadata.symbol is None

        metadata.symbol = ''
        assert metadata.symbol is None

        metadata.symbol = 0
        assert metadata.symbol is None

    def test_equality_operation(self, metadata):
        assert metadata == metadata  # pylint: disable=comparison-with-itself

        metadata.exchange = 'A'
        metadata.symbol = 'm'
        assert metadata == dataset_info.OHLCVMetadata(exchange='A', symbol='m')

    def test_to_repr_conversion(self, metadata):
        assert repr(metadata) == (
            f'{metadata.__class__.__name__}('
            f'exchange={metadata.exchange!r}, '
            f'symbol={metadata.symbol!r}'
            ')'
        )

    def test_to_bool_conversion(self, metadata):
        metadata.exchange = 'Bitmex'
        metadata.symbol = 'BTCUSDT'
        assert bool(metadata)

        metadata.exchange = None
        metadata.symbol = None
        assert not bool(metadata)

        assert not bool(dataset_info.OHLCVMetadata())


class TestTimeframe:

    def test_initialization(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert isinstance(timeframe, dataset_info.Timeframe)
        assert timeframe.interval == 3
        assert timeframe.unit == 'd'

        timeframe = dataset_info.Timeframe(interval='8', unit='h')
        assert timeframe.interval == 8
        assert timeframe.unit == 'h'

        timeframe = dataset_info.Timeframe(timeframe)
        assert timeframe.interval == 8
        assert timeframe.unit == 'h'

        timeframe = dataset_info.Timeframe()
        assert not timeframe.interval
        assert not timeframe.unit

        timeframe = dataset_info.Timeframe(interval=8.0, unit='h')
        assert timeframe.interval == 8
        assert timeframe.unit == 'h'

        timeframe = dataset_info.Timeframe('250ms')
        assert timeframe.interval == 250
        assert timeframe.unit == 'ms'

        with pytest.raises(errors.InvalidTimeframeError):
            dataset_info.Timeframe(interval=['invalid', 'interval'], unit='h')

        with pytest.raises(errors.InvalidTimeframeError):
            dataset_info.Timeframe(interval={1: 2, 3: 4}, unit='h')

    def test_interval_property(self, timeframe):
        timeframe.interval = 3
        assert isinstance(timeframe.interval, int)
        assert timeframe.interval == 3

        timeframe.interval = 0
        assert isinstance(timeframe.interval, int)
        assert timeframe.interval == 0

        timeframe.interval = -5
        assert isinstance(timeframe.interval, int)
        assert timeframe.interval == -5

        timeframe.interval = '-9.999'
        assert isinstance(timeframe.interval, int)
        assert timeframe.interval == -9

        timeframe.interval = '4.7'
        assert isinstance(timeframe.interval, int)
        assert timeframe.interval == 4

        timeframe.interval = 12.5
        assert isinstance(timeframe.interval, int)
        assert timeframe.interval == 12

        timeframe.interval = 'RANDOM VALUE'
        assert timeframe.interval is None

        timeframe.interval = None
        assert timeframe.interval is None

        timeframe.interval = [1, 2, 3]
        assert timeframe.interval is None

        timeframe.interval = ''
        assert timeframe.interval is None

    def test_unit_property(self, timeframe):
        timeframe.unit = 'd'
        assert isinstance(timeframe.unit, dataset_info.TimeframeUnit)
        assert str(timeframe.unit) == 'd'

        timeframe.unit = 'm'
        assert isinstance(timeframe.unit, dataset_info.TimeframeUnit)
        assert str(timeframe.unit) == 'm'

        with pytest.raises(errors.UnknownTimeframeUnitError):
            timeframe.unit = 'some unknown unit'

        with pytest.raises(errors.UnknownTimeframeUnitError):
            timeframe.unit = 'D'

    def test_equality_operation(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert timeframe == timeframe  # pylint: disable=comparison-with-itself
        assert timeframe == '3d'

        timeframe.interval = 2
        timeframe.unit = 'y'
        assert timeframe == timeframe  # pylint: disable=comparison-with-itself
        assert timeframe == '2y'

        assert dataset_info.Timeframe('1d') == dataset_info.Timeframe('24h')
        assert dataset_info.Timeframe() == dataset_info.Timeframe()

    def test_to_repr_conversion(self, timeframe):
        assert repr(timeframe) == (
            f'{timeframe.__class__.__name__}('
            f'interval={timeframe.interval!r}, '
            f'unit={timeframe.unit!r}'
            ')'
        )

    def test_to_str_conversion(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert str(timeframe) == '3d'

        timeframe.interval = 5.7
        timeframe.unit = 'h'
        assert str(timeframe) == '5h'

        timeframe.interval = None
        timeframe.unit = None
        assert str(timeframe) == '0'

    def test_to_duration_conversion(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert pytest.approx(timeframe.get_duration('y')) == 0.008219178082
        assert pytest.approx(timeframe.get_duration('w')) == 0.428571428571
        assert pytest.approx(timeframe.get_duration('M')) == 0.1
        assert timeframe.get_duration('d') == 3
        assert timeframe.get_duration('h') == 72
        assert timeframe.get_duration('m') == 4320
        assert timeframe.get_duration('s') == 259200
        assert timeframe.get_duration('ms') == 259200000

        assert dataset_info.Timeframe().get_duration() == 0

        with pytest.raises(errors.UnknownTimeframeUnitError):
            timeframe.get_duration('some unknown unit')

    def test_to_pandas_timeframe_conversion(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert timeframe.to_pandas_timeframe() == '3D'
        assert not dataset_info.Timeframe(0).to_pandas_timeframe()
        assert not dataset_info.Timeframe(
            interval=1, unit=None).to_pandas_timeframe()

    def test_to_offset_timeframe_conversion(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert timeframe.to_offset_timeframe() == '3d'

        assert not dataset_info.Timeframe(0).to_offset_timeframe()
        assert not dataset_info.Timeframe(
            interval=1, unit=None).to_offset_timeframe()

    def test_to_timedelta_conversion(self, timeframe):
        timeframe.interval = 3
        timeframe.unit = 'd'
        assert timeframe.to_timedelta() == relativedelta.relativedelta(days=3)

        assert dataset_info.Timeframe(
            '1d').to_timedelta() == relativedelta.relativedelta(hours=24)
        assert dataset_info.Timeframe(
            '1M').to_timedelta() == relativedelta.relativedelta(days=30.4167)
        assert dataset_info.Timeframe(
            '1y').to_timedelta() == relativedelta.relativedelta(days=365)
        assert dataset_info.Timeframe(
            '3d').to_timedelta() == relativedelta.relativedelta(days=3)
        assert dataset_info.Timeframe(
            '4h').to_timedelta() == relativedelta.relativedelta(hours=4)
        assert dataset_info.Timeframe(
            '69ms').to_timedelta() == relativedelta.relativedelta(
                microseconds=69000)


class TestTimeframeUnit:

    def test_initialization(self, timeframe_unit):
        assert isinstance(timeframe_unit, dataset_info.TimeframeUnit)

        assert not dataset_info.TimeframeUnit()
        assert not dataset_info.TimeframeUnit(None)
        assert not dataset_info.TimeframeUnit([])
        assert not dataset_info.TimeframeUnit('')

        inner_timeframe_unit = dataset_info.TimeframeUnit('h')
        outer_timeframe_unit = dataset_info.TimeframeUnit(inner_timeframe_unit)
        assert isinstance(outer_timeframe_unit, dataset_info.TimeframeUnit)
        assert inner_timeframe_unit == 'h'
        assert outer_timeframe_unit == 'h'

        with pytest.raises(errors.UnknownTimeframeUnitError):
            dataset_info.TimeframeUnit('some unknown unit')

        with pytest.raises(errors.UnknownTimeframeUnitError):
            dataset_info.TimeframeUnit(8012)

    def test_equality_operation(self, timeframe_unit):
        assert timeframe_unit == 'ms'

        assert dataset_info.TimeframeUnit('h') == 'h'
        assert dataset_info.TimeframeUnit('y') == 'y'
        assert dataset_info.TimeframeUnit('m') == 'm'
        assert dataset_info.TimeframeUnit('M') == 'M'

    def test_to_repr_conversion(self, timeframe_unit):
        assert repr(timeframe_unit) == repr('ms')

    def test_to_str_conversion(self, timeframe_unit):
        assert str(timeframe_unit) == str('ms')

    def test_to_seconds_conversion(self):
        assert dataset_info.TimeframeUnit('y').to_seconds() == 31536000
        assert dataset_info.TimeframeUnit('M').to_seconds() == 2592000
        assert dataset_info.TimeframeUnit('w').to_seconds() == 604800
        assert dataset_info.TimeframeUnit('d').to_seconds() == 86400
        assert dataset_info.TimeframeUnit('h').to_seconds() == 3600
        assert dataset_info.TimeframeUnit('m').to_seconds() == 60
        assert dataset_info.TimeframeUnit('s').to_seconds() == 1
        assert dataset_info.TimeframeUnit('ms').to_seconds() == 1 / 1000
        assert dataset_info.TimeframeUnit().to_seconds() == 0

    def test_to_pandas_unit_conversion(self):
        assert dataset_info.TimeframeUnit('y').to_pandas_unit() == 'Y'
        assert dataset_info.TimeframeUnit('M').to_pandas_unit() == 'MS'
        assert dataset_info.TimeframeUnit('w').to_pandas_unit() == 'W'
        assert dataset_info.TimeframeUnit('d').to_pandas_unit() == 'D'
        assert dataset_info.TimeframeUnit('h').to_pandas_unit() == 'H'
        assert dataset_info.TimeframeUnit('m').to_pandas_unit() == 'T'
        assert dataset_info.TimeframeUnit('s').to_pandas_unit() == 'S'
        assert dataset_info.TimeframeUnit('ms').to_pandas_unit() == 'L'
        assert not dataset_info.TimeframeUnit().to_pandas_unit()

    def test_to_offset_unit_conversion(self):
        assert dataset_info.TimeframeUnit('y').to_offset_unit() == 'y'
        assert dataset_info.TimeframeUnit('M').to_offset_unit() == 'm'
        assert dataset_info.TimeframeUnit('w').to_offset_unit() == 'w'
        assert dataset_info.TimeframeUnit('d').to_offset_unit() == 'd'
        assert dataset_info.TimeframeUnit('h').to_offset_unit() == 'h'
        assert dataset_info.TimeframeUnit('m').to_offset_unit() == 'min'
        assert dataset_info.TimeframeUnit('s').to_offset_unit() == 's'
        assert dataset_info.TimeframeUnit('ms').to_offset_unit() == 'ms'
        assert not dataset_info.TimeframeUnit().to_offset_unit()

    def test_to_word_conversion(self):
        assert dataset_info.TimeframeUnit('y').to_word() == 'years'
        assert dataset_info.TimeframeUnit('M').to_word() == 'months'
        assert dataset_info.TimeframeUnit('w').to_word() == 'weeks'
        assert dataset_info.TimeframeUnit('d').to_word() == 'days'
        assert dataset_info.TimeframeUnit('h').to_word() == 'hours'
        assert dataset_info.TimeframeUnit('m').to_word() == 'minutes'
        assert dataset_info.TimeframeUnit('s').to_word() == 'seconds'
        assert dataset_info.TimeframeUnit('ms').to_word() == 'milliseconds'
        assert not dataset_info.TimeframeUnit().to_word()
