from refinitiv.dataplatform.content.data.historical_pricing import HistoricalPricing
from refinitiv.dataplatform.legacy.tools import get_default_session


class Definition:
    """Class that defines parameters for requesting events from historical pricing"""

    def __init__(
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

        self.universe = universe
        self.eventTypes = eventTypes
        self.start = start
        self.end = end
        self.adjustments = adjustments
        self.count = count
        self.fields = fields
        self.closure = closure

    def get_data(self, session=None, on_response=None):
        _session = session
        if session is None:
            _session = get_default_session()

        if _session is None:
            raise AttributeError("A Session must be started")

        historical_pricing = HistoricalPricing(
            session=_session, on_response=on_response
        )
        return historical_pricing._get_events(
            universe=self.universe,
            eventTypes=self.eventTypes,
            start=self.start,
            end=self.end,
            adjustments=self.adjustments,
            count=self.count,
            fields=self.fields,
            closure=self.closure,
        )

    async def get_data_async(self, session=None, on_response=None):
        _session = session
        if session is None:
            _session = get_default_session()

        if _session is None:
            raise AttributeError("A Session must be started")
        historical_pricing = HistoricalPricing(
            session=_session, on_response=on_response
        )
        response = await historical_pricing._get_events_async(
            universe=self.universe,
            eventTypes=self.eventTypes,
            start=self.start,
            end=self.end,
            adjustments=self.adjustments,
            count=self.count,
            fields=self.fields,
            closure=self.closure,
        )
        return response
