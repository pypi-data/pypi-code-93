# pylint: disable=missing-docstring,no-self-use,line-too-long

import unittest
from unittest.mock import patch, call, MagicMock
from typing import NamedTuple, Optional, Dict
from json import dumps
from urllib.parse import urlparse, parse_qs
import numpy  # type: ignore
import pandas  # type: ignore
from soil.data_structure import DS_NAMESPACE
import soil


class MockHttpResponse(NamedTuple):
    """Soil configuration class"""

    status_code: int
    text: str


# pylint: disable=unused-argument
def mock_http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, str]] = None,
) -> MockHttpResponse:
    assert json is not None
    response = {"_id": "mock_id", "type": json["type"]}
    return MockHttpResponse(status_code=201, text=dumps(response))


# pylint: disable=unused-argument, too-many-return-statements
def mock_http_get(
    url: str, headers: Optional[Dict[str, str]] = None
) -> MockHttpResponse:
    url_parts = urlparse(url)
    query_params = parse_qs(url_parts.query)
    if (
        url_parts.path == "/v2/states/"
        and query_params["name"][0] == "non_existing_alias_but_valid_id"
    ):
        return MockHttpResponse(status_code=200, text=dumps([]))
    if (
        url_parts.path == "/v2/states/"
        and query_params["name"][0] == "invalid_alias_invalidid"
    ):
        return MockHttpResponse(status_code=200, text=dumps([]))
    if url_parts.path == "/v2/states/" and query_params["name"][0] == "valid_alias":
        return MockHttpResponse(status_code=200, text=dumps([{"_id": "alias_id"}]))
    if url_parts.path == "/v2/states/alias_id/":
        result = {"state": {"result_id": "non_existing_alias_but_valid_id"}}
        return MockHttpResponse(status_code=200, text=dumps(result))
    if url_parts.path == "/v2/results/non_existing_alias_but_valid_id/":
        return MockHttpResponse(
            status_code=200,
            text=dumps({"_id": "mock_id", "type": "data_structures.some.test.type"}),
        )
    if url_parts.path == "/v2/results/invalid_alias_invalidid/":
        return MockHttpResponse(
            status_code=404,
            text=dumps(
                {"message": "Document with id invalid_alias_invalidid not found"}
            ),
        )
    raise Exception("mock http case not found")


@patch("soil.api.requests.get", side_effect=mock_http_get)
@patch("soil.api.requests.post", side_effect=mock_http_post)
class TestData(unittest.TestCase):
    def test_upload_data_object_list(
        self, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data([1, 2, 3, 4])
        assert data.id == "mock_id"
        assert data.sym_id is None
        assert data.dstype == DS_NAMESPACE + "list.List"
        assert object.__getattribute__(data, "data") is None
        assert object.__getattribute__(data, "metadata") is None
        assert data.pipeline is None
        mock_post.assert_called_once_with(
            "http://test_host.test/v2/results/",
            headers={"Authorization": "Bearer test_token"},
            json={
                "type": "soil.data_structures.predefined.list.List",
                "data": "[1, 2, 3, 4]",
                "metadata": None,
            },
        )  # NOQA
        assert mock_get.call_count == 0

    def test_upload_data_object_dict(
        self, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data({"test": "dictionary", "value": 11})
        assert data.id == "mock_id"
        assert data.sym_id is None
        assert data.dstype == DS_NAMESPACE + "dict.Dict"
        assert object.__getattribute__(data, "data") is None
        assert object.__getattribute__(data, "metadata") is None
        assert data.pipeline is None
        mock_post.assert_called_once_with(
            "http://test_host.test/v2/results/",
            headers={"Authorization": "Bearer test_token"},
            json={
                "type": "soil.data_structures.predefined.dict.Dict",
                "data": '{"test": "dictionary", "value": 11}',
                "metadata": None,
            },
        )  # NOQA
        assert mock_get.call_count == 0

    def test_upload_data_object_numpy(
        self, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data(numpy.array([[1, 2], [3, 4]]))
        assert data.id == "mock_id"
        assert data.sym_id is None
        assert data.dstype == DS_NAMESPACE + "ndarray.Ndarray"
        assert object.__getattribute__(data, "data") is None
        assert object.__getattribute__(data, "metadata") is None
        assert data.pipeline is None
        mock_post.assert_called_once_with(
            "http://test_host.test/v2/results/",
            headers={"Authorization": "Bearer test_token"},
            json={
                "type": "soil.data_structures.predefined.ndarray.Ndarray",
                "data": "[[1, 2], [3, 4]]",
                "metadata": None,
            },
        )  # NOQA
        assert mock_get.call_count == 0

    def test_upload_data_object_pandas(
        self, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data(pandas.DataFrame(data={"col1": [1, 2], "col2": [3, 4]}))
        assert data.id == "mock_id"
        assert data.sym_id is None
        assert data.dstype == DS_NAMESPACE + "pd_data_frame.PdDataFrame"
        assert object.__getattribute__(data, "data") is None
        assert object.__getattribute__(data, "metadata") is None
        assert data.pipeline is None
        mock_post.assert_called_once_with(
            "http://test_host.test/v2/results/",
            headers={"Authorization": "Bearer test_token"},
            json={
                "type": "soil.data_structures.predefined.pd_data_frame.PdDataFrame",
                "data": '{"col1":{"0":1,"1":2},"col2":{"0":3,"1":4}}',
                "metadata": None,
            },
        )  # NOQA
        assert mock_get.call_count == 0

    def test_get_data_valid_id(self, mock_post: MagicMock, mock_get: MagicMock) -> None:
        data = soil.data("non_existing_alias_but_valid_id")
        assert data.id == "mock_id"
        assert data.sym_id is None
        assert data.dstype == "data_structures.some.test.type"
        assert object.__getattribute__(data, "data") is None
        assert object.__getattribute__(data, "metadata") is None
        assert data.pipeline is None
        assert mock_post.call_count == 0
        assert mock_get.call_count == 2
        mock_get.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/?name=non_existing_alias_but_valid_id&with-roles",
                    headers={"Authorization": "Bearer test_token"},
                ),
                call(
                    "http://test_host.test/v2/results/non_existing_alias_but_valid_id/",
                    headers={"Authorization": "Bearer test_token"},
                ),
            ]
        )

    def test_get_data_valid_alias(
        self, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data("valid_alias")
        data = soil.data("non_existing_alias_but_valid_id")
        assert data.id == "mock_id"
        assert data.sym_id is None
        assert data.dstype == "data_structures.some.test.type"
        assert object.__getattribute__(data, "data") is None
        assert object.__getattribute__(data, "metadata") is None
        assert data.pipeline is None
        assert mock_post.call_count == 0
        assert mock_get.call_count == 5
        mock_get.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/?name=valid_alias&with-roles",
                    headers={"Authorization": "Bearer test_token"},
                ),
                call(
                    "http://test_host.test/v2/states/alias_id/",
                    headers={"Authorization": "Bearer test_token"},
                ),
                call(
                    "http://test_host.test/v2/results/non_existing_alias_but_valid_id/",
                    headers={"Authorization": "Bearer test_token"},
                ),
                call(
                    "http://test_host.test/v2/states/?name=non_existing_alias_but_valid_id&with-roles",
                    headers={"Authorization": "Bearer test_token"},
                ),
                call(
                    "http://test_host.test/v2/results/non_existing_alias_but_valid_id/",
                    headers={"Authorization": "Bearer test_token"},
                ),
            ]
        )

    def test_get_data_invalid_alias(
        self, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        self.assertRaises(Exception, soil.data, "invalid_alias_invalidid")
        assert mock_post.call_count == 0
        assert mock_get.call_count == 2
        mock_get.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/?name=invalid_alias_invalidid&with-roles",
                    headers={"Authorization": "Bearer test_token"},
                ),
                call(
                    "http://test_host.test/v2/results/invalid_alias_invalidid/",
                    headers={"Authorization": "Bearer test_token"},
                ),
            ]
        )
