# coding: utf8

__all__ = ["StreamingPrices"]

import asyncio

from pandas import DataFrame
from refinitiv.dataplatform.content.streaming.streamingprice import StreamingPrice
from refinitiv.dataplatform.delivery.stream import StreamState, Openable
from refinitiv.dataplatform.core.log_reporter import _LogReporter
from refinitiv.dataplatform.errors import StreamingPricesError


class StreamingPrices(Openable, _LogReporter):
    """
    Open a streaming price subscription.

    Parameters
    ----------
    universe: string, list[string]
        List of RICs to subscribe.

    service: string
        Specified the service to subscribe on.
        Default: None

    fields: string or list[string]
        Specified the fields to retrieve.
        Default: None

    on_refresh: callable object (streaming_prices, instrument_name, message)
        Called when a stream on instrument_name was opened successfully or when the stream is refreshed by the server.
        This callback is called with the reference to the streaming_prices object, the instrument name and the instrument full image.
        Default: None

    on_update: callable object (streaming_prices, instrument_name, message)
        Called when an update is received for a instrument_name.
        This callback is called with the reference to the streaming_prices object, the instrument name and the instrument update.
        Default: None

    on_status: callable object (streaming_prices, instrument_name, status)
        Called when a status is received for a instrument_name.
        This callback is called with the reference to the streaming_prices object, the instrument name and the instrument status.
        Default: None

    on_complete: callable object  (streaming_prices, instrument_name)
        Called when all subscriptions are completed.
        This callback is called with the reference to the streaming_prices object.
        Default: None

    Raises
    ------
    Exception
        If request fails.

    Examples
    --------
    >> import eikon as ek
    >> fx = ek.StreamingPrices(['EUR=', 'GBP='])
    >> fx.open()
    >> bid_eur = fx['EUR']['BID']
    >> ask_eur = fx['EUR']['ASK']
    >>
    >> def on_update(streams, instrument, msg):
            ... print(msg)
    >> subscription = ek.StreamingPrices(['VOD.L', 'EUR=', 'PEUP.PA', 'IBM.N'],
            ... ['DSPLY_NAME', 'BID', 'ASK'],
            ... on_update=on_update)
    >> subscription.open()
    {"EUR=":{"DSPLY_NAME":"RBS          LON","BID":1.1221,"ASK":1.1224}}
    {"PEUP.PA":{"DSPLY_NAME":"PEUGEOT","BID":15.145,"ASK":15.155}}
    {"IBM.N":{"DSPLY_NAME":"INTL BUS MACHINE","BID":"","ASK":""}}
    ...
    """

    class Params(object):
        def __init__(self, universe, fields):
            self._universe = universe
            self._fields = fields

        @property
        def universe(self):
            return self._universe

        @property
        def fields(self):
            return self._fields

    class StreamingPricesIterator:
        """ StreamingPrices Iterator class """

        def __init__(self, streaming_prices):
            self._streaming_prices = streaming_prices
            self._index = 0

        def __next__(self):
            """" Return the next streaming item from streaming price list """
            if self._index < len(self._streaming_prices.params.universe):
                result = self._streaming_prices[
                    self._streaming_prices.params.universe[self._index]
                ]
                self._index += 1
                return result
            raise StopIteration()

    def __init__(
        self,
        universe,
        session=None,
        fields=None,
        service=None,
        api=None,
        on_refresh=None,
        on_status=None,
        on_update=None,
        on_complete=None,
    ):

        is_valid = False
        if isinstance(universe, str):
            universe = [universe]
            is_valid = True

        elif isinstance(universe, list) and all(
            isinstance(name, str) for name in universe
        ):
            is_valid = True

        if not is_valid:
            raise StreamingPricesError(
                -1, "StreamingPrices: universe must be a list of strings"
            )

        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session or DefaultSession.get_default_session()

        super().__init__(self, loop=session._loop, logger=session)

        self._fields = fields or []
        self._session = session
        self._service = service

        self.params = StreamingPrices.Params(universe=universe, fields=self._fields)

        self._streaming_prices_by_name = {
            name: StreamingPrice(
                session=self._session,
                name=name,
                fields=self._fields,
                service=self._service,
                api=api,
                on_refresh=self._on_refresh,
                on_update=self._on_update,
                on_status=self._on_status,
                on_complete=self._on_complete,
            )
            for name in universe
        }

        self._on_refresh_cb = on_refresh
        self._on_status_cb = on_status
        self._on_update_cb = on_update
        self._on_complete_cb = on_complete

        self._state = StreamState.Closed

        #   set universe of on_complete
        self._on_complete_set = None

    # region Access to StreamingPrices as a dict
    ###################################################
    #  Access to StreamingPrices as a dict            #
    ###################################################
    def keys(self):
        return self._streaming_prices_by_name.keys()

    def values(self):
        return self._streaming_prices_by_name.values()

    def items(self):
        return self._streaming_prices_by_name.items()

    # endregion

    # region Make StreamingPrices iterable
    ###################################################
    #  Make StreamingPrices iterable                  #
    ###################################################
    def __iter__(self):
        return StreamingPrices.StreamingPricesIterator(self)

    def __getitem__(self, name):
        if name in self.params.universe:
            return self._streaming_prices_by_name[name]
        else:
            raise KeyError(f"{name} not in StreamingPrices universe")

    def __len__(self):
        return len(self.params.universe)

    # endregion

    def get_snapshot(self, universe=None, fields=None, convert=True):
        """
        Returns a Dataframe filled with snapshot values for a list of instrument names and a list of fields.

        Parameters
        ----------
        universe: list of strings
            List of instruments to request snapshot data on.

        fields: list of strings
            List of fields to request.

        convert: boolean
            If True, force numeric conversion for all values.

        Returns
        -------
            pandas.DataFrame

            pandas.DataFrame content:
                - columns : instrument and fieled names
                - rows : instrument name and field values

        Raises
        ------
            Exception
                If request fails or if server returns an error

            ValueError
                If a parameter type or value is wrong

        Examples
        --------
        >>> import refinitiv.dataplatform as rdp
        >>> rdp.open_desktop_session('set your app key here')
        >>> streaming_prices = rdp.StreamingPrices(instruments=["MSFT.O", "GOOG.O", "IBM.N"], fields=["BID", "ASK", "OPEN_PRC"])
        >>> data = streaming_prices.get_snapshot(["MSFT.O", "GOOG.O"], ["BID", "ASK"])
        >>> data
              Instrument    BID        ASK
        0     MSFT.O        150.9000   150.9500
        1     GOOG.O        1323.9000  1327.7900
        """

        if universe:
            for name in universe:
                if name not in self.params.universe:
                    raise StreamingPricesError(
                        -1,
                        f"Instrument {name} was not requested : {self.params.universe}",
                    )

        if fields:
            for field in fields:
                if field not in self.params.fields:
                    raise StreamingPricesError(
                        -1, f"Field {field} was not requested : {self.params.fields}"
                    )

        _universe = universe if universe else self.params.universe
        _all_fields_value = {
            name: self._streaming_prices_by_name[name].get_fields(fields)
            if name in self._streaming_prices_by_name
            else None
            for name in _universe
        }
        _fields = []

        if not fields:
            for field_values in _all_fields_value.values():
                if field_values:
                    _fields.extend(
                        field for field in field_values.keys() if field not in _fields
                    )
        else:
            _fields = fields

        _df_source = {
            f: [
                _all_fields_value[name][f] if _all_fields_value[name].get(f) else None
                for name in _universe
            ]
            for f in _fields
        }
        _price_dataframe = DataFrame(_df_source, columns=_fields)

        if convert:
            # _price_dataframe = _price_dataframe.apply(to_numeric, errors='ignore')
            if not _price_dataframe.empty:
                _price_dataframe = _price_dataframe.convert_dtypes()

        _price_dataframe.insert(0, "Instrument", _universe)

        return _price_dataframe

    def _do_pause(self):
        results = [streaming_price.pause() for streaming_price in self.values()]
        assert all([r is StreamState.Pause for r in results])

    def _do_resume(self):
        results = [streaming_price.resume() for streaming_price in self.values()]
        assert all([r is not StreamState.Pause for r in results])

    async def _do_open_async(self, with_updates=True):
        """
        Open asynchronously the streaming price
        """
        self._session.debug(
            f"StreamingPrices : open streaming on {self.params.universe}"
        )
        #   reset the on_complete set
        self._on_complete_set = set()
        streaming_prices_iterator = iter(self.values())
        stream_opens_socket = next(streaming_prices_iterator)
        await stream_opens_socket.open_async(with_updates=with_updates)
        await asyncio.gather(
            *[
                item.open_async(with_updates=with_updates)
                for item in streaming_prices_iterator
            ]
        )
        self._session.debug(
            f"StreamingPrices : start asynchronously streaming on {self.params.universe} done"
        )

        #   change state to open after all streaming are open.
        self.state = StreamState.Open

        return True

    async def _do_close_async(self):
        self._session.debug(
            f"StreamingPrices : close streaming on {str(self.params.universe)}"
        )
        for streaming_price in self.values():
            streaming_price.close()

        #   change state to close after all streaming are closed
        self.state = StreamState.Closed

    # region Messages from streaming price
    #########################################
    # Messages from streaming price         #
    #########################################
    def _on_refresh(self, streaming_price, message):

        if self.is_pause():
            return

        if self._on_refresh_cb:
            self._session.debug("StreamingPrices : call on_refresh callback")
            self._session._loop.call_soon_threadsafe(
                self._on_refresh_cb, self, streaming_price.name, message
            )

    def _on_status(self, streaming_price, status):

        if self.is_pause():
            return

        if self._on_status_cb:
            self._session.debug("StreamingPrices : call on_status callback")
            self._session._loop.call_soon_threadsafe(
                self._on_status_cb, self, streaming_price.name, status
            )

        #   check for closed stream when status "Closed", "ClosedRecover", "NonStreaming" or "Redirect"
        if (
            streaming_price.state == StreamState.Closed
            and streaming_price.name not in self._on_complete_set
        ):
            #   this stream has been closed, so it means completed also
            self._on_complete(streaming_price)

    def _on_update(self, streaming_price, update):

        if self.is_pause():
            return

        if self._on_update_cb:
            self._session.debug("StreamingPrices : call on_update callback")
            self._session._loop.call_soon_threadsafe(
                self._on_update_cb, self, streaming_price.name, update
            )

    def _on_complete(self, streaming_price):
        assert self._on_complete_set is not None

        #   check for update completed set
        if streaming_price.name not in self._on_complete_set:
            #   update the stream to be in complete list
            self._on_complete_set.update(
                [
                    streaming_price.name,
                ]
            )

            #   after update subscribed RIC completed,
            #       check all RIC is completed or not, so on_complete is ready to call or not?
            if self._on_complete_set == set(self.params.universe):
                if self.is_pause():
                    return

                if self._on_complete_cb:
                    self._session.debug("StreamingPrices : call on_complete callback")
                    self._session._loop.call_soon_threadsafe(self._on_complete_cb, self)
