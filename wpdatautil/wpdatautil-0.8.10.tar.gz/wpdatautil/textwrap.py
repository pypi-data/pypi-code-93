"""textwrap utilities."""
import textwrap


def indent4(text: str, *, levels: int) -> str:
    """Indent the given string by the specified number of levels."""
    return textwrap.indent(text, prefix=" " * 4 * levels)
