from refinitiv.dataplatform.content.esg.esg import ESG
from refinitiv.dataplatform.content.esg.data_type import DataType


class Definition:
    def __init__(self, universe, closure=None):
        self.universe = universe
        self.closure = closure

    def get_data(self, session=None, on_response=None):
        esg = ESG(session, on_response)
        data_response = esg._get_data(
            universe=self.universe,
            data_type=DataType.BasicOverview,
            closure=self.closure,
        )
        return data_response

    async def get_data_async(self, session=None, on_response=None):
        esg = ESG(session, on_response)
        data_response = await esg._get_data_async(
            universe=self.universe,
            data_type=DataType.BasicOverview,
            closure=self.closure,
        )
        return data_response
