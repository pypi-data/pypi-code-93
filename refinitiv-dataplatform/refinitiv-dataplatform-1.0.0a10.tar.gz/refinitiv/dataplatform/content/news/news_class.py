# coding: utf8

__all__ = ["News"]

from refinitiv.dataplatform.tools._common import cached_property

from .news_headlines import NewsHeadlines
from .news_story import NewsStory
from .sort_order import SortOrder


class News(object):
    @cached_property
    def _headlines(self):
        return NewsHeadlines(self._session, self._on_response)

    @cached_property
    def _story(self):
        return NewsStory(self._session, self._on_response)

    def __init__(self, session, on_response=None):
        if session is None:
            raise AttributeError("Session must be defined")

        self._session = session
        self._on_response = on_response

    def get_headlines(
        self,
        query="Topic:TOPALL and Language:LEN",
        count=10,
        date_from=None,
        date_to=None,
        sort_order=SortOrder.new_to_old,
        on_page_response=None,
        closure=None,
    ):
        response = self._headlines.get_headlines(
            query, count, date_from, date_to, sort_order, on_page_response, closure
        )
        return response

    async def get_headlines_async(
        self,
        query="Topic:TOPALL and Language:LEN",
        count=10,
        date_from=None,
        date_to=None,
        sort_order=SortOrder.new_to_old,
        on_page_response=None,
        closure=None,
    ):
        response = await self._headlines.get_headlines_async(
            query, count, date_from, date_to, sort_order, on_page_response, closure
        )
        return response

    def get_story(self, story_id, closure=None):
        response = self._story.get_story(story_id, closure)
        return response

    async def get_story_async(self, story_id, closure=None):
        response = await self._story.get_story_async(story_id, closure)
        return response
