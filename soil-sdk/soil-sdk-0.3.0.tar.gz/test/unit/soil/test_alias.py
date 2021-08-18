# pylint: disable=missing-docstring,no-self-use,line-too-long
from typing import NamedTuple, Optional, Dict
import unittest
from unittest.mock import patch, call, MagicMock
from urllib.parse import urlparse, parse_qs
from json import dumps
import soil
from soil.data_structure import DataStructure


class MockHttpResponse(NamedTuple):
    """Soil configuration class"""

    status_code: int
    text: str


def set_id(self: DataStructure) -> None:
    self.id = "mock_id"


# pylint: disable=unused-argument
def mock_http_patch(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, str]] = None,
) -> MockHttpResponse:
    assert json is not None
    return MockHttpResponse(status_code=200, text=dumps({}))


# pylint: disable=unused-argument
def mock_http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, str]] = None,
) -> MockHttpResponse:
    assert json is not None
    url_parts = urlparse(url)
    if url_parts.path == "/v2/results/":
        response = {"_id": "mock_id", "type": json["type"]}
        return MockHttpResponse(status_code=201, text=dumps(response))
    if url_parts.path == "/v2/states/":
        return MockHttpResponse(status_code=200, text=dumps({}))
    raise Exception("mock http case not found")


# pylint: disable=unused-argument
def mock_http_get(
    url: str, headers: Optional[Dict[str, str]] = None
) -> MockHttpResponse:
    url_parts = urlparse(url)
    query_params = parse_qs(url_parts.query)
    if url_parts.path == "/v2/states/" and query_params["name"][0] == "test_alias":
        return MockHttpResponse(status_code=200, text=dumps([]))
    raise Exception("mock http case not found")


# pylint: disable=unused-argument
def mock_http_get2(
    url: str, headers: Optional[Dict[str, str]] = None
) -> MockHttpResponse:
    url_parts = urlparse(url)
    query_params = parse_qs(url_parts.query)
    if url_parts.path == "/v2/states/" and query_params["name"][0] == "valid_alias":
        return MockHttpResponse(status_code=200, text=dumps([{"_id": "alias_id"}]))
    if url_parts.path == "/v2/states/alias_id/":
        result = {
            "_id": "alias_id",
            "state": {"result_id": "non_existing_alias_but_valid_id"},
        }
        return MockHttpResponse(status_code=200, text=dumps(result))
    raise Exception("mock http case not found")


class TestAlias(unittest.TestCase):
    @patch("soil.api.requests.get", side_effect=mock_http_get)
    @patch("soil.api.requests.post", side_effect=mock_http_post)
    @patch("soil.api.requests.patch", side_effect=mock_http_patch)
    def test_alias_new(
        self, mock_patch: MagicMock, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data([1, 2, 3, 4])
        soil.alias("test_alias", data)
        mock_get.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/?name=test_alias&with-roles",
                    headers={"Authorization": "Bearer test_token"},
                )
            ]
        )
        mock_post.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/results/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "type": "soil.data_structures.predefined.list.List",
                        "data": "[1, 2, 3, 4]",
                        "metadata": None,
                    },
                ),
                call(
                    "http://test_host.test/v2/states/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "name": "test_alias",
                        "state": {"alias": "test_alias", "result_id": "mock_id"},
                    },
                ),
            ]
        )
        assert mock_patch.call_count == 0

    @patch("soil.api.requests.get", side_effect=mock_http_get2)
    @patch("soil.api.requests.post", side_effect=mock_http_post)
    @patch("soil.api.requests.patch", side_effect=mock_http_patch)
    def test_alias_existing(
        self, mock_patch: MagicMock, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data([1, 2, 3, 4])
        soil.alias("valid_alias", data)
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
            ]
        )
        mock_post.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/results/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "type": "soil.data_structures.predefined.list.List",
                        "data": "[1, 2, 3, 4]",
                        "metadata": None,
                    },
                )
            ]
        )
        mock_patch.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/alias_id/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "name": "valid_alias",
                        "state": {"alias": "valid_alias", "result_id": "mock_id"},
                    },
                )
            ]
        )

    @patch("soil.api.requests.get", side_effect=mock_http_get2)
    @patch("soil.api.requests.post", side_effect=mock_http_post)
    @patch("soil.api.requests.patch", side_effect=mock_http_patch)
    def test_alias_data_structure(
        self, mock_patch: MagicMock, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        with patch.object(
            DataStructure, "get_id", side_effect=set_id, autospec=True
        ) as mock_get_data:
            data = DataStructure(dstype="data_structures.some.test.type")
            soil.alias("valid_alias", data)
            assert mock_get_data.call_count == 1
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
            ]
        )
        assert mock_post.call_count == 0
        mock_patch.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/alias_id/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "name": "valid_alias",
                        "state": {"alias": "valid_alias", "result_id": "mock_id"},
                    },
                )
            ]
        )

    @patch("soil.api.requests.get", side_effect=mock_http_get2)
    @patch("soil.api.requests.post", side_effect=mock_http_post)
    @patch("soil.api.requests.patch", side_effect=mock_http_patch)
    def test_alias_roles(
        self, mock_patch: MagicMock, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        with patch.object(
            DataStructure, "get_id", side_effect=set_id, autospec=True
        ) as mock_get_data:
            data = DataStructure(dstype="data_structures.some.test.type")
            soil.alias("valid_alias", data, roles=["test"])
            assert mock_get_data.call_count == 1
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
            ]
        )
        assert mock_post.call_count == 0
        mock_patch.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/alias_id/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "name": "valid_alias",
                        "state": {"alias": "valid_alias", "result_id": "mock_id"},
                        "roles": ["test"],
                    },
                ),
                call(
                    "http://test_host.test/v2/results/mock_id/",
                    headers={"Authorization": "Bearer test_token"},
                    json={"roles": ["test"]},
                ),
            ]
        )

    @patch("soil.api.requests.get", side_effect=mock_http_get)
    @patch("soil.api.requests.post", side_effect=mock_http_post)
    @patch("soil.api.requests.patch", side_effect=mock_http_patch)
    def test_alias_new_with_roles(
        self, mock_patch: MagicMock, mock_post: MagicMock, mock_get: MagicMock
    ) -> None:
        data = soil.data([1, 2, 3, 4])
        soil.alias("test_alias", data, roles=["test1", "test2"])
        mock_get.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/states/?name=test_alias&with-roles",
                    headers={"Authorization": "Bearer test_token"},
                )
            ]
        )
        mock_post.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/results/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "type": "soil.data_structures.predefined.list.List",
                        "data": "[1, 2, 3, 4]",
                        "metadata": None,
                    },
                ),
                call(
                    "http://test_host.test/v2/states/",
                    headers={"Authorization": "Bearer test_token"},
                    json={
                        "name": "test_alias",
                        "state": {"alias": "test_alias", "result_id": "mock_id"},
                        "roles": ["test1", "test2"],
                    },
                ),
            ]
        )
        mock_patch.assert_has_calls(
            [
                call(
                    "http://test_host.test/v2/results/mock_id/",
                    headers={"Authorization": "Bearer test_token"},
                    json={"roles": ["test1", "test2"]},
                )
            ]
        )
