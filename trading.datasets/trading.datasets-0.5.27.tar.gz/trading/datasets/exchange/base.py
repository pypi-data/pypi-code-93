"""Module containing base exchange classes."""

from __future__ import annotations

import datetime as dtlib
import math
import time

from fuzzywuzzy import process as fuzzy_match
import ccxt
import pytz

from trading.datasets import dataset_info
from trading.datasets import errors
from trading.datasets.utils import datetime_utils
from trading.datasets.utils import generic_utils


__all__ = [
    # Class exports
    'Exchange',
]


class Exchange(ccxt.Exchange):
    """Improved class implementation of the CCXT Exchange.

    This is used in conjuction with any of the specific exchanges
    in CCXT. So if we want to use this base Exchange class as a parent
    class, we would also need to add the specific exchange from
    CCXT as a parent class.

    For example:
    ```
    # Create a new exchange class. We need to use two
    # classes as parents, one from CCXT and the other
    # one is our base Exchange class.
    class NewBinanceExchange(Exchange, ccxt.binance):
        ...
    ```
    """

    # Must be overriden by subclasses to
    # maximize each individual exchange's limit
    FETCH_OHLCV_LIMIT = 100

    def __init__(self, config: dict | None = None):
        # Make sure config is an empty dictionary if its invalid
        if not config:
            config = {}

        # Force rate limit into the config
        config.update({'enableRateLimit': True})

        super().__init__(config)

        # Make sure markets are already loaded when instance is created
        # but only do it for subclasses of Exchange, not Exchange itself
        if issubclass(type(self), Exchange) and type(self) != Exchange:
            self.load_markets()  # pragma: no cover

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: dataset_info.Timeframe | str,
        start: dtlib.datetime | str | int | None = None,
        end: dtlib.datetime | str | int | None = None,
        include_latest: bool = True,
        pbar: generic_utils.Progbar | None = None,
    ) -> list[list[int | float]]:

        """Fetches the OHLCV data from an exchange.

        Arguments:
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
            include_latest: If the `include_latest` variable is set to
                `True`, the latest OHLCV data is not returned since it
                is not finished yet. If set to `False`, then the
                unfinished data at the time `get_ohlcv()` was called
                will be returned.
            pbar: Optional `ProgBar` instance input. Used for combining
                multiple calls of `get_ohlcv()`.

        Raises:
            OHLCVFetchError: Raised for any errors that causes the
                fetching of OHLCV to fail.

        Returns:
            A list of list representing the candlestick data fetched
            from the exchange. Each row/inner list contains six
            datapoints: the opening timestamp in milliseconds, the
            opening price, highest price, lowest price, closing price,
            and trading volume.

            Example:

            ```
            [
                [1546128000000, 369.7, 390.5 365.9, 380.9, 33222.36],
                [1546214400000, 380.1, 381.0 363.3, 370.9, 29991.77],
                [1546300800000, 370.2, 381.1 364.0, 379.1, 23741.68],
            ]
            ```
        """

        # Validate and standardize the symbol before using it
        symbol = self.get_valid_symbol(symbol)

        # Standardize the timeframe before using it
        timeframe = dataset_info.Timeframe(timeframe)

        # Make sure that the start and end times are valid
        start, end = self.get_valid_start_end(
            start, end, timeframe, include_latest=include_latest)

        # Create millisecond versions of the start and end times
        start_ms = datetime_utils.get_milliseconds(start)
        end_ms = datetime_utils.get_milliseconds(end)

        # Keep the original starting point since start_ms is modified
        # every iteration in the main loop of the downloading process
        orig_start_ms = start_ms

        # Inform user of OHLCV download but don't create a new progress
        # bar if one is passed through the input parameters
        pbar_target = end_ms - start_ms
        if not(pbar and isinstance(pbar, generic_utils.Progbar)):
            print(f'Downloading {self.name} {symbol}-{timeframe}-0 '
                  f'from {start} to {end}...')
            pbar = generic_utils.Progbar(pbar_target)
            orig_pbar_progress = 0
        else:
            orig_pbar_progress = pbar.progress

        ohlcvs = []
        error_counter = 0
        while True:
            try:
                limit = (end_ms - orig_start_ms) / timeframe.get_duration()
                limit = self._get_valid_limit(limit)

                # Run CCXT's internal OHLCV fetch function
                # force an empty list if the limit passed is zero
                if limit > 0:

                    # Generate the API parameters for CCXT's original
                    # `fetch_ohlcv()` function
                    fetch_ohlcv_params = self._generate_fetch_ohlcv_params(
                        timeframe,
                        datetime_utils.get_datetime(start_ms),
                        datetime_utils.get_datetime(end_ms),
                        limit)

                    current_raw_ohlcv = self.fetch_ohlcv(
                        symbol,
                        str(timeframe),
                        limit=limit,
                        params=fetch_ohlcv_params)

                    # We want the oldest candle at the first index
                    current_raw_ohlcv.sort(key=lambda e: e[0])

                else:
                    current_raw_ohlcv = []

                if len(current_raw_ohlcv) > 0:
                    # Update the starting and ending timestamps (ms)
                    end_ms = current_raw_ohlcv[0][0] - 1
                    start_ms = end_ms - (
                        timeframe.get_duration() * self.FETCH_OHLCV_LIMIT)

                    # Adjust the starting time to the original one if it
                    # passes below it but the end time is still over it
                    if start_ms < orig_start_ms < end_ms:
                        start_ms = orig_start_ms

                    # Add the current raw OHLCV to the total OHLCV list
                    ohlcvs += current_raw_ohlcv
                    pbar.add(abs(
                        current_raw_ohlcv[0][0] -
                        current_raw_ohlcv[-1][0]))

                # No OHLCV was downloaded, we're done
                else:
                    break

            except (
                ccxt.ExchangeError,
                ccxt.AuthenticationError,
                ccxt.ExchangeNotAvailable,
                ccxt.RequestTimeout
            ) as err:

                # Exit the while loop if we had a lot of errors
                error_counter += 1
                if error_counter > 5:
                    raise errors.OHLCVFetchError(
                        'Unable to load the dataset.') from err

                # Retry after 30 seconds
                time.sleep(30)

        # Make sure the total target is added to the progress bar
        pbar.update(orig_pbar_progress + pbar_target)

        # Sort final OHLCV list just to be sure
        ohlcvs.sort(key=lambda e: e[0])

        return ohlcvs

    def _generate_fetch_ohlcv_params(
        self,
        timeframe: dataset_info.Timeframe,
        start: dtlib.datetime,
        end: dtlib.datetime,
        limit: int,
    ) -> dict:

        raise NotImplementedError

    def _get_valid_limit(self, limit: int) -> int:
        # Make sure the limit is a number and is valid
        if not limit:
            limit = self.FETCH_OHLCV_LIMIT

        # Set some restrictions to the limit value. We apply `ceil`
        # to the Exchange's limit to include the actual starting date
        # into the return of the original `fetch_ohlcv()` function.
        return max(0, min(math.ceil(limit), self.FETCH_OHLCV_LIMIT))

    def get_valid_start_end(
        self,
        start: dtlib.datetime | str | int | None,
        end: dtlib.datetime | str | int | None,
        timeframe: dataset_info.Timeframe,
        include_latest: bool = True,
    ) -> tuple[dtlib.datetime, dtlib.datetime]:

        """Validates and fills up the start and end times.

        Since we want the user to be able to readily use
        the `get_ohlcv()` without thinking much about this small detail,
        we automatically fill up the starting and end timestamps
        based on the parameters provided. Here are the different
        fill up cases:

        * If `start` and `end` are not provided, `end` is assigned the
          latest date and `start` is `end` minus the limit of one fetch
          based on the indicated exchange.
        * If either `start` and `end` are not provided but the other one
          is, we just add or subtract the same fetch limit to compute
          for `end` or `start`.
        * Lastly, if both are provided by the user, we use those without
          any other processing.

        Arguments:
            start: Starting datetime of the data to be fetched.
                The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            end: Ending timestamp of the data to be fetched.
                The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            timeframe: Timeframe of the candlestick data to fetch. Some
                examples of valid timeframe strings are `'2h'` for two
                hour, `'1d'` for one day, and `'1w'` for 1 week.
            include_latest: If the `include_latest` variable is set to
                `True`, the latest OHLCV data is not returned since it
                is not finished yet. If set to `False`, then the
                unfinished data at the time `get_ohlcv()` was called
                will be returned.

        Returns:
            A tuple containing the validated start and ending datetimes.
        """

        start = datetime_utils.get_datetime(start)
        end = datetime_utils.get_datetime(end)
        now = dtlib.datetime.utcnow().replace(tzinfo=pytz.utc)

        # Create a time adjustment variable to dynamically determine
        # the start or end times if ever one of them or both of them
        # are missing or invalid values.
        time_adjustment = timeframe.to_timedelta() * self.FETCH_OHLCV_LIMIT

        if not start and end:
            start = end - time_adjustment
        elif start and not end:
            end = start + time_adjustment
            if end > now:
                end = now
        elif not start and not end:
            end = now
            start = end - time_adjustment

        if not include_latest:
            # Get the time now to use as reference for the
            # removal of the current candle
            now = now

            # If the end date is not less than the threshold
            # then don't include it, subtract timeframe from end
            threshold = now - timeframe.to_timedelta()
            if end >= threshold:
                end -= timeframe.to_timedelta()

        return start, end

    def get_valid_symbol(self, symbol: str) -> str:
        valid_symbol, match_score = fuzzy_match.extractOne(
            str(symbol), self.markets.keys())

        # Raise an error if the exchange name is unrecognized or invalid
        if not symbol or match_score < 55:
            raise errors.UnknownSymbolError(symbol)

        return valid_symbol
