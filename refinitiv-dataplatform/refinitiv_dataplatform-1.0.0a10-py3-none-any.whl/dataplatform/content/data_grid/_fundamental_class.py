# coding: utf8

__all__ = ["Fundamental"]

import numpy
import pandas as pd
import json
from refinitiv.dataplatform.core.log_reporter import LogReporter
from refinitiv.dataplatform.legacy.tools import (
    check_for_string_or_list_of_strings,
    build_list,
    is_string_type,
)
from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.tools._common import urljoin
from ._response import FundamentalResponse


class Fundamental(LogReporter):
    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session or DefaultSession.get_default_session()

        if session is None:
            raise AttributeError("A Session must be started")

        super().__init__(logger=session)

        config = session._get_endpoint_config("data.datagrid")
        base_url = config.get_str("url")
        standard_url = config.get_str("endpoints.standard")
        self._url = urljoin(base_url, standard_url)
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

    def _run_until_complete(self, future):
        return self._endpoint.session._loop.run_until_complete(future)

    @staticmethod
    def get_data(
        universe,
        fields,
        parameters=None,
        field_name=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        fundamental = Fundamental(session=session, on_response=on_response)
        result = fundamental._get_data(
            universe=universe,
            fields=fields,
            parameters=parameters,
            field_name=field_name,
            closure=None,
            session=None,
        )
        return result

    def _get_data(
        self,
        universe,
        fields,
        parameters=None,
        field_name=None,
        closure=None,
        session=None,
    ):
        """
        :param universe: list    The list of RICs
        :param fields: list      List of fundamental field names
        :param parameters
        :param closure:str
        :param session:Session
        :return:Response
        """
        result = self._run_until_complete(
            self._get_data_async(
                universe=universe,
                fields=fields,
                parameters=parameters,
                field_name=field_name,
                closure=closure,
            )
        )
        return result

    async def _get_data_async(
        self,
        universe,
        fields,
        parameters=None,
        field_name=None,
        closure=None,
        session=None,
    ):

        from refinitiv.dataplatform.legacy.tools import DefaultSession

        check_for_string_or_list_of_strings(universe, "universe")
        universe = build_list(universe, "universe")
        universe = [value.upper() if value.islower() else value for value in universe]

        if len(universe) == 0:
            with "get_data error: universe must not be empty" as error_msg:
                self.error(error_msg)
                raise ValueError(error_msg)

        if field_name is None:
            self.field_name = False
        else:
            self.field_name = field_name

        fields_for_request = fields
        fields = self._parse_fields(fields)

        payload = {"universe": universe, "fields": fields_for_request}

        if parameters:
            parameters = build_dictionary(parameters, "parameters")
            payload.update({"parameters": parameters})

        response = await self._endpoint.send_request_async(
            Endpoint.RequestMethod.POST,
            header_parameters={"Accept": "application/json"},
            body_parameters=payload,
            closure=closure,
        )
        if response and not response.is_success:
            self._endpoint.session.log(
                1, f"Fundamental request failed: {response.status}"
            )

        _fundamental_result = FundamentalResponse(
            response._response, _convert_fundamental_json_to_pandas, self.field_name
        )
        if _fundamental_result:
            if _fundamental_result.data is None:
                self._endpoint.session.log(
                    1,
                    f"Fundamental request return empty data ({_fundamental_result.status})",
                )
                _fundamental_result._is_success = False
            if not _fundamental_result.is_success:
                self._endpoint.session.log(
                    1, f"Fundamental request failed: {_fundamental_result.status}"
                )

        return _fundamental_result

    def _on_response(self, endpoint, data):

        self._data = data

        if self._on_response_cb:
            _result = FundamentalResponse(
                data._response, _convert_fundamental_json_to_pandas, self.field_name
            )
            if not _result.is_success:
                self._endpoint.session.log(
                    1, f"Fundamental data request failed: {_result.status}"
                )
            self._on_response_cb(self, _result)

    def _parse_fields(self, fields):
        if is_string_type(fields):
            return [{fields: {}}]

        if type(fields) == dict:
            if len(fields) == 0:
                with "get_data error: fields list must not be empty" as error_msg:
                    self.error(error_msg)
                    raise ValueError(error_msg)
            return [fields]
        field_list = []
        if type(fields) == list:
            if len(fields) == 0:
                with "get_data error: fields list must not be empty" as error_msg:
                    self.error(error_msg)
                    raise ValueError(error_msg)
            for f in fields:
                if is_string_type(f):
                    field_list.append({f: {}})
                elif type(f) == dict:
                    field_list.append(f)
                else:
                    error_msg = "get_data error: the fields should be of type string or dictionary"
                    self.error(error_msg)
                    raise ValueError(error_msg)
            return field_list

        error_msg = "get_data error: the field parameter should be a string, a dictionary , or a list of strings|dictionaries"
        self.error(error_msg)
        raise ValueError(error_msg)

    @staticmethod
    def _get_data_value(value):
        if is_string_type(value):
            return value
        elif value is dict:
            return value["value"]
        else:
            return value


def build_dictionary(dic, name):
    if dic is None:
        raise ValueError(
            name + " is None, it must be a string or a dictionary of strings"
        )

    if is_string_type(dic):
        return json.loads(dic)
    elif type(dic) is dict:
        return dic
    else:
        raise ValueError(name + " must be a string or a dictionary")


def _convert_fundamental_json_to_pandas(json_fundamental_data, use_title):
    if "headers" not in json_fundamental_data:
        return None
    if use_title:
        _fields = [field["title"] for field in json_fundamental_data["headers"]]
    else:
        _fields = [field["name"] for field in json_fundamental_data["headers"]]
    fundamental_dataframe = None
    _data = json_fundamental_data["data"]
    if _data:
        # build numpy array with all datapoints
        _numpy_array = numpy.array(_data)
        fundamental_dataframe = pd.DataFrame(_numpy_array, columns=_fields)
        if not fundamental_dataframe.empty:
            fundamental_dataframe = (
                fundamental_dataframe.convert_dtypes()
            )  # convert_string=False)
    else:
        fundamental_dataframe = pd.DataFrame([], columns=_fields)

    return fundamental_dataframe

    # @staticmethod
    # def _get_data_frame(data_dict, field_name=False):
    #     if field_name:
    #         headers = [header.get('field', header.get('displayName')) for header in data_dict['headers'][0]]
    #     else:
    #         headers = [header['displayName'] for header in data_dict['headers'][0]]
    #     data = numpy.array([[Fundamental._get_data_value(value) for value in row] for row in data_dict['data']])
    #     df = pd.DataFrame(data, columns=headers)
    #     df = df.convert_dtypes()  # convert_string=False)
    #     errors = get_json_value(data_dict, 'error')
    #     return df, errors
