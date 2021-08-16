"""Models."""

import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .formatter import format_extract_html, format_img, format_link, format_title


@dataclass  # type: ignore
class Page(ABC):
    """Metadata of a wiki page."""

    title: str
    link: str
    lang: str

    @abstractmethod
    def format(self) -> str:
        """Format the page to print it on the terminal."""


@dataclass
class MainPage(Page):
    """The main page."""

    def format(self) -> str:
        """Format a standard article."""
        ret = format_title(self.title)
        ret += format_link(self.link)

        return ret


@dataclass
class StandardArticle(Page):
    """A standard article."""

    image: typing.Optional[str]
    extract_html: str

    def format(self) -> str:
        """Format a standard article."""
        ret = format_img(self.image)
        ret += format_title(self.title)
        ret += format_extract_html(self.extract_html)
        ret += "\n\n"
        ret += format_link(self.link)

        return ret


@dataclass
class DisambiguationPage(Page):
    """A disambiguation page."""

    extract_html: str

    def format(self) -> str:
        ret = format_title(self.title)
        ret += format_extract_html(self.extract_html)
        ret += "\n\n"
        ret += format_link(self.link)

        return ret
