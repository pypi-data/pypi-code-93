# coding: utf8

__all__ = ["ESG"]

import numpy
import pandas as pd

from refinitiv.dataplatform.tools._common import urljoin
from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.errors import ESGError
from .data_type import DataType
from .response import ESGResponse


class ESG(object):
    DataType = DataType

    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import get_default_session

        if session is None:
            session = get_default_session()

        if session is None:
            raise AttributeError("A Session must be started")

        config = session._get_endpoint_config("data.environmental-social-governance")
        self._url = config.get_str("url")
        self._url_universe = urljoin(self._url, config.get_str("endpoints.universe"))
        self._config = config

        self._on_response_cb = on_response
        self._data = None
        self._endpoint = Endpoint(session, self._url, on_response=self._on_response)

    def __del__(self):
        self._on_response_cb = None
        self._data = None
        self._endpoint = None

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
            _result = ESGResponse(data._response, _convert_esg_json_to_pandas)
            if not _result.is_success:
                self._endpoint.session.log(1, f"ESG request failed: {_result.status}")
            self._on_response_cb(self, _result)

    @staticmethod
    def get_universe(session=None, closure=None, on_response=None):
        esg = ESG(session, on_response)
        universe_response = esg._get_universe(closure)
        return universe_response

    @staticmethod
    async def get_universe_async(session=None, closure=None, on_response=None):
        esg = ESG(session, on_response)
        universe_response = await esg._get_universe_async(closure)
        return universe_response

    @staticmethod
    def get_basic_overview(universe, session=None, closure=None, on_response=None):
        return ESG.__get_data(
            universe,
            DataType.BasicOverview,
            session=session,
            closure=closure,
            on_response=on_response,
        )

    @staticmethod
    async def get_basic_overview_async(
        universe, session=None, closure=None, on_response=None
    ):
        return await ESG.__get_data_async(
            universe,
            DataType.BasicOverview,
            session=session,
            closure=closure,
            on_response=on_response,
        )

    @staticmethod
    def get_standard_scores(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return ESG.__get_data(
            universe, DataType.StandardScores, start, end, session, closure, on_response
        )

    @staticmethod
    async def get_standard_scores_async(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return await ESG.__get_data_async(
            universe, DataType.StandardScores, start, end, session, closure, on_response
        )

    @staticmethod
    def get_full_scores(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return ESG.__get_data(
            universe, DataType.FullScores, start, end, session, closure, on_response
        )

    @staticmethod
    async def get_full_scores_async(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return await ESG.__get_data_async(
            universe, DataType.FullScores, start, end, session, closure, on_response
        )

    @staticmethod
    def get_standard_measures(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return ESG.__get_data(
            universe,
            DataType.StandardMeasures,
            start,
            end,
            session,
            closure,
            on_response,
        )

    @staticmethod
    async def get_standard_measures_async(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return await ESG.__get_data_async(
            universe,
            DataType.StandardMeasures,
            start,
            end,
            session,
            closure,
            on_response,
        )

    @staticmethod
    def get_full_measures(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return ESG.__get_data(
            universe, DataType.FullMeasures, start, end, session, closure, on_response
        )

    @staticmethod
    async def get_full_measures_async(
        universe, start=None, end=None, session=None, closure=None, on_response=None
    ):
        return await ESG.__get_data_async(
            universe, DataType.FullMeasures, start, end, session, closure, on_response
        )

    @staticmethod
    def __get_data(
        universe,
        data_type,
        start=None,
        end=None,
        session=None,
        closure=None,
        on_response=None,
    ):
        esg = ESG(session, on_response)
        data_response = esg._get_data(universe, data_type, start, end, closure)
        return data_response

    @staticmethod
    async def __get_data_async(
        universe,
        data_type,
        start=None,
        end=None,
        session=None,
        closure=None,
        on_response=None,
    ):
        esg = ESG(session, on_response)
        data_response = await esg._get_data_async(
            universe, data_type, start, end, closure
        )
        return data_response

    def _get_universe(self, closure=None):
        return self._endpoint.session._loop.run_until_complete(
            self._get_universe_async(closure)
        )

    async def _get_universe_async(self, closure=None):
        _result = await self.__get_esg(self._url_universe, closure=closure)

        _esg_result = ESGResponse(_result._response, _convert_esg_json_to_pandas)
        if _esg_result:
            if _esg_result.data is None:
                self._endpoint.session.log(
                    1, f"ESG universe request return empty data ({_esg_result.status})"
                )
                _esg_result._is_success = False
            if not _esg_result.is_success:
                self._endpoint.session.log(
                    1, f"ESG universe request failed: {_esg_result.status}"
                )

        return _esg_result

    def _get_data(self, universe, data_type, start=None, end=None, closure=None):
        return self._endpoint.session._loop.run_until_complete(
            self._get_data_async(universe, data_type, start, end, closure)
        )

    def _get_url(self, data_type=None):
        if data_type:
            data_type = DataType.convert_to_str(data_type)
            url = self._config.get_str(f"endpoints.{data_type}")
            url = urljoin(self._url, url)
            return url

        return self._url

    async def _get_data_async(
        self, universe, data_type, start=None, end=None, closure=None
    ):

        if not universe:
            raise ESGError(-1, "Universe was not requested.")

        if not data_type:
            raise ESGError(-1, "Data type was not requested.")

        if start is not None and end is None:
            raise ESGError(
                -1, f"Start requested without end parameter. start:{start} - end:{end}"
            )

        if start is None and end is not None:
            raise ESGError(
                -1, f"End requested without start parameter. start:{start} - end:{end}"
            )

        _query_parameters = [("universe", universe)]

        if start is not None and end is not None:
            _query_parameters.append(("start", start))
            _query_parameters.append(("end", end))

        _result = await self.__get_esg(
            url=self._get_url(data_type),
            query_parameters=_query_parameters,
            closure=closure,
        )

        _esg_result = ESGResponse(_result._response, _convert_esg_json_to_pandas)
        if _esg_result:
            if _esg_result.data is None:
                self._endpoint.session.log(
                    1, f"ESG universe request return empty data ({_esg_result.status})"
                )
                _esg_result._is_success = False
            if not _esg_result.is_success:
                self._endpoint.session.log(
                    1, f"ESG universe request failed: {_esg_result.status}"
                )

        return _esg_result

    async def __get_esg(
        self, url, path_parameters=None, query_parameters=None, closure=None
    ):
        self._endpoint.url = url
        _result = await self._endpoint.send_request_async(
            Endpoint.RequestMethod.GET,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            closure=closure,
        )
        if _result and not _result.is_success:
            self._endpoint.session.log(1, f"ESG request failed: {_result.status}")

        return _result


def _convert_esg_json_to_pandas(json_esg_data):
    _fields = [field["name"] for field in json_esg_data["headers"]]
    _data = json_esg_data["data"]
    if _data:
        # build numpy array with all data points
        _numpy_array = numpy.array(_data)
        esg_dataframe = pd.DataFrame(_numpy_array, columns=_fields)
        if not esg_dataframe.empty:
            esg_dataframe = esg_dataframe.convert_dtypes()
    else:
        esg_dataframe = pd.DataFrame([], columns=_fields)

    return esg_dataframe
