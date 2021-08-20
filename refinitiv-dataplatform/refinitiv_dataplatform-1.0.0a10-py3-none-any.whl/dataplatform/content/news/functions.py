__all__ = [
    "get_news_headlines",
    "get_news_headlines_async",
    "get_headlines",
    "get_headlines_async",
    "get_news_story",
    "get_news_story_async",
    "get_story",
    "get_story_async",
]

from refinitiv.dataplatform.content.news.sort_order import SortOrder
from .news_headlines import NewsHeadlines
from .news_story import NewsStory


def _get_default_session():
    from refinitiv.dataplatform.legacy import get_default_session

    return get_default_session()


# <editor-fold desc="========================================= Headlines =========================================">


def get_headlines(
    query="Topic:TOPALL and Language:LEN",
    count=10,
    date_from=None,
    date_to=None,
    sort_order=SortOrder.new_to_old,
    on_page_response=None,
):
    session = _get_default_session()
    news_headlines = NewsHeadlines(session=session)
    response = news_headlines.get_headlines(
        query,
        count=count,
        date_to=date_to,
        date_from=date_from,
        sort_order=sort_order,
        on_page_response=on_page_response,
    )
    return response


def get_news_headlines(
    query="Topic:TOPALL and Language:LEN",
    count=10,
    date_from=None,
    date_to=None,
    sort_order=SortOrder.new_to_old,
):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> headlines = rdp.get_news_headlines(query="LFR",
    ...                                    date_from="2019-05-01",
    ...                                    date_to="2019-05-02",
    ...                                    count=212)

    Parameters
    ----------
    query: str, optional
    count: int, optional
    date_from: str, optional
    date_to: str, optional
    sort_order: SortOrder or str

    Returns
    -------
    DataFrame or None

    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    result = get_headlines(
        query=query,
        count=count,
        date_from=date_from,
        date_to=date_to,
        sort_order=sort_order,
    )
    ContentFactory._last_result = result
    if result.is_success and result.data and result.data.df is not None:
        return result.data.df
    else:
        ContentFactory._last_error_status = result.status
        return None


async def get_headlines_async(
    query="Topic:TOPALL and Language:LEN",
    count=10,
    date_from=None,
    date_to=None,
    sort_order=SortOrder.new_to_old,
    on_response=None,
    on_page_response=None,
    closure=None,
    session=None,
):
    session = session or _get_default_session()
    news_headlines = NewsHeadlines(session=session, on_response=on_response)
    response = await news_headlines.get_headlines_async(
        query,
        count=count,
        date_to=date_to,
        date_from=date_from,
        sort_order=sort_order,
        on_page_response=on_page_response,
        closure=closure,
    )
    return response


async def get_news_headlines_async(
    query="Topic:TOPALL and Language:LEN",
    count=10,
    date_from=None,
    date_to=None,
    sort_order=SortOrder.new_to_old,
    on_response=None,
    on_page_response=None,
    closure=None,
):
    response = await get_headlines_async(
        query=query,
        count=count,
        date_from=date_from,
        date_to=date_to,
        sort_order=sort_order,
        on_response=on_response,
        on_page_response=on_page_response,
        closure=closure,
    )
    df = response.data.df
    return df


# </editor-fold>
# <editor-fold desc="========================================= Story =========================================">


def get_story(
    story_id,
):
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    session = _get_default_session()
    news_story = NewsStory(session=session)
    result = news_story.get_story(story_id)
    ContentFactory._last_result = result

    if result.is_success and result.data and result.data.df is not None:
        return result.data.text

    else:
        ContentFactory._last_error_status = result.status
        return None


def get_news_story(story_id):
    """
    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> result = rdp.get_news_story(story_id='urn%3Anewsml%3Areuters.com%3A20190531%3AnL2N237053')

    Parameters
    ----------
    story_id: str

    Returns
    -------
    str or None

    """
    return get_story(story_id)


async def get_story_async(story_id, on_response=None, closure=None, session=None):
    session = session or _get_default_session()
    news_story = NewsStory(session=session, on_response=on_response)
    response = await news_story.get_story_async(story_id, closure)
    return response


async def get_news_story_async(story_id):
    response = await get_story_async(story_id)
    text = response.data.text
    return text


# </editor-fold>
