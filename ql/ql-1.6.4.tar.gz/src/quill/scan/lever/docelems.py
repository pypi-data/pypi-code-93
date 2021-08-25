from .elems import BaseElem

__all__ = ["DocElem", "DocLists"]

class DocElem(BaseElem):
    """
    Base class for any doc-level element. Initialised as either
    a list of `Node` objects (stored as the `nodes` attribute) or
    a list of objects which themselves have a `nodes` attribute
    (stored as the `items` attribute).
    """
    def __init__(self, nodes=None, nodelists=None):
        super().__init__(nodes, nodelists)

class DocLists(DocElem, list):
    """
    A doc-level 'holder' for block-level [by definition] lists,
    providing access to the union (over all blocks in the Doc)
    of blocks' lines' output from parsing the block nodes to
    lists (however there is no need to confine the lists to
    block-level features after they have been parsed as such).
    """
    # TODO: wasteful to store nodes twice: just store index for header/list items
    # i.e. some 'view' on nodes, not a duplicate copy of the nodes
    def __init__(self, nodelists):
        super().__init__()
        self.extend(nodelists)

    @property
    def repr_str(self):
        n_lists = len(self)
        s = "s" if n_lists > 1 else ""
        return f"{n_lists} list{s}"

# Example use case
class DocHeaderTree(DocElem):
    """
    A doc-level header tree could be a hierarchy of header nodes.
    """
    def __init__(self, nodelist):
        super().__init__(nodelist)
