"""Module containing the OHLCV class."""

from __future__ import annotations

from collections import abc
from typing import Any
import datetime as dtlib
import pathlib
import re
import unicodedata

import datetimerange as dtrangelib
import numpy as np
import pandas as pd

from trading.datasets import dataset_info
from trading.datasets import exchange as exchangelib
from trading.datasets.utils import cache_utils
from trading.datasets.utils import datetime_utils
from trading.datasets.utils import generic_utils
from trading.datasets.utils import string_utils


__all__ = [
    # Class exports
    'OHLCV',
]


class OHLCVSeries(pd.Series):
    """Makes sure that slicing OHLCV data returns a new OHLCV as well."""

    @property
    def _constructor(self):  # pragma: no cover
        return OHLCVSeries

    @property
    def _constructor_expanddim(self):  # pragma: no cover
        return OHLCV


class OHLCV(pd.DataFrame):
    """OHLCV (Opening, Highest, Lowest, Closing, Volume) dataframe."""

    _COLUMN_RESAMPLE_FUNCTIONS = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
    }

    _DEFAULT_TIMESTAMP_COLUMN = 'datetime'
    _DEFAULT_COLUMNS = [_DEFAULT_TIMESTAMP_COLUMN]
    _DEFAULT_COLUMNS += list(_COLUMN_RESAMPLE_FUNCTIONS.keys())

    # Allow transfer of data in new OHLCV frame
    _subclass_metadata = ['metadata', 'offset', 'timeframe']
    _metadata = pd.DataFrame._metadata + _subclass_metadata

    def __init__(
        self,
        data: Any = None,
        index: abc.Collection | None = None,
        columns: abc.Collection | None = None,
        dtype: str | np.dtype | None = None,
        copy: bool = False):

        # Initialize parent DataFrame class using standard column and dtype
        super().__init__(
            data=data,
            index=index,
            columns=columns,
            dtype=dtype,
            copy=copy)

        self.metadata = dataset_info.OHLCVMetadata()
        self.timeframe = None
        self.offset = None

    @property
    def _constructor(self):  # pragma: no cover
        """Required property for DataFrame when subclassing DataFrame."""
        return self.__class__

    @property
    def _constructor_sliced(self):
        """Required property for Series when subclassing DataFrame."""
        return OHLCVSeries

    @property
    def timeframe(self):
        """Returns the detected timeframe of the OHLCV instance."""

        # If timeframe is set before, return that
        if self._timeframe:
            return self._timeframe

        # Otherwise, automagically get the timeframe of the dataset
        # Don't even try if the there are less than two rows
        if len(self.index) < 2:
            return None

        # We can't really detect the timeframe if the index is not
        # of type DateTimeIndex
        if not isinstance(self.index, pd.DatetimeIndex):
            return None

        # Get the average seconds difference between row timestamps
        average_timedelta = self.index.to_series().diff()
        average_timedelta = int(average_timedelta.dt.total_seconds().mean())

        # Mapping of seconds to
        seconds_to_unit_mapping = (
            dataset_info.TimeframeUnit.SECONDS_TO_UNIT_MAPPING)

        for duration_in_seconds, unit in seconds_to_unit_mapping.items():
            # Ignore second timeframe if its more than a minute
            if duration_in_seconds == 1 and average_timedelta > 60:
                continue

            # Check if average timedelta is divisible by any of the conversions
            if average_timedelta % duration_in_seconds <= 0:
                timeframe = f'{average_timedelta // duration_in_seconds}{unit}'
                self._timeframe = dataset_info.Timeframe(timeframe)
                return self._timeframe

        # No more ways to detect the timeframe, just return None
        return None

    @timeframe.setter
    def timeframe(self, value: dataset_info.Timeframe | str):
        self._timeframe = dataset_info.Timeframe(value)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value: dataset_info.Timeframe | str):
        self._offset = dataset_info.Timeframe(value)

    def info(self, **kwargs):  # pylint: disable=arguments-differ  # pragma: no cover
        super().info(**kwargs)

        print(f'metadata: {self.metadata!r}')
        print(f'timeframe: {self.timeframe!r}')
        print(f'offset: {self.offset!r}')

    def indexify(self, index_column: str | None = None):
        """Uses the default datetime column to use as index."""
        index_column = index_column or self._DEFAULT_TIMESTAMP_COLUMN

        # Make sure that the index column that we want is in the dataframe
        if index_column not in self.columns:
            raise errors.OHLCVReindexError(index_column)

        self[index_column] = datetime_utils.get_datetime(self[index_column])
        self.set_index(index_column, inplace=True)
        self.sort_index(inplace=True)

    @classmethod
    def from_exchange(
        cls,
        exchange_name: str,
        symbol: str,
        timeframe: dataset_info.Timeframe | str,
        start: dtlib.datetime | str | int | None = None,
        end: dtlib.datetime | str | int | None = None,
        offset: dataset_info.Timeframe | str | None = None,
        use_cache: bool = True,
    ) -> OHLCV:

        """Returns an instance of an OHLCV based on the given parameters.

        Arguments:
            exchange_name: Name of the crypto asset exchange.
            symbol: Ticker symbol of the crypto asset.
            timeframe: Timeframe of the candlestick data to fetch. Some
                examples of valid timeframe strings are `'2h'` for two
                hour, `'1d'` for one day, and `'1w'` for 1 week.
            start: Starting datetime of the data to be fetched.
                The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            end: Ending timestamp of the data to be fetched.
                The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            offset: Offset to the timeframe of the candlestick data to be
                fetch. Some examples of valid offset strings are `'5n'`
                for five minutes, `'2h'` for two hour, `'1d'` for one day,
                and `'1w'` for 1 week.
            use_cache: An overriding variable to forcefully disable the
                use of the caching system. Default value is `True`.

        Returns:
            An instance of `OHLCV()` containing the data of the
            given input parameters.
        """

        # Validate and convert the exchange name into an exchange instance
        exchange = exchangelib.get(exchange_name)()

        # Validate and standardize the symbol before using it
        symbol = exchange.get_valid_symbol(symbol)

        # Standardize the timeframe and offset before using it
        timeframe = dataset_info.Timeframe(timeframe)
        offset = dataset_info.Timeframe(offset)

        # Make sure that the start and end times are valid
        start, end = exchange.get_valid_start_end(start, end, timeframe)

        # Conditional timeframe for the download
        if offset and offset.get_duration() < timeframe.get_duration():
            fetch_timeframe = dataset_info.Timeframe(
                interval=1, unit=offset.unit)
        else:
            fetch_timeframe = dataset_info.Timeframe(
                interval=1, unit=timeframe.unit)

        pbar_target = (
            datetime_utils.get_milliseconds(end) -
            datetime_utils.get_milliseconds(start))

        # Update user of OHLCV download progress
        print(f'Downloading {exchange.name} {symbol}-{timeframe}-{offset} '
              f'from {start} to {end}...')
        pbar = generic_utils.Progbar(pbar_target)

        # Generate cache filepath and load the file itself
        cache_filepath = cls._generate_cache_filepath(
            exchange.name, symbol, fetch_timeframe, extension='parquet')

        # Did we ever download any new data timeranges
        has_new_data = False

        if cache_filepath.is_file() and use_cache:
            ohlcv = cls.from_parquet(cache_filepath)

            cache_start = ohlcv.index[0]
            cache_end = ohlcv.index[-1]

            # Get the timerange of the cache and the actual relevant timeranges
            input_timerange = dtrangelib.DateTimeRange(start, end)
            cache_timerange = dtrangelib.DateTimeRange(cache_start, cache_end)

            try:
                cached_timerange = input_timerange.intersection(
                    cache_timerange)

                fetch_timeranges = input_timerange.subtract(cached_timerange)

                # Update progress
                cached_start = cached_timerange.start_datetime
                cached_end = cached_timerange.end_datetime
                pbar.update(
                    datetime_utils.get_milliseconds(cached_end) -
                    datetime_utils.get_milliseconds(cached_start))

            # Cache doesn't catch the wanted input timerange
            except TypeError:
                fetch_timeranges = [dtrangelib.DateTimeRange(start, end)]

        else:
            ohlcv = cls()
            fetch_timeranges = [dtrangelib.DateTimeRange(start, end)]

        # Actual downloading loop for each un-chached timerange
        list_of_current_ohlcvs = [ohlcv]
        for timerange in fetch_timeranges:
            current_raw_ohlcv = exchange.get_ohlcv(
                symbol, fetch_timeframe,
                timerange.start_datetime,
                timerange.end_datetime,
                include_latest=False,
                pbar=pbar)

            # Remember if we ever do download a new dataset
            # this is used later if we really do need to update
            # the copy of the cache or not
            has_new_data = has_new_data or len(current_raw_ohlcv) > 1

            # Make sure the index is a datetime type
            current_ohlcv = cls(current_raw_ohlcv)
            if not current_ohlcv.empty:
                current_ohlcv.columns = cls._DEFAULT_COLUMNS
                current_ohlcv.indexify()

                list_of_current_ohlcvs.append(current_ohlcv)

        # Combine all the downloaded OHLCVs
        ohlcv = pd.concat(list_of_current_ohlcvs)

        # Make sure the total target is added to the progress bar
        pbar.update(pbar_target)

        are_there_duplicates = ohlcv.index.duplicated(keep='last')
        if any(are_there_duplicates):
            ohlcv = ohlcv[~are_there_duplicates]
        ohlcv = ohlcv.sort_index()

        # Save cache to file if it contains any row and if its updated
        if not ohlcv[start:end].empty and has_new_data and use_cache:
            cache_filepath.parent.mkdir(exist_ok=True)
            ohlcv.to_parquet(cache_filepath)

        # Resample if needed
        if timeframe != ohlcv.timeframe:
            # WARNING! Resampling doesn't conserve added attributes
            # to subclassed dataframes so keep that in mind
            ohlcv = ohlcv.resample(
                timeframe.to_pandas_timeframe(),
                offset=offset.to_offset_timeframe())
            ohlcv = ohlcv.agg(cls._COLUMN_RESAMPLE_FUNCTIONS)

        # Limit the end of the OHLCV to what the user wanted
        ohlcv = ohlcv[start:end]

        # Remove the first row if the timeframe and the offset is the same
        if timeframe == offset:
            ohlcv = ohlcv.iloc[1:, :]

        # Forward fill NaN values
        ohlcv = ohlcv.fillna(method='ffill')

        # Add metadata to OHLCV
        ohlcv.metadata.exchange = exchange_name
        ohlcv.metadata.symbol = symbol
        ohlcv.offset = offset

        return ohlcv

    @classmethod
    def from_csv(cls, file: pathlib.Path | str, **kwargs) -> OHLCV:  # pragma: no cover
        """Returns an instance of an OHLCV based on the given parameters.

        Arguments:
            file: The file path of the CSV file to be opened.
            kwargs: Any keyword argument that we want to pass down to
                the original Pandas `read_csv()` function.

        Returns:
            An instance of `OHLCV` containing the data of the input CSV file.
        """
        file = pathlib.Path(file)
        ohlcv = cls(pd.read_csv(file, **kwargs), columns=cls._DEFAULT_COLUMNS)
        ohlcv.indexify()

        return ohlcv

    @classmethod
    def from_parquet(cls, file: pathlib.Path | str, **kwargs) -> OHLCV:  # pragma: no cover
        """Returns an instance of an OHLCV based on the given parameters.

        Arguments:
            file: The file path of the parquet file to be opened.
            kwargs: Any keyword argument that we want to pass down to
                the original Pandas `read_parquet()` function.

        Returns:
            An instance of `OHLCV` containing the data of the input CSV file.
        """
        file = pathlib.Path(file)
        return cls(pd.read_parquet(file, **kwargs))

    @staticmethod
    def _generate_cache_filepath(
        exchange_name: str,
        symbol: str,
        timeframe: dataset_info.Timeframe,
        extension: str = 'parquet'
    ) -> pathlib.Path:

        """Returns the cache filepath given the OHLCV metadata as parameters.

        Arguments:
            exchange_name: Name of the crypto asset exchange.
            symbol: Ticker symbol of the crypto asset.
            timeframe: The period or timeframe of the OHLCV data.
            extension: File extension that we want the cache in.

        Returns:
            The generated filepath of the OHLCV cache file.

        """
        valid_symbol = string_utils.special_chars_to_words(symbol)
        raw_filename = f'{exchange_name}_{valid_symbol}_{timeframe}'

        # ASCII Validate the raw filename
        valid_filename = unicodedata.normalize('NFKD', raw_filename)
        valid_filename = valid_filename.encode('ascii', 'ignore')
        valid_filename = valid_filename.decode('ascii')

        # Remove special characters and spaces
        valid_filename = re.sub(r'[^\w\s\[\]-]', '-', valid_filename)
        valid_filename = re.sub(r'[-\s]+', '-', valid_filename).strip('-_')

        # Remove invalid extension characters
        valid_extension = '.' + re.sub(r'[\W_]+', '', extension)

        cache_filename = f'{valid_filename}.ohlcv{valid_extension}'
        return cache_utils.cache_path().joinpath(cache_filename)
