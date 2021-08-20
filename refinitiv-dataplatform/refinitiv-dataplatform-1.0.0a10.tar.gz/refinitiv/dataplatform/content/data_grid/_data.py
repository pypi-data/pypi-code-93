# coding: utf8

from pandas import DataFrame
from refinitiv.dataplatform.delivery.data.endpoint import Endpoint


class FundamentalData(Endpoint.EndpointData):
    def __init__(self, raw, dataframe):
        super().__init__(raw)
        self._data = None
        self._dataframe = dataframe

        if raw:
            self._data = raw.get("data")
