from enum import Enum
from yarl import URL
from .exceptions import UnavailableTag
from dataclasses import dataclass
from typing import List, Any

__all__ = [
    "AccountFields",
    "Account",
    "Page"
]


class AccountFields(Enum):

    short_name = "short_name"
    author_name = "author_name"
    author_url = "author_url"
    auth_url = "auth_url"
    page_count = "page_count"

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Account:
    short_name: str = None
    author_name: str = None
    author_url: URL = None
    access_token: str = None
    auth_url: URL = None
    page_count: int = None


@dataclass(frozen=True)
class Page:
    path: str
    url: URL
    title: str
    description: str
    author_name: str = None
    author_url: URL = None
    image_url: URL = None
    content: list = None
    html_content: str = None
    views: int = 0
    can_edit: bool = None
