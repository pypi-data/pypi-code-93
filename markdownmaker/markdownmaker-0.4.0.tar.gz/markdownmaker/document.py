from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import List, Tuple, Union


class Node:
    """Base class of all nodes."""
    pass


class BlockNode(Node, ABC):
    """A node that can't be inlined and usually represents a block."""
    @abstractmethod
    def write(self, document: 'Document') -> str:
        return ""

    def __str__(self) -> str:
        raise TypeError("Block nodes cannot be inlined!")


class InlineNode(Node, ABC):
    """A node which consists only of one line."""
    @abstractmethod
    def write(self) -> str:
        return ""

    def __str__(self) -> str:
        return self.write()


class ListNode(BlockNode, ABC):
    """A node representing a list."""
    pass


class Document:
    indent_spaces = 2
    """Amount of spaces used for indentation. For item blocks in lists,
    this must be larger than the list marker:
    https://github.github.com/gfm/#example-232"""

    def __init__(self):
        self.header_level = 1
        self.indent_level = 0

        self.nodes: List[Tuple[int, Node]] = []

        self.current_node: Union[Document, Node] = self

    def add(self, node: Node) -> None:
        if self.current_node == self:
            self.nodes.append((self.header_level, node))
        else:
            self.current_node.add(node)

    def write(self) -> str:
        out = ""
        for h_level, node in self.nodes:
            self.header_level = h_level
            if isinstance(node, (str, InlineNode)):
                out += f"{node}\n"
            elif isinstance(node, BlockNode):
                out += node.write(self)

        return out


@contextmanager
def set_indent_spaces(document: Document, spaces: int):
    old = document.indent_spaces
    document.indent_spaces = spaces
    try:
        yield
    finally:
        document.indent_spaces = old
