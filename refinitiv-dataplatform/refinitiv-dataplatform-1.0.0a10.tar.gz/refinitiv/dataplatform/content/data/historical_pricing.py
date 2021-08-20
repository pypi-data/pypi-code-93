# coding: utf8

__all__ = [
    "HistoricalPricing",
    "EventTypes",
    "Adjustments",
    "MarketSession",
    "Intervals",
]

from enum import Enum, unique

import numpy
from pandas import DataFrame, to_numeric, NaT

from refinitiv.dataplatform.tools._common import cached_property, urljoin
from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.legacy.tools import to_utc_date, to_utc_datetime_isofmt


@unique
class EventTypes(Enum):
    """
    The list of market events (comma delimiter), supported event types are trade, quote and correction.
    Note: Currently support only single event type. If request with multiple event types, the backend will
        pick up the first event type to proceed.
    """

    TRADE = "trade"
    QUOTE = "quote"
    CORRECTION = "correction"


_EVENT_TYPES = [k.value for k in EventTypes]


def _convert_event_types(event_types):
    if isinstance(event_types, list):
        return [_convert_event_types(event_type) for event_type in event_types]
    elif isinstance(event_types, EventTypes):
        return event_types.value
    elif event_types in _EVENT_TYPES:
        return event_types
    else:
        raise AttributeError(f"event_type values must be in {_EVENT_TYPES}")


@unique
class Intervals(Enum):
    ONE_MINUTE = "PT1M"
    FIVE_MINUTES = "PT5M"
    TEN_MINUTES = "PT10M"
    THIRTY_MINUTES = "PT30M"
    SIXTY_MINUTES = "PT60M"
    ONE_HOUR = "PT1H"
    DAILY = "P1D"
    SEVEN_DAYS = "P7D"
    WEEKLY = "P1W"
    MONTHLY = "P1M"
    QUARTERLY = "P3M"
    TWELVE_MONTHS = "P12M"
    YEARLY = "P1Y"


_ISO8601_INTERVALS = [k.value for k in Intervals]
_INTRADAY = _ISO8601_INTERVALS[
    :6
]  # ['PT1M', 'PT5M', 'PT10M', 'PT30M', 'PT60M', 'PT1H']
_INTERDAY = _ISO8601_INTERVALS[6:]  # ['P1D', 'P7D', 'P1W', 'P1M', 'P3M', 'P12M', 'P1Y']


def _convert_interval_to_iso8601(interval):
    if isinstance(interval, Intervals):
        return interval.value
    elif isinstance(interval, str) and interval.upper() in _ISO8601_INTERVALS:
        return Intervals(interval.upper()).value
    else:
        raise AttributeError(f"interval must be in {_ISO8601_INTERVALS}")


@unique
class Adjustments(Enum):
    """
    The list of adjustment types (comma delimiter) that tells the system whether to apply
     or not apply CORAX (Corporate Actions) events or exchange/manual corrections to historical time series data.

     The supported values of adjustments :

        UNADJUSTED - Not apply both exchange/manual corrections and CORAX
        EXCHANGE_CORRECTION - Apply exchange correction adjustment to historical pricing
        MANUAL_CORRECTION - Apply manual correction adjustment to historical pricing i.e. annotations made by content analysts
        CCH - Apply Capital Change adjustment to historical Pricing due to Corporate Actions e.g. stock split
        CRE - Apply Currency Redenomination adjustment when there is redenomination of currency
        RPO - Apply Reuters Price Only adjustment to adjust historical price only not volume
        RTS - Apply Reuters TimeSeries adjustment to adjust both historical price and volume
    """

    UNADJUSTED = "unadjusted"
    EXCHANGE_CORRECTION = "exchangeCorrection"
    MANUAL_CORRECTION = "manualCorrection"
    CCH = "CCH"
    CRE = "CRE"
    RPO = "RPO"
    RTS = "RTS"
    QUALIFIERS = "qualifiers"


_ADJUSTMENTS = [k.value for k in Adjustments]


def _convert_adjustment(adjustments):
    if isinstance(adjustments, list):
        return [_convert_adjustment(adjustment) for adjustment in adjustments]
    elif isinstance(adjustments, Adjustments):
        return adjustments.value
    elif adjustments in _ADJUSTMENTS:
        return adjustments
    else:
        raise AttributeError(f"adjustment values must be in {_ADJUSTMENTS}")


@unique
class MarketSession(Enum):
    PRE = "pre"
    NORMAL = "normal"
    POST = "post"


_MARKET_SESSION = [k.value for k in MarketSession]


def _convert_market_session(market_sessions):
    if isinstance(market_sessions, list):
        return [_convert_market_session(mkt_session) for mkt_session in market_sessions]
    elif isinstance(market_sessions, MarketSession):
        return market_sessions.value
    elif market_sessions in _MARKET_SESSION:
        return market_sessions
    else:
        raise AttributeError(f"market session values must be in {_MARKET_SESSION}")


class HistoricalPricing(object):
    """"""

    class HistoricalPricingData(Endpoint.EndpointData):
        def __init__(self, raw_json, dataframe):
            super().__init__(raw_json)
            self._dataframe = dataframe

    class HistoricalPricingResponse(Endpoint.EndpointResponse):
        def __init__(self, response, convert_function):
            super().__init__(response)
            _raw_json = self.data.raw if self.data else None
            if self.is_success:
                if _raw_json is not None and isinstance(_raw_json, list):
                    _raw_json = _raw_json[0]
                    _status = _raw_json.get("status")
                    _dataframe = None
                    if _status:
                        if "Error" in _status["code"]:
                            self._is_success = False
                            self._status["error"] = _status
                            self._error_code = _status["code"]
                            self._error_message = _status["message"]
                        else:
                            self._status["status"] = _status
                            _dataframe = convert_function(_raw_json)
                    else:
                        _dataframe = convert_function(_raw_json)
                    self._data = HistoricalPricing.HistoricalPricingData(
                        _raw_json, _dataframe
                    )
                else:
                    self._data = HistoricalPricing.HistoricalPricingData(
                        _raw_json, None
                    )
            else:
                self._data = HistoricalPricing.HistoricalPricingData(_raw_json, None)

    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import get_default_session

        if session is None:
            session = get_default_session()

        if session is None:
            raise AttributeError("A Session must be started")

        config = session._get_endpoint_config("data.historical-pricing")
        _url = config.get_str("url")
        self._config = config

        self._on_response_cb = on_response
        self._data = None
        self._endpoint = Endpoint(session, _url, on_response=self._on_response)

    @property
    def data(self):
        return self._data

    @property
    def status(self):
        if self._data:
            return self._data.status
        return {}

    def _on_response(self, endpoint, data):

        self._data = data

        if self._on_response_cb:
            _result = HistoricalPricing.HistoricalPricingResponse(
                data._response, self._convert_historical_json_to_pandas
            )
            if not _result.is_success:
                self._endpoint.session.log(
                    1, f"Historical pricing request failed: {_result.status}"
                )
            self._on_response_cb(self, _result)

    #####################################################
    #  methods to request historical data synchronously #
    #####################################################
    @staticmethod
    def get_events(
        universe,
        session=None,
        eventTypes=None,
        start=None,
        end=None,
        adjustments=None,
        count=None,
        fields=None,
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        if session is None:
            session = DefaultSession.get_default_session()
        if session is not None:
            return HistoricalPricing(
                session=session, on_response=on_response
            )._get_events(
                universe=universe,
                eventTypes=eventTypes,
                start=start,
                end=end,
                adjustments=adjustments,
                count=count,
                fields=fields,
                closure=closure,
            )

    def _get_events(
        self,
        universe,
        eventTypes=None,
        start=None,
        end=None,
        adjustments=None,
        count=None,
        fields=None,
        closure=None,
    ):
        return self._endpoint.session._loop.run_until_complete(
            self._get_events_async(
                universe=universe,
                eventTypes=eventTypes,
                start=start,
                end=end,
                adjustments=adjustments,
                count=count,
                fields=fields,
                closure=closure,
            )
        )

    @staticmethod
    def get_summaries(
        universe,
        session=None,
        interval=None,
        start=None,
        end=None,
        adjustments=None,
        sessions=None,
        count=None,
        fields=None,
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        if session is None:
            session = DefaultSession.get_default_session()
        if session is not None:
            historical_pricing = HistoricalPricing(
                session=session, on_response=on_response
            )
            result = historical_pricing._get_summaries(
                universe=universe,
                interval=interval,
                start=start,
                end=end,
                adjustments=adjustments,
                sessions=sessions,
                count=count,
                fields=fields,
                closure=closure,
            )
            return result

    def _get_summaries(
        self,
        universe=None,
        interval=None,
        start=None,
        end=None,
        adjustments=None,
        sessions=None,
        count=None,
        fields=None,
        closure=None,
    ):
        return self._endpoint.session._loop.run_until_complete(
            self._get_summaries_async(
                universe=universe,
                interval=interval,
                start=start,
                end=end,
                adjustments=adjustments,
                sessions=sessions,
                count=count,
                fields=fields,
                closure=closure,
            )
        )

    #############################################################
    #  methods to request historical data events asynchronously #
    #############################################################
    @staticmethod
    async def get_events_async(
        universe,
        session=None,
        eventTypes=None,
        start=None,
        end=None,
        adjustments=None,
        count=None,
        fields=None,
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        if session is None:
            session = DefaultSession.get_default_session()
        if session is not None:
            historical_pricing = HistoricalPricing(
                session=session, on_response=on_response
            )
            result = await historical_pricing._get_events_async(
                universe=universe,
                eventTypes=eventTypes,
                start=start,
                end=end,
                adjustments=adjustments,
                count=count,
                fields=fields,
                closure=closure,
            )
            return result

    async def _get_events_async(
        self,
        universe,
        eventTypes=None,
        start=None,
        end=None,
        adjustments=None,
        count=None,
        fields=None,
        closure=None,
    ):
        if eventTypes:
            eventTypes = _convert_event_types(eventTypes)

        base_url = self._config.get_str("url")
        events_url = self._config.get_str("endpoints.events")
        _url = urljoin(base_url, events_url, "/{universe}")

        _path_parameters = {"universe": universe}
        _query_parameters = []
        if eventTypes:
            if isinstance(eventTypes, list):
                _query_parameters.append(("eventTypes", ",".join(eventTypes)))
            else:
                _query_parameters.append(("eventTypes", eventTypes))

        if fields:
            if "DATE_TIME" not in fields:
                fields.append("DATE_TIME")

        _result = await self._get_historicalpricing(
            url=_url,
            path_parameters=_path_parameters,
            query_parameters=_query_parameters,
            start=start,
            end=end,
            fn_format_datetime=to_utc_datetime_isofmt,
            adjustments=adjustments,
            count=count,
            fields=fields,
            closure=closure,
        )

        _historical_result = HistoricalPricing.HistoricalPricingResponse(
            _result._response, self._convert_historical_json_to_pandas
        )
        if _historical_result.is_success:
            return _historical_result
        else:
            self._endpoint.session.log(
                1, f"Historical events request failed: {_historical_result.status}"
            )
            return _historical_result

    ################################################################
    #  methods to request historical data summaries asynchronously #
    ################################################################
    @staticmethod
    async def get_summaries_async(
        universe,
        session=None,
        interval=None,
        start=None,
        end=None,
        adjustments=None,
        sessions=None,
        count=None,
        fields=None,
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        if session is None:
            session = DefaultSession.get_default_session()
        if session is not None:
            historical_pricing = HistoricalPricing(
                session=session, on_response=on_response
            )
            result = await historical_pricing._get_summaries_async(
                universe=universe,
                interval=interval,
                start=start,
                end=end,
                adjustments=adjustments,
                sessions=sessions,
                count=count,
                fields=fields,
                closure=closure,
            )
            return result

    @cached_property
    def _interday_summaries_url(self):
        base_url = self._config.get_str("url")
        interday_summaries_url = self._config.get_str("endpoints.interday-summaries")
        url = urljoin(base_url, interday_summaries_url, "/{universe}")

        return url

    @cached_property
    def _intraday_summaries_url(self):
        base_url = self._config.get_str("url")
        intraday_summaries_url = self._config.get_str("endpoints.intraday-summaries")
        url = urljoin(base_url, intraday_summaries_url, "/{universe}")

        return url

    async def _get_summaries_async(
        self,
        universe,
        interval=None,
        start=None,
        end=None,
        adjustments=None,
        sessions=None,
        count=None,
        fields=None,
        closure=None,
    ):
        # By default, if interval is not defined, interday default value is requested
        _url = self._interday_summaries_url

        if isinstance(interval, Enum):
            interval = interval.value
        if interval is not None and not isinstance(interval, str):
            raise TypeError("Interval is not string value")
        if interval is not None:
            _query_parameters = [("interval", interval)]
        else:
            _query_parameters = []
        field_timestamp = "DATE"
        function_format_datetime = to_utc_date
        if interval:
            interval = _convert_interval_to_iso8601(interval)
            if interval in _INTRADAY:
                _url = self._intraday_summaries_url
                field_timestamp = "DATE_TIME"
                function_format_datetime = to_utc_datetime_isofmt

        _path_parameters = {"universe": universe}

        if fields:
            if field_timestamp not in fields:
                fields.append(field_timestamp)

        _result = await self._get_historicalpricing(
            url=_url,
            path_parameters=_path_parameters,
            query_parameters=_query_parameters,
            start=start,
            end=end,
            fn_format_datetime=function_format_datetime,
            adjustments=adjustments,
            market_sessions=sessions,
            count=count,
            fields=fields,
            closure=closure,
        )

        _historical_result = HistoricalPricing.HistoricalPricingResponse(
            _result._response, self._convert_historical_json_to_pandas
        )
        if _historical_result:
            if _historical_result.data and _historical_result.data.df is None:
                self._endpoint.session.log(
                    1,
                    f"Historical summaries request return empty data ({_historical_result.status})",
                )
                _historical_result._is_success = False
            if not _historical_result.is_success:
                self._endpoint.session.log(
                    1,
                    f"Historical summaries request failed: {_historical_result.status}",
                )

        return _historical_result

    ######################################################
    #  methods to request historical data asynchronously #
    ######################################################

    @staticmethod
    def _convert_historical_json_to_pandas(json_historical_data):
        _headers = json_historical_data.get("headers")
        if _headers:
            _fields = [field["name"] for field in _headers]
            field_timestamp = None
            if "DATE_TIME" in _fields:
                field_timestamp = "DATE_TIME"
            elif "DATE" in _fields:
                field_timestamp = "DATE"
            if field_timestamp:
                _timestamp_index = _fields.index(field_timestamp)
                # remove timestamp from fields (timestamp is used as index for dataframe)
                _fields.pop(_timestamp_index)
            else:
                _fields = []
        else:
            _fields = []

        historical_dataframe = None
        _data = json_historical_data.get("data")

        if _data and _fields:
            # build numpy array with all datapoints
            _numpy_array = numpy.array(_data)
            # build timestamp as index for dataframe
            _timestamp_array = numpy.array(
                _numpy_array[:, _timestamp_index], dtype="datetime64"
            )
            # remove timestamp column from numpy array
            _numpy_array = numpy.delete(_numpy_array, numpy.s_[_timestamp_index], 1)

            historical_dataframe = DataFrame(
                _numpy_array, columns=_fields, index=_timestamp_array
            )
            # historical_dataframe = historical_dataframe.apply(to_numeric, errors='ignore')
            if not historical_dataframe.empty:
                historical_dataframe = (
                    historical_dataframe.convert_dtypes()
                )  # convert_string=False)

            historical_dataframe.sort_index(inplace=True)

        return historical_dataframe

    async def _get_historicalpricing(
        self,
        url,
        path_parameters,
        query_parameters=None,
        start=None,
        end=None,
        fn_format_datetime=None,
        adjustments=None,
        market_sessions=None,
        count=None,
        fields=None,
        closure=None,
    ):
        query_parameters = [] if query_parameters is None else query_parameters
        adjustments = [] if adjustments is None else adjustments
        market_sessions = [] if market_sessions is None else market_sessions
        count = 1 if count is None else count
        fields = [] if fields is None else fields

        if fn_format_datetime is None:
            raise ValueError("Format datetime legacy must defined.")

        if start is not None:
            start = fn_format_datetime(start)

        if end is not None:
            end = fn_format_datetime(end)

        if adjustments:
            adjustments = _convert_adjustment(adjustments)
        else:
            adjustments = []

        if market_sessions:
            market_sessions = _convert_market_session(market_sessions)
        else:
            market_sessions = []

        if count < 1:
            raise AttributeError("count minimum value is 1")

        if not isinstance(fields, list) or not all(
            isinstance(field, str) for field in fields
        ):
            raise AttributeError("fields must contains strings")

        _query_parameters = query_parameters
        if start:
            _query_parameters.append(("start", start))
        if end:
            _query_parameters.append(("end", end))
        if adjustments:
            _query_parameters.append(("adjustments", ",".join(adjustments)))
        if market_sessions:
            _query_parameters.append(("sessions", ",".join(market_sessions)))
        if count > 1:
            _query_parameters.append(("count", count))
        if fields:
            _query_parameters.append(("fields", ",".join(fields)))

        self._endpoint.url = url
        _result = await self._endpoint.send_request_async(
            Endpoint.RequestMethod.GET,
            path_parameters=path_parameters,
            query_parameters=_query_parameters,
            closure=closure,
        )
        if _result and not _result.is_success:
            self._endpoint.session.log(
                1, f"Historical Pricing request failed: {_result.status}"
            )

        return _result
