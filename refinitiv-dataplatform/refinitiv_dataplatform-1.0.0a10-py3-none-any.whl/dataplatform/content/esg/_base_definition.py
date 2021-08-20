from refinitiv.dataplatform.content.esg.esg import ESG


class BaseDefinition:
    def __init__(self, universe, start=None, end=None, closure=None):
        self.universe = universe
        self.start = start
        self.end = end
        self.closure = closure
        self._data_type = None

    def get_data(self, session=None, on_response=None):
        esg = ESG(session, on_response)
        data_response = esg._get_data(
            self.universe, self._data_type, self.start, self.end, self.closure
        )
        return data_response

    async def get_data_async(self, session=None, on_response=None):
        esg = ESG(session, on_response)
        data_response = await esg._get_data_async(
            self.universe, self._data_type, self.start, self.end, self.closure
        )
        return data_response
