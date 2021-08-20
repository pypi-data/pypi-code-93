from refinitiv.dataplatform.content.data.historical_pricing import HistoricalPricing
from refinitiv.dataplatform.legacy.tools import get_default_session


class Definition:
    """Class that defines parameters for requesting summaries from historical pricing"""

    def __init__(
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

        self.universe = universe
        self.interval = interval
        self.start = start
        self.end = end
        self.adjustments = adjustments
        self.sessions = sessions
        self.count = count
        self.fields = fields
        self.closure = closure

    def get_data(self, session=None, on_response=None):
        _session = session
        if _session is None:
            _session = get_default_session()

        if _session is None:
            raise AttributeError("A Session must be started")
        historical_pricing = HistoricalPricing(
            session=_session, on_response=on_response
        )
        return historical_pricing._get_summaries(
            universe=self.universe,
            interval=self.interval,
            start=self.start,
            end=self.end,
            adjustments=self.adjustments,
            sessions=self.sessions,
            count=self.count,
            fields=self.fields,
            closure=self.closure,
        )

    async def get_data_async(self, session=None, on_response=None):
        _session = session
        if _session is None:
            _session = get_default_session()

        if _session is None:
            raise AttributeError("A Session must be started")
        historical_pricing = HistoricalPricing(
            session=_session, on_response=on_response
        )
        response = await historical_pricing._get_summaries_async(
            universe=self.universe,
            interval=self.interval,
            start=self.start,
            end=self.end,
            adjustments=self.adjustments,
            sessions=self.sessions,
            count=self.count,
            fields=self.fields,
            closure=self.closure,
        )
        return response
