"""Format pages."""

# pylint: disable=R0911

import typing

import termcolor
from bs4 import BeautifulSoup


def format_title(title: str) -> str:
    """Format the title of a page."""

    return termcolor.colored(title, attrs=["bold"]) + "\n\n"


def format_link(link: str) -> str:
    """Format the link of a page."""

    return termcolor.colored(
        link,
        color="blue",
        attrs=["underline"],
    )


def format_img(img: typing.Optional[str]) -> str:
    """Format an ascii image."""

    if img:
        return img + "\n"

    #  termcolor.cprint('No Image', color='grey', file=sys.stderr)

    return ""


def html_formatter_walk(root, prefix="") -> str:
    """Format html."""

    if not root:
        return ""

    if root.name in (
        "html",
        "body",
        "span",
        "[document]",
    ):
        return "".join(html_formatter_walk(bit) for bit in root).strip()

    if root.name == "p":
        return "".join(html_formatter_walk(bit) for bit in root) + f"\n{prefix}"

    if root.name in ("b", "strong"):
        return termcolor.colored(
            "".join(html_formatter_walk(bit) for bit in root),
            attrs=["bold"],
        )

    if root.name in ("i", "em"):
        return termcolor.colored(
            "".join(html_formatter_walk(bit, prefix=prefix) for bit in root),
            attrs=["italic"],
        )

    if root.name == "ul":
        return "\n" + "".join(
            html_formatter_walk(bit, prefix=prefix + "  ") for bit in root
        )

    if root.name == "br":
        return f"\n{prefix}"

    if root.name == "li":
        return (
            f"{prefix}- "
            + "".join(html_formatter_walk(bit, prefix=prefix + "  ") for bit in root)
            + "\n"
        )

    if root.name is None:
        if str(root) == "\n":
            return ""

        return str(root).replace("\n", f"\n{prefix}")

    return root.string


def format_extract_html(extract_html: str) -> str:
    """Format extract_html."""
    soup = BeautifulSoup(extract_html, parser="html.parser", features="lxml")

    return html_formatter_walk(soup).strip()
