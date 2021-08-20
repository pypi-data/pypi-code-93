from refinitiv.dataplatform.content.esg.esg import ESG


class Definition:
    def __init__(self, closure=None):
        self.closure = closure

    def get_data(self, session=None, on_response=None):
        esg = ESG(session=session, on_response=on_response)
        return esg._get_universe(closure=self.closure)

    async def get_data_async(self, session=None, on_response=None):
        esg = ESG(session, on_response)
        universe_response = await esg._get_universe_async(self.closure)
        return universe_response
