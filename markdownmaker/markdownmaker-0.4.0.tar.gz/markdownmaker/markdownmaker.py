from typing import Union, Sequence

from markdownmaker.document import *

# Typing aliases
InlineNodeType = Union[InlineNode, str]
NodeType = Union[Node, str]


def _write(node: NodeType, document: Document):
    if isinstance(node, (str, InlineNode)):
        return str(node)
    elif isinstance(node, BlockNode):
        return node.write(document)


def _write_inline(node: InlineNodeType):
    if isinstance(node, str):
        return str(node)
    else:
        return node.write()


class Optional(BlockNode):
    """Node that will be filled with content later but must be added
    to the document before the content is available."""
    def __init__(self):
        self.content: NodeType = ""

    def write(self, document: Document) -> str:
        return _write(self.content, document)


class Paragraph(BlockNode):
    def __init__(self, content: NodeType):
        self.content = content

    def write(self, document: Document) -> str:
        return f"{_write(self.content, document)}\n\n"


class HorizontalRule(BlockNode):
    def write(self, document: Document) -> str:
        return "---\n"


class UnorderedList(ListNode):
    def __init__(self, items: Sequence[NodeType]):
        super()
        self.items = items

    def write(self, document: Document) -> str:
        out = ""
        for item in self.items:
            if isinstance(item, ListNode):
                document.indent_level += 1
                out += _write(item, document)
                document.indent_level -= 1

            else:
                out += f"{' ' * Document.indent_spaces * document.indent_level}- {item}\n"

        if document.indent_level > 0:
            return out
        return out + "\n"


class OrderedList(ListNode):
    def __init__(self, items: Sequence[NodeType]):
        super()
        self.items = items

    def write(self, document: Document) -> str:
        out = ""
        index = 1
        for item in self.items:
            if isinstance(item, ListNode):
                document.indent_level += 1
                with set_indent_spaces(document, len(str(index)) + 2):
                    out += _write(item, document)
                document.indent_level -= 1

            else:
                out += f"{' ' * Document.indent_spaces * document.indent_level}{index}. {item}\n"
                # Only increase if we don't have a sublist
                index += 1

        if document.indent_level > 0:
            return out
        return out + "\n"


class Link(InlineNode):
    def __init__(self, label: str, url: str):
        super()
        self.label = label
        self.url = url

    def write(self) -> str:
        return f"[{self.label}]({self.url})"


class Image(BlockNode):
    def __init__(self, url: str, alt_text: str = ""):
        super()
        self.url = url
        self.alt_text = alt_text

    def write(self, document: Document) -> str:
        return f"\n![{self.alt_text}]({self.url})\n\n"


class InlineImage(InlineNode):
    def __init__(self, url: str, alt_text: str = ""):
        super()
        self.url = url
        self.alt_text = alt_text

    def write(self) -> str:
        return f"![{self.alt_text}]({self.url})"


class CodeBlock(BlockNode):
    def __init__(self, code: str, language: str = ''):
        super()
        self.code = code
        self.language = language

    def write(self, document: Document) -> str:
        return f"```{self.language}\n{self.code}\n```\n"


class InlineCode(InlineNode):
    def __init__(self, code: str):
        super()
        self.code = code

    def write(self) -> str:
        return f"`{self.code}`"


class Quote(BlockNode):
    def __init__(self, content: NodeType):
        super()
        self.content = content

    def write(self, document: Document) -> str:
        return "> " + "\n> ".join(_write(self.content, document).splitlines()) + "\n\n"


class Bold(InlineNode):
    def __init__(self, content: InlineNodeType):
        super()
        self.content = content

    def write(self) -> str:
        return f"**{_write_inline(self.content)}**"


class Italic(InlineNode):
    def __init__(self, content: InlineNodeType):
        super()
        self.content = content

    def write(self) -> str:
        return f"*{_write_inline(self.content)}*"


class Header(BlockNode):
    content_str: str

    def __init__(self, content: InlineNodeType):
        super()
        self.content = content

    def write(self, document: Document) -> str:
        return f"{'#' * document.header_level} {_write_inline(self.content)}\n"


class HeaderSubLevel:
    def __init__(self, document: Document, steps: int = 1):
        self.document = document
        self.steps = steps

    def __enter__(self):
        self.document.header_level += self.steps

    def __exit__(self, exc_type, exc_val, exc_traceback):
        self.document.header_level -= self.steps


class ListSubLevel:
    def __init__(self, document: Document):
        self.document = document

    def __enter__(self):
        self.document.indent_level += 1

    def __exit__(self, exc_type, exc_val, exc_traceback):
        self.document.indent_level -= 1
