# coding: utf8

from pandas import DataFrame

from refinitiv.dataplatform.content.news.functions import (
    get_news_story,
    get_news_headlines,
)
from refinitiv.dataplatform.content.news.news_headlines import NewsHeadlines
from refinitiv.dataplatform.content.news.news_story import NewsStory
from refinitiv.dataplatform.content.news.sort_order import SortOrder
from refinitiv.dataplatform.content.search import Search, Lookup, ViewMetadata
from refinitiv.dataplatform.content.streaming.streamingprice import StreamingPrice
from refinitiv.dataplatform.content.symbology.symbol_type import SymbolTypes
from refinitiv.dataplatform.errors import RDPError

from refinitiv.dataplatform.delivery.stream import StreamingServiceDirectory
from refinitiv.dataplatform.delivery.stream import StreamingMetadataService

__all__ = [
    "ContentFactory",
    "get_last_status",
    "get_reference_data",
    "get_snapshot",
    "open_realtime_cache",
    "close_realtime_cache",
    "get_historical_price_events",
    "get_historical_price_summaries",
    "get_news_headlines",
    "get_news_story",
    "search",
    "lookup",
    "get_search_metadata",
    "get_esg_universe",
    "get_esg_full_measures",
    "get_esg_standard_measures",
    "get_esg_full_scores",
    "get_esg_standard_scores",
    "get_esg_basic_overview",
    "convert_symbols",
    "create_streaming_service_directory",
    "create_streaming_metadata_service",
]


class _ContentFactory_meta(type):
    def __init__(cls, *args, **kwargs):
        cls.__last_error_status = None
        cls.__last_result = None

    @property
    def _last_result(cls):
        return cls.__last_result

    @_last_result.setter
    def _last_result(cls, value):
        cls.__last_result = value

    @property
    def _last_error_status(cls):
        return cls.__last_error_status

    @_last_error_status.setter
    def _last_error_status(cls, value):
        cls.__last_error_status = value


class ContentFactory(metaclass=_ContentFactory_meta):
    __content_factory = None

    def __init__(self):
        pass

    @classmethod
    def get_default_session(cls):
        from refinitiv.dataplatform.legacy import get_default_session

        return get_default_session()

    @classmethod
    def _get_content_factory(cls):
        return ContentFactory()
        # following code limit ContentFactory instance to 1 singleton
        # if cls.__content_factory is None:
        #     cls.__content_factory = ContentFactory()
        # return cls.__content_factory

    @classmethod
    def _get_last_result(cls):
        return cls._last_result

    @classmethod
    def _get_last_status(cls):
        if cls._last_result:
            return cls._last_result.status

    @classmethod
    def _get_last_error_status(cls):
        return cls._last_error_status

    @staticmethod
    def create_market_price_with_params(mp_params):
        if isinstance(mp_params, StreamingPrice.Params):
            mp = StreamingPrice(
                session=mp_params._session,
                name=mp_params._name,
                service=mp_params._service,
                fields=mp_params._fields,
                api=mp_params._api,
                extended_params=mp_params._extended_params,
                on_refresh=mp_params._on_refresh_cb,
                on_update=mp_params._on_update_cb,
                on_status=mp_params._on_status_cb,
                on_complete=mp_params._on_complete_cb,
            )
            return mp
        else:
            raise Exception("Wrong MarketPrice.Param parameter")

    @staticmethod
    def create_market_price(
        session,
        name,
        service=None,
        fields=None,
        api=None,
        extended_params=None,
        on_refresh=None,
        on_update=None,
        on_status=None,
        on_complete=None,
    ):
        return StreamingPrice(
            session=session,
            name=name,
            service=service,
            fields=fields,
            api=api,
            extended_params=extended_params,
            on_refresh=on_refresh,
            on_update=on_update,
            on_status=on_status,
            on_complete=on_complete,
        )

    @classmethod
    def _get_reference_data(cls, universe, fields=[], parameters={}):
        from refinitiv.dataplatform.pricing.pricing_ import Pricing

        session = cls.get_default_session()
        pricing = Pricing(session)
        reference_data = pricing.get_snapshot(universe, fields, parameters)
        cls._last_result = reference_data
        if (
            reference_data.is_success
            and reference_data.data
            and reference_data.data.df is not None
        ):
            return reference_data.data.df
        else:
            cls._last_error_status = reference_data.status
            return None

    @classmethod
    def _get_snapshot(cls, universe, fields, options={}):
        from refinitiv.dataplatform.pricing.pricing_ import Pricing

        session = ContentFactory.get_default_session()
        pricing = Pricing(session)
        price_data = pricing.get_snapshot(universe, fields)

        cls._last_result = price_data
        if price_data.is_success and price_data.data and price_data.data.df is not None:
            return price_data.data.df
        else:
            cls._last_error_status = price_data.status
            return None

    @classmethod
    def _open_realtime_cache(cls, universe, fields=[]):
        from refinitiv.dataplatform.pricing.pricing_ import PriceCache

        session = ContentFactory.get_default_session()
        price_cache = PriceCache(session, universe, fields)
        price_cache.open()
        return price_cache

    @classmethod
    def _close_realtime_cache(cls, price_cache):
        price_cache.close()

    @classmethod
    def _get_historical_price_events(
        cls,
        universe,
        eventTypes=None,
        start=None,
        end=None,
        adjustments=[],
        count=1,
        fields=[],
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.content.data.historical_pricing import (
            HistoricalPricing,
        )

        session = ContentFactory.get_default_session()
        historical_pricing = HistoricalPricing(session=session, on_response=on_response)
        historic_events = historical_pricing.get_events(
            universe=universe,
            eventTypes=eventTypes,
            start=start,
            end=end,
            adjustments=adjustments,
            count=count,
            fields=fields,
            closure=closure,
        )
        cls._last_result = historic_events
        if (
            historic_events.is_success
            and historic_events.data
            and historic_events.data.df is not None
        ):
            return historic_events.data.df
        else:
            cls._last_error_status = historic_events.status
            return None

    @classmethod
    def _get_historical_price_summaries(
        cls,
        universe,
        interval=None,
        start=None,
        end=None,
        adjustments=None,
        sessions=[],
        count=1,
        fields=[],
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.content.data.historical_pricing import (
            HistoricalPricing,
        )

        session = ContentFactory.get_default_session()
        historical_pricing = HistoricalPricing(session=session, on_response=on_response)
        historic_summaries = historical_pricing.get_summaries(
            universe=universe,
            interval=interval,
            start=start,
            end=end,
            adjustments=adjustments,
            sessions=sessions,
            count=count,
            fields=fields,
            closure=closure,
        )
        cls._last_result = historic_summaries
        if (
            historic_summaries.is_success
            and historic_summaries.data
            and historic_summaries.data.df is not None
        ):
            return historic_summaries.data.df
        else:
            cls._last_error_status = historic_summaries.status
            return None

    _news_headline_endpoint = None

    @classmethod
    def _get_news_headline_endpoint(cls, on_response=None):
        _news_headline_endpoint = NewsHeadlines(
            cls.get_default_session(), on_response=on_response
        )
        return _news_headline_endpoint

    @classmethod
    def _get_news_headlines(
        cls,
        query="Topic:TOPALL and Language:LEN",
        count=10,
        date_from=None,
        date_to=None,
        sort_order=SortOrder.new_to_old,
        on_response=None,
        on_page_response=None,
    ):
        headline_endpoint = cls._get_news_headline_endpoint(on_response=on_response)
        headlines = headline_endpoint.get_headlines(
            query=query,
            count=count,
            date_from=date_from,
            date_to=date_to,
            sort_order=sort_order,
            on_page_response=on_page_response,
        )
        cls._last_result = headline_endpoint
        if headlines is not None:
            if headlines.is_success:
                cls._last_result = headlines
                return headlines.data.df
            else:
                cls._last_error_status = headline_endpoint.status
                return None
        else:
            cls._last_error_status = headline_endpoint.status
            return None

    @classmethod
    async def _get_news_headlines_async(
        cls,
        query="Topic:TOPALL and Language:LEN",
        count=10,
        date_from=None,
        date_to=None,
        sort_order=SortOrder.new_to_old,
        on_response=None,
        on_page_response=None,
        closure=None,
    ):
        headline_endpoint = cls._get_news_headline_endpoint(on_response=on_response)
        headlines = await headline_endpoint.get_headlines_async(
            query=query,
            count=count,
            date_from=date_from,
            date_to=date_to,
            sort_order=sort_order,
            on_page_response=on_page_response,
            closure=closure,
        )
        cls._last_result = headline_endpoint
        if headlines is not None:
            if headlines.is_success:
                cls._last_result = headlines
                return headlines.data.df
            else:
                cls._last_error_status = headline_endpoint.status
                return None
        else:
            cls._last_error_status = headline_endpoint.status
            return None

    @classmethod
    def _get_next_headlines(cls, headlines_response):
        return cls._get_link_headlines(
            headlines_response=headlines_response, link_type="next"
        )

    @classmethod
    def _get_prev_headlines(cls, headlines_response):
        return cls._get_link_headlines(
            headlines_response=headlines_response, link_type="prev"
        )

    @classmethod
    def _get_link_headlines(cls, headlines_response, link_type=None):
        headline_endpoint = cls._get_news_headline_endpoint()
        if isinstance(headlines_response, NewsHeadlines.NewsHeadlinesResponse):
            if headlines_response.data and headlines_response.data.raw:
                links_headlines = headlines_response.data.raw.get("meta")
                if links_headlines:
                    _link = links_headlines.get(link_type)
                    if link_type == "next":
                        _other_headlines_result = headline_endpoint.get_next_headlines(
                            link_next=_link
                        )
                    else:
                        _other_headlines_result = headline_endpoint.get_prev_headlines(
                            link_prev=_link
                        )
                    cls._last_result = _other_headlines_result
                    if (
                        _other_headlines_result.is_success
                        and _other_headlines_result.data
                        and _other_headlines_result.data.df is not None
                    ):
                        cls._last_result = _other_headlines_result
                        return _other_headlines_result.data.df
                    else:
                        cls._last_error_status = _other_headlines_result.status
                        return None
            raise RDPError(
                -1,
                f"Can't get {link_type} headlines from empty object {headlines_response}({type(headlines_response)})",
            )
        elif isinstance(headlines_response, DataFrame):
            if hasattr(headlines_response, f"_link_{link_type}"):
                if link_type == "next":
                    _link = headlines_response._link_next
                    _other_headlines_result = headline_endpoint.get_next_headlines(
                        link_next=_link
                    )
                else:
                    if hasattr(headlines_response, "_link_prev"):
                        _link = headlines_response._link_prev
                        _other_headlines_result = headline_endpoint.get_prev_headlines(
                            link_prev=_link
                        )
                    else:
                        raise RDPError(
                            -1,
                            f"Can't get {link_type} headlines from object {headlines_response}({type(headlines_response)})",
                        )
                cls._last_result = _other_headlines_result
                if (
                    _other_headlines_result.is_success
                    and _other_headlines_result.data
                    and _other_headlines_result.data.df is not None
                ):
                    return _other_headlines_result.data.df
                else:
                    cls._last_error_status = _other_headlines_result.status
                    return None
        raise RDPError(
            -1,
            f"Can't get {link_type} headlines from object {headlines_response}({type(headlines_response)})",
        )

    _news_story_endpoint = None

    @classmethod
    def _get_news_story_endpoint(cls):
        return NewsStory(cls.get_default_session())
        if cls._news_story_endpoint is None:
            session = ContentFactory.get_default_session()
            cls._news_story_endpoint = NewsStory(session)
        return cls._news_story_endpoint

    @classmethod
    def _get_news_story(cls, story_id):
        story = cls._get_news_story_endpoint().get_story(story_id=story_id)
        cls._last_result = story
        if story.is_success and story.data and story.data.text is not None:
            cls._last_result = story
            return story.data.text
        else:
            cls._last_error_status = story.status
            return None

    @classmethod
    async def _get_news_story_async(cls, story_id):
        story = await cls._get_news_story_endpoint().get_story_async(story_id=story_id)
        cls._last_result = story
        if story.is_success and story.data and story.data.text is not None:
            cls._last_result = story
            return story.data.text
        else:
            cls._last_error_status = story.status
            return None

    @classmethod
    def _search(cls, query=None, **kwargs):
        #   call the search api request
        response = Search.search(query=query, **kwargs)
        cls.__last_status = response.status

        #   check the response status
        if response.is_success and response.data:
            #   successfully request
            cls._last_result = response
            return response.data.df
        else:
            #   failed to request a search
            cls._last_error_status = response.status
            return None

    @classmethod
    def _lookup(cls, **kwargs):
        #   call the lookup api to request
        response = Lookup.lookup(**kwargs)
        cls.__last_status = response.status

        #   check the response status
        if response.is_success and response.data:
            #   successfully request
            cls._last_result = response
            return response.data.df
        else:
            #   failed to request a lookup
            cls._last_error_status = response.status
            return None

    @classmethod
    def _search_metadata(cls, **kwargs):
        #   call the search metadata api to request
        response = ViewMetadata.get_metadata(**kwargs)
        cls.__last_status = response.status

        #   check the response status
        if response.is_success and response.data:
            #   successfully request
            cls._last_result = response
            return response.data.df
        else:
            #   failed to request a metadata
            cls._last_error_status = response.status
            return None

    @classmethod
    def _get_esg_universe(cls):
        from refinitiv.dataplatform.content.esg.esg import ESG

        session = ContentFactory.get_default_session()
        esg = ESG(session=session)
        universe_response = esg._get_universe()
        cls._last_result = universe_response
        if (
            universe_response.is_success
            and universe_response.data
            and universe_response.data.df is not None
        ):
            return universe_response.data.df
        else:
            cls._last_error_status = universe_response.status
            return None

    @classmethod
    def _get_esg_data(
        cls, universe, data_type, start=None, end=None, on_response=None, closure=None
    ):
        from refinitiv.dataplatform.content.esg.esg import ESG

        session = ContentFactory.get_default_session()
        esg = ESG(session=session, on_response=on_response)
        universe_response = esg._get_data(
            universe, data_type, start=start, end=end, closure=closure
        )
        cls._last_result = universe_response
        if (
            universe_response.is_success
            and universe_response.data
            and universe_response.data.df is not None
        ):
            return universe_response.data.df
        else:
            cls._last_error_status = universe_response.status
            return None

    @classmethod
    def _convert_symbols(
        cls,
        symbols,
        from_symbol_type=SymbolTypes.RIC,
        to_symbol_types=None,
        on_response=None,
        closure=None,
    ):
        from refinitiv.dataplatform.content.symbology.symbology import Symbology

        session = ContentFactory.get_default_session()
        symbology = Symbology(session=session, on_response=on_response)
        symbology_response = symbology._convert(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
        )
        cls._last_result = symbology_response
        if (
            symbology_response.is_success
            and symbology_response.data
            and symbology_response.data.df is not None
        ):
            return symbology_response.data.df
        else:
            cls._last_error_status = symbology_response.status
            return None

    @staticmethod
    def create_streaming_service_directory(session, connection=None):
        return StreamingServiceDirectory(session, connection)

    @staticmethod
    def create_streaming_metadata_service(session, connection=None):
        return StreamingMetadataService(session, connection)


def get_last_status():
    return ContentFactory._get_last_status()
    return ContentFactory._get_content_factory()._get_last_status()


def get_reference_data(universe, fields=[], parameters={}):
    return ContentFactory._get_content_factory()._get_reference_data(
        universe=universe, fields=fields, parameters=parameters
    )


def get_realtime_snapshot(universe, fields, options={}):
    return ContentFactory._get_content_factory()._get_snapshot(
        universe=universe, fields=fields, options=options
    )


get_snapshot = get_realtime_snapshot


def open_realtime_cache(universe, fields=[]):
    return ContentFactory._get_content_factory()._open_realtime_cache(
        universe=universe, fields=fields
    )


def close_realtime_cache(price_cache):
    return ContentFactory._get_content_factory()._close_realtime_cache(
        price_cache=price_cache
    )


def get_historical_price_events(
    universe,
    eventTypes=None,
    start=None,
    end=None,
    adjustments=[],
    count=1,
    fields=[],
):
    return ContentFactory._get_content_factory()._get_historical_price_events(
        universe=universe,
        eventTypes=eventTypes,
        start=start,
        end=end,
        adjustments=adjustments,
        count=count,
        fields=fields,
    )


def get_historical_price_summaries(
    universe,
    interval=None,
    start=None,
    end=None,
    adjustments=None,
    sessions=[],
    count=1,
    fields=[],
):
    return ContentFactory._get_historical_price_summaries(
        universe=universe,
        interval=interval,
        start=start,
        end=end,
        adjustments=adjustments,
        sessions=sessions,
        count=count,
        fields=fields,
    )


def get_next_headlines(headlines_response):
    return ContentFactory._get_next_headlines(headlines_response)


def get_prev_headlines(headlines_response):
    return ContentFactory._get_prev_headlines(headlines_response)


def search(query=None, **kwargs):
    return ContentFactory._get_content_factory()._search(query, **kwargs)


def get_search_metadata(**kwargs):
    return ContentFactory._get_content_factory()._search_metadata(**kwargs)


def lookup(**kwargs):
    return ContentFactory._get_content_factory()._lookup(**kwargs)


def get_esg_universe():
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_esg_universe()

    Returns
    -------
    DataFrame or None

    """
    return ContentFactory._get_esg_universe()


def get_esg_basic_overview(universe):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_esg_basic_overview(universe='IBM.N')

    Parameters
    ----------
    universe: str
        Requested universe

    Returns
    -------
    DataFrame or None

    """
    from refinitiv.dataplatform.content.esg.esg import ESG

    return ContentFactory._get_esg_data(
        universe=universe, data_type=ESG.DataType.BasicOverview
    )


def get_esg_standard_scores(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_esg_standard_scores(universe='5000002406', start=0, end=-2)

    Parameters
    ----------
    universe: str
        Requested universe

    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    from refinitiv.dataplatform.content.esg.esg import ESG

    return ContentFactory._get_esg_data(
        universe=universe, data_type=ESG.DataType.StandardScores, start=start, end=end
    )


def get_esg_full_scores(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_esg_full_scores(universe='4295904307', start=-5, end=0)

    Parameters
    ----------
    universe: str
        Requested universe

    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    from refinitiv.dataplatform.content.esg.esg import ESG

    return ContentFactory._get_esg_data(
        universe=universe, data_type=ESG.DataType.FullScores, start=start, end=end
    )


def get_esg_standard_measures(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_esg_standard_measures( universe='BNPP.PA', start=0, end=-2)

    Parameters
    ----------
    universe: str
        Requested universe

    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    from refinitiv.dataplatform.content.esg.esg import ESG

    return ContentFactory._get_esg_data(
        universe=universe, data_type=ESG.DataType.StandardMeasures, start=start, end=end
    )


def get_esg_full_measures(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_esg_full_measures(universe='BNPP.PA', start=0, end=-3)

    Parameters
    ----------
    universe: str
        Requested universe

    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    from refinitiv.dataplatform.content.esg.esg import ESG

    return ContentFactory._get_esg_data(
        universe=universe, data_type=ESG.DataType.FullMeasures, start=start, end=end
    )


def convert_symbols(symbols, from_symbol_type=SymbolTypes.RIC, to_symbol_types=None):
    return ContentFactory._convert_symbols(
        symbols=symbols,
        from_symbol_type=from_symbol_type,
        to_symbol_types=to_symbol_types,
    )


def create_streaming_service_directory(session, connection=None):
    return ContentFactory.create_streaming_service_directory(session, connection)


def create_streaming_metadata_service(session, connection=None):
    return ContentFactory.create_streaming_service_directory(session, connection)
