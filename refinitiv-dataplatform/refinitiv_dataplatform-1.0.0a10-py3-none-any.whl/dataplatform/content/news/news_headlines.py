# coding: utf8

__all__ = ["NewsHeadlines"]

import logging
import sys

import numpy
import pandas as pd

from refinitiv.dataplatform.tools._common import urljoin
from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.errors import NewsHeadlinesError
from refinitiv.dataplatform.legacy.tools import to_datetime, tz_replacer
from .data_classes import Headline
from .sort_order import SortOrder


class NewsHeadlines(object):
    """"""

    class NewsHeadlinesData(Endpoint.EndpointData):
        def __init__(self, raw_json, dataframe):
            super().__init__(raw_json)
            self._dataframe = dataframe
            self._headlines = None

            self._raw = self._raw or {}

        @property
        def story_ids(self):
            return NewsHeadlines._get_story_ids(self.raw)

        @property
        def headlines(self):
            if self._headlines is None:
                self._headlines = []
                for datum in self._raw.get("data", []):
                    headline = Headline.create(datum)
                    self._headlines.append(headline)
            return self._headlines

    class NewsHeadlinesResponse(Endpoint.EndpointResponse):
        def __init__(self, response, convert_function):
            super().__init__(response)
            _raw_json = None
            _dataframe = None
            if self.is_success:
                _raw_json = self.data.raw
                _dataframe = convert_function(_raw_json) if _raw_json else None
            self._data = NewsHeadlines.NewsHeadlinesData(_raw_json, _dataframe)

    def __init__(self, session, on_response=None):
        if session is None:
            raise AttributeError("Session must be defined")

        config = session._get_endpoint_config("data.news")
        base_url = config.get_str("url")
        headlines_url = config.get_str("endpoints.headlines")
        self._url = urljoin(base_url, headlines_url)

        self._session = session
        self._on_response_cb = on_response

        self._data = None
        self._endpoint_headlines = Endpoint(
            session, self._url, on_response=self._on_response
        )
        self._partial_next_dataframe = None
        self._partial_next_raw = None

    @property
    def data(self):
        return self._data

    @property
    def status(self):
        if self._data:
            return self._data.status
        return {}

    def _on_response(self, endpoint, data):

        self._data = data

        if self._on_response_cb:
            _result = NewsHeadlines.NewsHeadlinesResponse(
                data._response, self._convert_headlines_json_to_pandas
            )

            if not _result.is_success:
                endpoint.session.log(
                    1, f"News Headlines request failed: {_result.status}"
                )
                if _result.data.raw is not None and _result.data.df is None:
                    endpoint.session.log(
                        logging.DEBUG,
                        f"Fail to parse news headlines result: \n{_result.data.raw}",
                    )

            self._on_response_cb(self, _result)

    #####################################################
    #  methods to request news headlines synchronously  #
    #####################################################
    def get_headlines(
        self,
        query,
        count=10,
        date_from=None,
        date_to=None,
        sort_order=SortOrder.new_to_old,
        on_page_response=None,
        closure=None,
    ):
        return self._session._loop.run_until_complete(
            self.get_headlines_async(
                query, count, date_from, date_to, sort_order, on_page_response, closure
            )
        )

    #####################################################
    #  methods to request news headlines asynchronously #
    #####################################################
    async def get_headlines_async(
        self,
        query,
        count=10,
        date_from=None,
        date_to=None,
        sort_order=SortOrder.new_to_old,
        on_page_response=None,
        closure=None,
    ):

        self._partial_next_dataframe = None
        self._partial_next_raw = None

        if count < 0:
            raise AttributeError("count minimum value is 0")

        if "daterange:" in query and (date_from or date_to):
            raise AttributeError("daterange in two places")

        if isinstance(query, str):
            _query_parameters = {"query": query}
        else:
            _query_parameters = query

        _start = None
        _end = None

        if date_from:
            _start = to_datetime(date_from)

        if date_to:
            _end = to_datetime(date_to)

        if _start and _end:
            # add query parameter "daterange:"<_start>,<_end>"
            _date_range = f'daterange:"{_start},{_end}"'
            _query_parameters["query"] = " ".join(
                [_query_parameters["query"], _date_range]
            )
        elif _start:
            # add query parameter "After <_start>"
            _query_parameters["query"] = " AFTER ".join(
                [_query_parameters["query"], str(_start.date())]
            )
        elif _end:
            # add query parameter "Before <_end>"
            _query_parameters["query"] = " BEFORE ".join(
                [_query_parameters["query"], str(_end.date())]
            )

        if count > 0:
            _query_parameters["number"] = min(count, 100)
        else:
            _query_parameters["number"] = 100

        if sort_order and sort_order is not SortOrder.new_to_old:
            _query_parameters["sort"] = SortOrder.convert_to_str(sort_order)

        _result = await self._endpoint_headlines.send_request_async(
            Endpoint.RequestMethod.GET,
            query_parameters=_query_parameters,
            closure=closure,
        )
        if _result:
            _headlines_result = NewsHeadlines.NewsHeadlinesResponse(
                _result._response, self._convert_headlines_json_to_pandas
            )
            if _headlines_result.is_success:
                if count == 0:
                    count = sys.maxsize
                if count > 100 or count == 0:
                    full_data = _headlines_result.data.raw["data"]
                    meta = _headlines_result.data.raw.get("meta")
                    full_responses = [_headlines_result.data.df]
                    if meta is not None:
                        next_link = meta.get("next")
                        for _count in range(0, count - 100, 100):
                            if next_link:
                                _headlines_result = await self.get_next_headlines_async(
                                    link_next=next_link, closure=closure
                                )
                                if (
                                    _headlines_result.is_success
                                    and _headlines_result.data
                                    and _headlines_result.data.df is not None
                                ):
                                    full_responses.append(_headlines_result.data.df)
                                    raw = _headlines_result.data.raw
                                    raw_data = raw.get("data")
                                    if raw_data:
                                        full_data += raw_data
                                    else:
                                        self._session.debug(
                                            f"raw_data is empty: \n{raw_data}"
                                        )
                                    meta["count"] = meta["count"] + 100
                                    if raw.get("meta") and raw.get("meta").get("next"):
                                        next_link = raw["meta"]["next"]
                                    else:
                                        next_link = None
                                if on_page_response:
                                    on_page_response(self, _headlines_result)
                            else:
                                break
                        if _headlines_result.is_success:
                            # remove exceeded headlines beyond count number
                            full_responses = NewsHeadlines._concat_headlines_dataframe(
                                full_responses
                            )
                            self._partial_next_dataframe = full_responses[count:]
                            # if hasattr(full_responses, "_link_prev"):
                            #     setattr(self._partial_next_dataframe, "_link_prev", full_responses._link_prev)
                            # if hasattr(full_responses, "_link_next"):
                            #     setattr(self._partial_next_dataframe, "_link_next", full_responses._link_next)
                            # self._partial_next_raw = {"data": full_data[count:], "meta": meta}
                            self._partial_next_raw = {"data": full_data[count:]}
                            full_responses = full_responses[:count]
                            full_data = full_data[:count]
                            meta["count"] = count
                            _headlines_result._data._dataframe = full_responses
                            _headlines_result._data._raw = {
                                "data": full_data,
                                "meta": meta,
                            }
                return _headlines_result
            self._session.log(
                1, f"News Headlines request failed: {_headlines_result.status}"
            )
            if (
                _headlines_result.data.raw is not None
                and _headlines_result.data.df is None
            ):
                self._session.debug(
                    f"Fail to parse news headlines result: \n{_headlines_result.data.raw}"
                )
            return _headlines_result
        else:
            raise NewsHeadlinesError(-1, "GET headlines request failed")

    ###############################################################
    #  methods to request next/prev news headlines synchronously  #
    ###############################################################
    def get_next_headlines(self, link_next=None):
        return self._session._loop.run_until_complete(
            self.get_next_headlines_async(link_next)
        )

    def get_prev_headlines(self, link_prev=None):
        return self._session._loop.run_until_complete(
            self.get_prev_headlines_async(link_prev)
        )

    ###############################################################
    #  methods to request next/prev news headlines asynchronously #
    ###############################################################
    async def get_next_headlines_async(self, link_next=None, closure=None):
        result = None
        if link_next is None:
            if self.data and self.data.is_success and self.data.data.raw:
                links_headlines = self.data.data.raw.get("meta")
                if links_headlines:
                    link_next = links_headlines.get("next")
        if link_next is not None:
            result = await self._get_link_headlines_async(
                link_type="next", link=link_next, closure=closure
            )
            if self._partial_next_dataframe is not None:
                # prepend partial dataframe and raw to result
                result.data._dataframe = self._concat_headlines_dataframe(
                    [self._partial_next_dataframe, result.data.df]
                )
                result.data._raw["data"] = self._partial_next_raw["data"].extend(
                    result.data.raw["data"]
                )
                self._partial_next_dataframe = None
                self._partial_next_raw = None
        return result

    async def get_prev_headlines_async(self, link_prev=None, closure=None):
        result = None
        if link_prev is None:
            if self.data.is_success and self.data.data.raw:
                links_headlines = self.data.data.raw.get("meta")
                if links_headlines:
                    link_prev = links_headlines.get("prev")
        if link_prev is not None:
            result = await self._get_link_headlines_async(
                link_type="prev", link=link_prev, closure=closure
            )

        return result

    async def _get_link_headlines_async(
        self, link_type="next", link=None, closure=None
    ):
        if link is None:
            if self.data.is_success:
                if self.data.data.raw:
                    links_headlines = self.data.data.raw.get("meta")
                    if links_headlines:
                        link = links_headlines.get(link_type)
                    else:
                        self._endpoint_headlines.session.log(
                            logging.DEBUG,
                            f"There is no {link_type} headlines in {links_headlines}",
                        )
                else:
                    self._endpoint_headlines.session.log(
                        logging.DEBUG,
                        f"Can't request {link_type} headlines for empty data",
                    )
            else:
                self._endpoint_headlines.session.log(
                    logging.DEBUG, f"Can't request {link_type} headlines for empty data"
                )

        if link:
            _query_parameters = {"cursor": link}
            _result = await self._endpoint_headlines.send_request_async(
                Endpoint.RequestMethod.GET,
                query_parameters=_query_parameters,
                closure=closure,
            )

            _headlines_result = NewsHeadlines.NewsHeadlinesResponse(
                _result._response, self._convert_headlines_json_to_pandas
            )
            if not _headlines_result.is_success:
                self._endpoint_headlines.session.log(
                    1,
                    f"News Headlines {link} request failed: {_headlines_result.status}",
                )

            return _headlines_result
        else:
            raise NewsHeadlinesError(
                -1, "Can't get prev/next headlines from empty Headlines object"
            )

    ######################################################
    #  method  to get story id from headline             #
    ######################################################

    @staticmethod
    def _get_story_ids(news_headlines_raw):
        headlines = news_headlines_raw["data"]
        story_ids = [headline["storyId"] for headline in headlines]
        return story_ids

    ######################################################
    #  method  to get news story                         #
    ######################################################

    ######################################################
    #  method  to convert headlines to dataframe         #
    ######################################################

    @staticmethod
    def _convert_headlines_json_to_pandas(json_headlines_data):
        from refinitiv.dataplatform.legacy.tools import to_datetime

        json_headlines_array = json_headlines_data["data"]
        first_created = [
            tz_replacer(headline["newsItem"]["itemMeta"]["firstCreated"]["$"])
            for headline in json_headlines_array
        ]
        Headline_Selected_Fields = ["versionCreated", "text", "storyId", "sourceCode"]
        headlines = []
        try:
            for headline in json_headlines_array:
                info_sources = headline["newsItem"]["contentMeta"]["infoSource"]
                info_source = next(
                    (
                        item["_qcode"]
                        for item in info_sources
                        if item["_role"] == "sRole:source"
                    ),
                    None,
                )
                # version_created = to_utc_datetime(headline["newsItem"]["itemMeta"]["versionCreated"]["$"])
                version_created = to_datetime(
                    headline["newsItem"]["itemMeta"]["versionCreated"]["$"]
                )
                headlines.append(
                    [
                        version_created,
                        headline["newsItem"]["itemMeta"]["title"][0]["$"],
                        headline["storyId"],
                        info_source,
                    ]
                )
            headlines_dataframe = None
            if headlines:
                headlines_dataframe = pd.DataFrame(
                    headlines,
                    numpy.array(first_created, dtype="datetime64"),
                    Headline_Selected_Fields,
                )
                if not headlines_dataframe.empty:
                    headlines_dataframe = headlines_dataframe.convert_dtypes()
                headlines_dataframe["versionCreated"] = headlines_dataframe[
                    "versionCreated"
                ].astype("datetime64[ns]")
            else:
                headlines_dataframe = pd.DataFrame([], columns=Headline_Selected_Fields)
            # if json_headlines_data.get("meta") and json_headlines_data.get("meta").get("next"):
            #     setattr(headlines_dataframe, "_link_next", json_headlines_data["meta"]["next"])
            # if json_headlines_data.get("meta") and json_headlines_data.get("meta").get("prev"):
            #     setattr(headlines_dataframe, "_link_prev", json_headlines_data["meta"]["prev"])
            return headlines_dataframe
        except Exception as e:
            raise e

    @staticmethod
    def _concat_headlines_dataframe(headlines_list):
        if isinstance(headlines_list, list):
            concated_headlines = pd.concat(headlines_list)
            # first_headlines = headlines_list[0]
            # last_headlines = headlines_list[-1]
            # if hasattr(first_headlines, "_link_prev"):
            #     setattr(concated_headlines, "_link_prev", first_headlines._link_prev)
            # if hasattr(first_headlines, "_link_next"):
            #     setattr(concated_headlines, "_link_next", last_headlines._link_next)
            return concated_headlines
