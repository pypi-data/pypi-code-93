from .elems import BaseElem

__all__ = ["BlockElem", "BlockList"]

class BlockElem(BaseElem):
    "Base class for any block-level element."
    #def __init__(self, nodelist):
    #    super().__init__(nodelist)

class BlockList(BlockElem):
    """
    A block-level list would be a list of `ListInit`-prefixed
    nodes and could have a `ListInit`-suffixed header node.

    If initialised in the midst of a different element type, pass its
    element type (block- or doc-level) through `parent_elem` argument.
    """
    def __init__(self, nodes, header=None, parent_elem=None):
        super().__init__(nodes) # once sublist of nodes determined
        self.header = header
        self.parent_elem = parent_elem

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, h):
        self._header = h

    @property
    def all_nodes(self):
        return [self.header, *self.nodes] if self.header else self.nodes

    def __repr__(self):
        headered = ("H" if self.header else "Unh") + "eadered"
        return f"{headered} list with {len(self.nodes)} items"
