# coding: utf8

__all__ = ["CurveDefinition"]

import abc

from pandas import DataFrame

from refinitiv.dataplatform.delivery.data.endpoint import Endpoint
from ..instrument._definition import ObjectDefinition


class CurveDefinition(ObjectDefinition, abc.ABC):
    class Data(Endpoint.EndpointData):
        def __init__(self, raw):
            super().__init__(raw)
            self._data = None

            if raw:
                self._data = raw.get("data")

        @property
        def df(self):
            if self._data:
                data_dataframe = DataFrame(self._data).convert_dtypes()
            else:
                data_dataframe = DataFrame([])
            return data_dataframe

    class Response(Endpoint.EndpointResponse):
        def __init__(self, response):
            super().__init__(response, service_class=CurveDefinition)
