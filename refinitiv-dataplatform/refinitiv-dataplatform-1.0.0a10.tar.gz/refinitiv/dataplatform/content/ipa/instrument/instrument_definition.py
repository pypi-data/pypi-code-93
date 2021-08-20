# coding: utf8

__all__ = ["InstrumentDefinition"]

import abc

import numpy
from pandas import DataFrame

from refinitiv.dataplatform.delivery.data.endpoint import Endpoint
from ._definition import ObjectDefinition


class InstrumentDefinition(ObjectDefinition, abc.ABC):
    """
    This class is designed to represent the instrument definition templates for QPS request.
    """

    class Data(Endpoint.EndpointData):
        """
        This class is designed for storing and managing the response instrument data
        """

        def __init__(self, raw):
            super().__init__(raw)
            self._analytics_headers = None
            self._analytics_data = None
            self._analytics_market_data = None
            self._analytics_statuses = None
            if raw:
                #   get headers
                self._analytics_headers = raw.get("headers")
                #   get data
                self._analytics_data = raw.get("data")
                #   get marketData
                self._analytics_market_data = raw.get("marketData")
                #   get statuses
                self._analytics_statuses = raw.get("statuses")

        @property
        def analytics_headers(self):
            return self._analytics_headers

        @property
        def analytics_data(self):
            return self._analytics_data

        @property
        def analytics_market_data(self):
            return self._analytics_market_data

        @property
        def analytics_statuses(self):
            return self._analytics_statuses

        @property
        def df(self):
            """
            Convert "data" from raw response bond to dataframe format
            """
            data_dataframe = None
            if self.analytics_data:
                headers = [header["name"] for header in self.analytics_headers]
                numpy_array = numpy.array(self.analytics_data, dtype=object)
                data_dataframe = DataFrame(numpy_array, columns=headers)
                if not data_dataframe.empty:
                    data_dataframe = data_dataframe.convert_dtypes()
            else:
                data_dataframe = DataFrame([], columns=[])
            return data_dataframe

        @property
        def marketdata_df(self):
            """
            Convert "marketData" from raw response bond to dataframe format
            """
            return None

    class Response(Endpoint.EndpointResponse):
        def __init__(self, response):
            super().__init__(response, service_class=InstrumentDefinition)

            if self.is_success:
                raw_data = self._data.raw
                status = raw_data.get("status", False)

                if status == "Error":
                    self._error_code = raw_data.get("code")
                    self._error_message = raw_data.get("message")
                    self._is_success = False

    #
    # class Params(abc.ABC):
    #
    #     def __init__(self):
    #         self._instrument_tag = None
    #
    #     def with_instrument_tag(self, value):
    #         """
    #         User defined string to identify the instrument.It can be used to link output results to the instrument definition.
    #             Only alphabetic, numeric and '- _.#=@' characters are supported.
    #         """
    #         self._instrument_tag = value
    #         return self
    #
    # @classmethod
    # def from_params(cls, params):
    #     if isinstance(params, InstrumentDefinition.Params):
    #         return InstrumentDefinition(tag=params._instrument_tag)
    #     else:
    #         return None

    @classmethod
    def get_instrument_type(cls):
        return ""

    def __init__(self, tag=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_tag = tag

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output results to the instrument definition.
        Only alphabetic, numeric and '- _.#=@' characters are supported.
        Optional.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        try:
            value = value.value
        except:
            pass
        self._set_parameter("instrumentTag", value)
