# coding: utf8

__all__ = ["Pricing", "PriceCache"]

import urllib.parse
from collections import namedtuple

import numpy
from pandas import DataFrame
from pandas import to_numeric

from refinitiv.dataplatform.tools._common import urljoin
from refinitiv.dataplatform.content.streaming import StreamingPrice
from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.delivery.stream.stream_cache import StreamCache


class Pricing(object):
    Params = namedtuple("Params", ["universe", "fields"])

    class PricingData(Endpoint.EndpointData):
        def __init__(self, raw_json, dataframe, pricing_response):
            super().__init__(raw_json)
            self._dataframe = dataframe
            self._pricing_response = pricing_response

        @property
        def prices(self):
            price_cache = PriceCache(self._pricing_response)
            return price_cache

    class PricingResponse(Endpoint.EndpointResponse):
        def __init__(self, universe, fields, response, convert_function=None):
            super().__init__(response)
            self.params = Pricing.Params(universe=universe, fields=fields)
            if self.is_success and self._data and self._data.raw:
                _dataframe = convert_function(universe, fields, self._data.raw)
            else:
                _dataframe = None
            try:
                _raw_json = self.data.raw if self.data else None
                if _raw_json:
                    if isinstance(_raw_json, list):
                        errors_states = {}
                        ok_states = {}
                        for item in _raw_json:
                            name = (
                                item["Key"]["Name"]
                                if item.get("Key") and item["Key"].get("Name")
                                else None
                            )
                            state = item.get("State")
                            if name and state:
                                if state.get("Code"):
                                    errors_states.update({name: state})
                                else:
                                    ok_states.update({name: state})
                        if errors_states:
                            self._is_success = False
                            item_state = next(iter(errors_states.values()))
                            self._error_code = item_state.get("Code")
                            self._error_message = item_state.get("Text")
                            self._status.update(errors_states)
                        self._status.update(ok_states)
                    # elif _raw_json.get("error"):
                    #     self._error_code = _raw_json["error"].get("code")
                    #     self._error_message = _raw_json["error"].get("message")
                    #     self._status["error"] = _raw_json["error"])
            except ValueError:
                self._error_code = response.status_code
                self._error_message = response.text
                self._data = Pricing.PricingData(None, None, self)
                return

            self._data = Pricing.PricingData(self._data.raw, _dataframe, self)

    class PricingIterator:
        """ Pricing Iterator class """

        def __init__(self, pricing):
            self._pricing = pricing
            self._universe = list(pricing.keys())
            self._index = 0

        def __next__(self):
            """" Return the next field value from pricing """
            if self._index < len(self._universe):
                result = self._pricing[self._universe[self._index]]
                self._index += 1
                return result
            raise StopIteration()

    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        if session is None:
            session = DefaultSession.get_default_session()

        config = session._get_endpoint_config("data.pricing")
        base_url = config.get_str("url")
        snapshots_url = config.get_str("endpoints.snapshots")
        _url = urljoin(base_url, snapshots_url)

        self._session = session
        self._streaming_prices = {}
        self._snapshot_endpoint = Endpoint(session, _url, on_response=self._on_response)
        self._snapshot_completes = 0
        self._snapshot_image = {}
        self._on_response_cb = on_response

    ###################################################
    #  Access to Pricing as a dict                    #
    ###################################################

    def keys(self):
        if self._streaming_prices:
            return self._streaming_prices.keys()
        return {}.keys()

    def values(self):
        if self._streaming_prices:
            return self._streaming_prices.values()
        return {}.values()

    def items(self):
        if self._streaming_prices:
            return self._streaming_prices.items()
        return {}.items()

    ###################################################
    #  Make Pricing iterable                          #
    ###################################################

    def __iter__(self):
        return Pricing.PricingIterator(self)

    def __getitem__(self, name):
        if self._streaming_prices:
            return self._streaming_prices[name]
        raise KeyError(f"{name} not in Pricing universe")

    def __len__(self):
        return len(self._streaming_prices)

    @staticmethod
    def get_snapshot(
        universe, fields, session=None, parameters=None, on_response=None, closure=None
    ):
        pricing = Pricing(session=session, on_response=on_response)
        result = pricing._get_snapshot(
            universe=universe, fields=fields, parameters=parameters, closure=closure
        )
        return result

    def _get_snapshot(self, universe, fields, parameters=None, closure=None):
        return self._snapshot_endpoint.session._loop.run_until_complete(
            self._get_snapshot_async(
                universe=universe, fields=fields, parameters=parameters, closure=closure
            )
        )

    @staticmethod
    async def get_snapshot_async(
        universe, fields, session=None, parameters=None, on_response=None, closure=None
    ):
        pricing = Pricing(session=session, on_response=on_response)
        result = await pricing._get_snapshot_async(
            universe=universe, fields=fields, parameters=parameters, closure=closure
        )
        return result

    async def _get_snapshot_async(
        self, universe, fields, parameters=None, closure=None
    ):
        _query_parameters = {"universe": ",".join(universe)}

        if fields:
            _query_parameters["fields"] = ",".join(fields)

        endpoint_response = await self._snapshot_endpoint.send_request_async(
            Endpoint.RequestMethod.GET,
            query_parameters=_query_parameters,
            closure=closure,
        )

        _result = Pricing.PricingResponse(
            universe=universe,
            fields=fields,
            response=endpoint_response._response,
            convert_function=self._convert_pricing_json_to_pandas,
        )

        return _result

    ######################################################
    #  methods to convert pricing data to Dataframe      #
    ######################################################

    @staticmethod
    def _convert_pricing_json_to_pandas(universe, fields, json_pricing_data):
        # build numpy array with all field values
        data = numpy.array(
            [Pricing._get_field_values(fields, item) for item in json_pricing_data]
        )
        try:
            df = DataFrame(data, columns=fields, index=universe)
            df = df.apply(to_numeric, errors="ignore")
            if not df.empty:
                df = df.convert_dtypes()
            df = df.reset_index()
            df = df.rename(columns={"index": "Instruments"})
            return df
        except ValueError as e:
            return None

    @staticmethod
    def _get_field_values(fields, item):
        if item["Type"] == "Status":
            status = numpy.nan
            _code = item["State"]["Code"]
            if _code == "NotEntitled":
                status = "#N/P"
            elif _code == "NotFound":
                status = "#N/F"
            return numpy.full(len(fields), status)
        else:
            return numpy.array(
                [Pricing._get_field_value(item["Fields"], f) for f in fields]
            )

    @staticmethod
    def _get_field_value(item_fields, field):
        if item_fields.get(field) is None:
            return numpy.nan
        else:
            return item_fields.get(field)

    ######################################################
    #  methods to forward events                         #
    ######################################################

    def _on_response(self, endpoint, endpoint_response):
        if self._on_response_cb:
            url = endpoint_response.request_message.url
            query_parameters = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            _universe = query_parameters.get("universe")[0].split(",")
            _fields = query_parameters.get("fields")[0].split(",")
            _result = Pricing.PricingResponse(
                universe=_universe,
                fields=_fields,
                response=endpoint_response._response,
                convert_function=self._convert_pricing_json_to_pandas,
            )
            self._on_response_cb(self, _result)

    def open_stream(
        self,
        universe,
        fields=[],
        on_refresh=None,
        on_update=None,
        on_status=None,
        on_complete=None,
        close_after_snapshot=False,
    ):
        if not isinstance(universe, str):
            raise AttributeError("universe must be a string")

        if universe in self._streaming_prices:
            return self._streaming_prices[universe]

        self._streaming_prices[universe] = StreamingPrice(
            session=self._session,
            name=universe,
            fields=fields,
            on_refresh=on_refresh,
            on_update=on_update,
            on_status=on_status,
            on_complete=on_complete,
        )
        self._streaming_prices[universe].open(with_updates=not close_after_snapshot)
        return self._streaming_prices[universe]

    def close_stream(self, stream):

        if stream.name in self._streaming_prices:
            stream.close()
            # self._streaming_prices.pop(stream.name)


class PriceCache:
    def __init__(self, data):
        self._cache = {}
        if data:
            if isinstance(data, Pricing):
                for item in data:
                    self._cache[item.name] = StreamCache(
                        name=item.name,
                        fields=item.fields,
                        service=item.service,
                        status=item.status,
                        record=item._record,
                    )
            elif isinstance(data, Pricing.PricingResponse):
                if data.is_success:
                    fields = data.params.universe
                    for item in data.data.raw:
                        name = None
                        service = None
                        if item.get("Key"):
                            name = item["Key"]["Name"]
                            service = item["Key"]["Service"]
                        self._cache[name] = StreamCache(
                            name=name,
                            fields=fields,
                            service=service,
                            status=item["State"],
                            record=item,
                        )

    ###################################################
    #  Access to PriceCache as a dict                 #
    ###################################################

    def keys(self):
        if self._cache:
            return self._cache.keys()
        return {}.keys()

    def values(self):
        if self._cache:
            return self._cache.values()
        return {}.values()

    def items(self):
        if self._cache:
            return self._cache.items()
        return {}.items()

    ###################################################
    #  Make PriceCache iterable                       #
    ###################################################

    def __iter__(self):
        return Pricing.PricingIterator(self)

    def __getitem__(self, name):
        if self._cache:
            if name in self._cache.keys():
                return self._cache[name]
        raise KeyError(f"{name} not in PriceCache name list")

    def __len__(self):
        return len(self._cache.keys())

    def __str__(self):
        return str(self._cache)
