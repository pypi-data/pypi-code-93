"""Module containing extended base OHLCVFetcher classes."""

from datetime import datetime as datetime_lib
from inspect import isclass
from math import ceil
from operator import itemgetter
from typing import List
from typing import Union
from tempfile import NamedTemporaryFile

import ccxt
import pandas as pd

from trading.etl.ohlcv import OHLCV
from trading.etl.ohlcv import Timeframe


__all__ = [
    # Class exports
    "OHLCVFetcher"
]

# pylint: disable=W0221
class OHLCVFetcher(ccxt.Exchange):
    """Improved class implementation of CCXT Exchange.

    Currently, this extension is able to download the whole history OHLCV
    of a given currency pair.
    """

    def fetch_all_ohlcvs(self, symbol: str, timeframe: str) -> OHLCV:
        """Fetch all the candlesticks for a given exchange and symbol.

        The way this is done is we still use `fetch_ohlcv()` but we
        use a date before the creation of Bitcoin as the starting
        timestamp and the current timestamp as the ending timestamp.

        Arguments:
            symbol: Text symbol of the currency pair.
            timeframe: Timeframe of the candlestick data to fetch. Some
                examples of valid timeframe strings are `'2h'` for two
                hour, `'1d'` for one day, and `'1w'` for 1 week.

        Raises:
            ccxt.BadRequest: Raised for any errors while using CCXT to
                fetch exchange OHLCV data.

        Returns:
            A OHLCV dataframe representing the candlestick data fetched
            from the exchange. Each row contains six datapoints:
            the opening timestamp, the opening price, highest price,
            lowest price, closing price, and trading volume. Example:

            ```
               opening_timeframe  opening_price  ...  trading_volume
            0         2021-03-01       45134.11  ...    85086.111648
            1         2021-03-02       49595.76  ...    64221.062140
            2         2021-03-03       48436.61  ...    81035.913705
            3         2021-03-04       50349.37  ...    82649.716829
            4         2021-03-05       48374.09  ...    78192.496372
            5         2021-03-06       48746.81  ...    44399.234242
            6         2021-03-07       48882.20  ...    55235.028032
            ```
        """
        ohlcv_df = self.fetch_ohlcv(
            symbol,
            timeframe,
            starting_timestamp=1199030400000,
            ending_timestamp=self.milliseconds())

        # Remove the current date candle
        ohlcv_df.drop(ohlcv_df.tail(1).index, inplace=True)

        return ohlcv_df

    def fetch_ohlcv(self,
                    symbol: str,
                    timeframe: str,
                    starting_timestamp: Union[int, str],
                    ending_timestamp: Union[int, str],
                    max_retries: int = 3) -> OHLCV:

        """Fetches a set of currency OHLCV data from an exchange.

        Arguments:
            symbol: Text symbol of the currency pair.
            timeframe: Timeframe of the candlestick data to fetch. Some
                examples of valid timeframe strings are `'2h'` for two
                hour, `'1d'` for one day, and `'1w'` for 1 week.
            starting_timestamp: Starting timestamp of the data fetching
                process. The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            ending_timestamp: Ending timestamp of the data fetching
                process. The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            max_retries: The number of failures we can try to fetch the
                OHLCV until we give up on trying.

        Raises:
            ccxt.BadRequest: Raised for any errors while using CCXT to
                fetch exchange OHLCV data.

        Returns:
            A OHLCV dataframe representing the candlestick data fetched
            from the exchange. Each row contains six datapoints:
            the opening timestamp, the opening price, highest price,
            lowest price, closing price, and trading volume. Example:

            ```
               opening_timeframe  opening_price  ...  trading_volume
            0         2021-03-01       45134.11  ...    85086.111648
            1         2021-03-02       49595.76  ...    64221.062140
            2         2021-03-03       48436.61  ...    81035.913705
            3         2021-03-04       50349.37  ...    82649.716829
            4         2021-03-05       48374.09  ...    78192.496372
            5         2021-03-06       48746.81  ...    44399.234242
            6         2021-03-07       48882.20  ...    55235.028032
            ```
        """
        # Dynamically parse input timestamp
        starting_timestamp = self._convert_to_timestamp(starting_timestamp)
        ending_timestamp = self._convert_to_timestamp(ending_timestamp)

        # Make sure starting is before ending
        if starting_timestamp > ending_timestamp:
            print(
                'Swapping because starting is older than ending timestamp.')
            starting_timestamp, ending_timestamp = (
                ending_timestamp, starting_timestamp)

        # Convert timeframe into a duration in milliseconds
        timeframe_duration_in_ms = Timeframe(timeframe).get_duration(unit='ms')

        # Compute for the estimated candlestick data count
        candles_count = ending_timestamp - starting_timestamp
        candles_count = ceil(candles_count / timeframe_duration_in_ms)

        # Compute for the limit per API call
        limit = min(900, candles_count)

        # Track resulting OHLCV data
        ohlcv_list = []

        log_msg = f'Fetching {symbol} ({timeframe}) candles '
        log_msg += f'from {self.name}, ranging from '
        log_msg += f'{self.iso8601(starting_timestamp)} to '
        log_msg += f'{self.iso8601(ending_timestamp)}'
        print(log_msg)

        # Variable trackers for every iteration
        # that should be initialized before the loop
        i = 0
        is_done = False
        num_retries = 0
        current_starting_timestamp = ending_timestamp
        current_ending_timestamp = ending_timestamp

        while not is_done:
            current_limit = min(limit, (candles_count - len(ohlcv_list)))
            timedelta = current_limit * timeframe_duration_in_ms
            current_starting_timestamp = current_ending_timestamp - timedelta

            # If fetching fails, retry upto max_retries-times
            try:
                ohlcv = super().fetch_ohlcv(
                    symbol,
                    timeframe=timeframe,
                    since=int(current_starting_timestamp),
                    limit=current_limit)

                log_msg = f'Iteration {i}: '
                log_msg += f'Fetched  {len(ohlcv)} {symbol} '
                log_msg += f'({timeframe}) candles from {self.name}, '
                log_msg += 'ranging from '
                log_msg += f'{self.iso8601(int(current_starting_timestamp))} '
                log_msg += 'to '
                log_msg += f'{self.iso8601(int(current_ending_timestamp))}'
                print(log_msg)

                # Check if we're done
                is_done |= current_starting_timestamp <= starting_timestamp
                is_done |= len(ohlcv) == 0

                # Update current ending timestamp
                current_ending_timestamp = current_starting_timestamp

                # Add current OHLCV to list and reset number
                # of tries if we reach this point
                ohlcv_list += ohlcv
                num_retries = 0

                # Last final done check, duplicate entries
                is_done |= self._does_list_have_duplicates(ohlcv_list)

            except ccxt.BadRequest:
                num_retries += 1
                if num_retries > max_retries:
                    print('Error retry limit reached. Aborting...')
                    raise
                continue

            # Incremenent iteration counter
            i += 1

        # Populate the OHLCV data and add metadata
        ohlcv_df = OHLCV(ohlcv_list)
        ohlcv_df.timeframe = timeframe
        ohlcv_df.metadata.exchange = self.name
        ohlcv_df.metadata.symbol = symbol

        # Remove duplicate timestamps
        ohlcv_df.drop_duplicates(
            subset=[ohlcv_df.columns[0]], keep='first', inplace=True)

        # Re-align number index, just because
        ohlcv_df.reset_index(drop=True)

        # Status update
        log_msg = f'Fetched {len(ohlcv_df.index)} {symbol} '
        log_msg += f'({timeframe}) candles from {self.name}, '
        log_msg += 'ranging from '
        log_msg += f'{self.iso8601(starting_timestamp)} to '
        log_msg += f'{self.iso8601(ending_timestamp)}'
        print(log_msg)

        return ohlcv_df

    @staticmethod
    def _convert_to_timestamp(datetime: Union[str, int]) -> Union[int, None]:
        """Converts a valid datetime-like string into a millisecond timestamp.

        Arguments:
            datetime: Can be a string indicating a valid datetime-like
                string or a number indicating the timestamp in milliseconds.

        Returns:
            If the `datetime` is a valid datetime-like string or is
            already a millisecond timestamp, then the return is a millisecond
            timestamp as well. Other than that, `None` is returned.
        """
        if not datetime:
            return None

        if isinstance(datetime, (int, float)):
            return int(datetime)

        # Parse it dynamically then multiply to 1000 to convert to milliseconds
        parsed_timestamp = pd.to_datetime(str(datetime))
        parsed_timestamp = int(parsed_timestamp.timestamp() * 1000)

        return parsed_timestamp

    @staticmethod
    def _does_list_have_duplicates(llist: list) -> bool:
        """Checks if a given list contains any duplicates."""
        stringified_list = [str(e) for e in llist]
        if len(stringified_list) == len(set(stringified_list)):
            return False
        return True


# Dynamic recreation of existing constructors
# but apply better OHLCVFetcher class
for attr_name in dir(ccxt):
    attr = getattr(ccxt, attr_name)

    # Ignore any non-class attributes
    if not isclass(attr):
        continue

    # Ignore non-OHLCVFetcher subclass
    if not issubclass(attr, ccxt.Exchange) or attr == ccxt.Exchange:
        continue

    # New class name
    class_name = attr_name[0].upper() + attr_name[1:]
    globals()[class_name] = type(class_name, (OHLCVFetcher, attr), {})
    __all__.append(class_name)
