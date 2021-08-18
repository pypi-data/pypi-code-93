import aiohttp
import functools
import json
import copy

from typing import Union, List
from yarl import URL

from .types import *
from .exceptions import TokenRequired, TelegraphException
from .html_parser import nodes_to_html, html_to_nodes


def token_required(function):
    @functools.wraps(function)
    async def wrapper(self, *args, **kwargs):
        if self.access_token is None:
            raise TokenRequired("Telegraph token is required to call this method.")

        return await function(self, *args, **kwargs)

    return wrapper


def remove_nones(data: dict) -> dict:
    return dict(filter(
        lambda item: item[1] is not None,
        data.items()
    ))


def str_values(data: dict) -> dict:
    return dict(map(
        lambda item: (item[0], str(item[1])),
        data.items()
    ))


def build_urls(data: dict, *keys) -> dict:
    url_or_none = lambda value: URL(value) if value is not None else None
    return dict(map(
        lambda pair: (pair[0], url_or_none(pair[1])) if pair[0] in keys else pair,
        data.items()
    ))


class TelegraphClient:
    API_URL = URL("https://api.telegra.ph/")

    def __init__(self, access_token: str = None):
        self.session = aiohttp.ClientSession()
        self._access_token = access_token

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Access token must be str")
        self._access_token = value

    async def request(self, method: str, **params):

        params = str_values(remove_nones(params))

        url = self.API_URL.with_path(method)

        async with self.session.post(url, data=params) as response:
            json_resp = await response.json()
            if json_resp.get("ok", False):
                return json_resp.get("result", {})
            else:
                raise TelegraphException(json_resp.get("error"))

    async def create_account(
            self,
            short_name: str,
            author_name: str = "",
            author_url: URL = None
    ) -> Account:
        json_response = await self.request(
            "createAccount",
            short_name=short_name,
            author_name=author_name,
            author_url=author_url
        )

        json_response = build_urls(json_response, 'author_url', 'auth_url')

        return Account(**json_response)

    @token_required
    async def edit_account_info(
            self,
            short_name: str = None,
            author_name: str = None,
            author_url: URL = None,
    ) -> Account:

        params = {
            "short_name": short_name,
            "author_name": author_name,
            "author_url": author_url,
            "access_token": self.access_token,
        }

        json_response = await self.request("editAccountInfo", **params)

        json_response = build_urls(json_response, 'author_url', 'auth_url')

        return Account(**json_response)

    @token_required
    async def get_account_info(self, fields: List[Union[AccountFields, str]] = None) -> Account:
        if fields is None:
            fields = [
                AccountFields.short_name,
                AccountFields.author_name,
                AccountFields.author_url
            ]

        json_fields = json.dumps(list(map(str, fields)))
        response = await self.request(
            "getAccountInfo",
            access_token=self.access_token,
            fields=json_fields
        )

        response = build_urls(response, 'author_url', 'auth_url')

        return Account(**response)

    async def close(self):
        await self.session.close()

    @token_required
    async def revoke_access_token(self, update_client_token=True) -> Account:
        response = await self.request("revokeAccessToken", access_token=self.access_token)
        account = Account(**response)
        if update_client_token:
            self.access_token = account.access_token

        return account

    async def get_views(
            self,
            path: str,
            year: int = None,
            month: int = None,
            day: int = None,
            hour: int = None
    ) -> int:
        params = {"hour": hour, "day": day, "month": month, "year": year}
        specified_before = -1

        for index, (dep_name, dep_value) in enumerate(params.items()):
            if dep_value is None and specified_before != -1:
                raise TelegraphException(
                    f"If you specifies {list(params.keys())[specified_before]}, "
                    f"you must specify {dep_name}"
                )
            if dep_value is not None:
                specified_before = index

        response = await self.request("getViews", path=path, **params)

        return response["views"]

    async def get_page(
        self,
        path: str,
        return_content=False,
        return_html_content=False
    ) -> Page:

        response = await self.request(
            "getPage",
            path=path,
            return_content=return_html_content or return_content)

        response = build_urls(response, 'author_url', 'url', 'image_url')

        if return_html_content:
            html_content = nodes_to_html(copy.deepcopy(response["content"]))
            response["html_content"] = html_content

        return Page(**response)

    @token_required
    async def get_page_list(self, offset: int = 0, limit: int = 50) -> List[Page]:
        if not (0 <= limit <= 200):
            raise ValueError("Limit must be in range 1-200")

        response = await self.request("getPageList",
                                      offset=offset,
                                      limit=limit,
                                      access_token=self.access_token)

        pages = list(map(lambda p: build_urls(p, 'author_url', 'url', 'image_url'), response["pages"]))

        return list(map(lambda page: Page(**page), response["pages"]))

    @token_required
    async def create_page(
            self,
            title: str,
            author_name: str = None,
            author_url: str = None,
            content: dict = None,
            html_content: str = None,
            return_content=False,
            return_html_content=False,
    ) -> Page:

        if html_content is not None and content is not None:
            raise ValueError(
                "You must specify either `html_content` or `content`, not both."
            )

        if html_content is not None:
            content = html_to_nodes(html_content)

        content = json.dumps(content)

        response = await self.request(
            "createPage",
            access_token=self.access_token,
            title=title,
            author_name=author_name,
            author_url=author_url,
            content=content,
            return_content=return_content or return_html_content
        )

        if return_html_content:
            html_content = nodes_to_html(copy.deepcopy(response["content"]))
            response["html_content"] = html_content

        return Page(**response)

    @token_required
    async def edit_page(
            self,
            path: str,
            title: str,
            author_name: str = None,
            author_url: str = None,
            content: dict = None,
            html_content: str = None,
            return_content=False,
            return_html_content=False,
    ) -> Page:

        if html_content is not None and content is not None:
            raise ValueError(
                "You must specify either `html_content` or `content`, not both."
            )

        if html_content is not None:
            content = html_to_nodes(html_content)

        content = json.dumps(content)

        response = await self.request(
            "editPage",
            access_token=self.access_token,
            path=path,
            title=title,
            author_name=author_name,
            author_url=author_url,
            content=content,
            return_content=return_content or return_html_content
        )

        if return_html_content:
            html_content = nodes_to_html(copy.deepcopy(response["content"]))
            response["html_content"] = html_content

        return Page(**response)
