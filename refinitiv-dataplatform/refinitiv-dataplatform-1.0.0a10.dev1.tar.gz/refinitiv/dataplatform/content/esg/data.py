from refinitiv.dataplatform.delivery.data import Endpoint


class ESGData(Endpoint.EndpointData):
    def __init__(self, raw, dataframe):
        super().__init__(raw)
        self._dataframe = dataframe
