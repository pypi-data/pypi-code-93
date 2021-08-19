from typing import NamedTuple, Type, Union
import html

from .htmlclasses import E


def to_string(
        element: Type[E],
        *,
        indent: str = '',
        html_doctype: bool = True,
        ) -> str:
    """Serialize an E instance.

    Parameters
    ----------
    element: n/c.
    indent: If it's given the code will be indented accordingly.
    html_doctype: Whether to prepend the DOCTYPE html declaration.

    Returns
    -------
    Valid HTML string.
    """

    lines = _lines(element, doctype=html_doctype)
    if indent:
        return '\n'.join(
            indent * line.indent_level + line.text
            for line in lines
        )
    else:
        return ''.join(line.text for line in lines)


class IndentedLine(NamedTuple):

    text: str
    indent_level: int


def _lines(
        element: Union[Type[E], E, str],
        *,
        indent_level: int = 0,
        doctype: bool = False,
):
    # For the purpose of pretty formatted HTML it's convenient
    # for me to think of it in terms of collections of lines
    # with indent levels.
    if doctype:
        yield IndentedLine('<!DOCTYPE html>', indent_level)

    if isinstance(element, str):
        for line in element.splitlines():
            yield IndentedLine(html.escape(line), indent_level)
        return

    if isinstance(element, E):
        for e in element._subelements:
            for line in _lines(e, indent_level=indent_level):
                yield line
        return

    tag_name = element.__name__

    is_leaf = not element._trees_and_leaves
    tag_opening = _build_tag_opening(
            tag_name, is_leaf, element._element_attributes)
    tag_closing = _build_tag_closing(tag_name, is_leaf)

    if tag_name.lower() == 'pre':
        yield IndentedLine(
                _handle_pre(element, tag_opening, tag_closing),
                indent_level,
                )
        return

    yield IndentedLine(tag_opening, indent_level)
    for tree_or_leaf in element._trees_and_leaves:
        for indented_line in _lines(
                tree_or_leaf, indent_level=indent_level + 1):
            yield indented_line
    if tag_closing:
        yield IndentedLine(tag_closing, indent_level)


def _build_tag_opening(tag_name, is_leaf, attributes):
    attrs = ' '.join(
            f'{k}="{v}"'
            for k, v in attributes.items()
            )

    prefix = '<' + tag_name
    middle = ' ' + attrs if attrs else ''
    if is_leaf:
        suffix = '/>'
    else:
        suffix = '>'
    return prefix + middle + suffix


def _build_tag_closing(tag_name, is_leaf):
    if is_leaf:
        return ''
    else:
        return f'</{tag_name}>'


def _handle_pre(element, tag_opening, tag_closing):
    text_list = element._trees_and_leaves

    if not text_list or text_list == ['']:
        return tag_opening + tag_closing
    elif len(text_list) != 1 or not isinstance(text_list[0], str):
        raise NotImplementedError(
                f'Do now know what to do with {element}.'
                + ' Is it even legal HTML?'
        )
    else:
        text, = text_list
        return tag_opening + html.escape(text) + tag_closing
