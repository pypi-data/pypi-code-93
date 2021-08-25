from .blockelems import BlockList
from .tokens import Prefix, Suffix
from pandas import DataFrame

__all__ = ["parse_nodes_to_list", "SepBlockList"]

def create_BlockList(nodes, has_header, listclass=BlockList, config=None):
    """
    Simple wrapper to turn boolean `has_header` into a header `Node` argument
    to the `BlockList` class constructor (or any substituted `BlockList` class).
    """
    header = nodes.pop(0) if has_header else None
    # for now only set up to handle `SepBlockList` config
    listclasscheck = listclass is SepBlockList
    if config and listclass is SepBlockList:
        sep = config.get("sep") if "sep" in config else ":"
        hsep = config.get("headersep") if "headersep" in config else False
        lab = config.get("labels") if "labels" in config else None
        return listclass(nodes, header, sep=sep, headersep=hsep, labels=lab)
    else:
        return listclass(nodes, header)

def parse_nodes_to_list(nodes, listconfig=None, listclass=BlockList):
    """
    Generator function which yields all lists per block, ignoring any intervening
    or pre/succeeding non-list nodes (except any directly preceding 'header' node,
    with a line-terminating colon marked as `Suffix.ListInit`).
    """
    nodes = nodes.copy() # do not modify input!
    list_open = list_header_open = False
    has_header = False
    parsed = [] # nodes belonging to a list go here
    while nodes: # unlike a for loop, allows passing any remaining `nodes` upon return
        node = nodes.pop(0)
        if list_open:
            # very crudely, just terminate on any non-list continuation item
            if node.prefix is Prefix.ContList:
                parsed.append(node)
            else:
                list_open = False # list terminates
                # a break here would skip any remaining nodes, requiring func recursion
                # to capture multiple lists per block, a yield is the preferable option
                yield create_BlockList(parsed, has_header, listclass, listconfig)
                has_header = False # reset this in case parsing another list in block
                parsed = []
        elif list_header_open:
            if node.prefix == Prefix.InitList:
                list_header_open = False
                list_open = True
                parsed.append(node)
        else:
            if node.suffix == Suffix.InitList:
                list_header_open = has_header = True
                parsed.append(node)
            elif node.prefix == Prefix.InitList:
                if list_header_open:
                    list_header_open = False
                list_open = True
                parsed.append(node)
    if parsed:
        yield create_BlockList(parsed, has_header, listclass, listconfig)

def _as_df(self, forbid_header=False):
    labels = self._labels
    nodes = self.all_nodes if self.has_sep_header and not forbid_header else self.nodes
    datadict = {label: [getattr(node, label) for node in nodes] for label in labels}
    return DataFrame.from_dict(datadict)

class SepBlockList(BlockList):
    """
    A structured variant of the `BlockList` block-level list, with a
    specified separator, to function in the manner of a CSV,
    optionally with the 'columns' named via the `labels` argument.

    Will not permit different numbers of values in the header (if the
    header exists but does not conform to the CSV format, `sep_header`
    can disable the attempt to validate the header node in this way).

    `tokenise_separated_values` implements an interface for setting
    attributes on the `SepBlockList` according to a given list of
    attribute names (TODO: method to create a dictionary from the list
    nodes, to then e.g. create a `pandas.DataFrame`).
    """
    def __init__(self, nodes, h=None, par=None, sep=":", headersep=False, labels=None):
        super().__init__(nodes, header=h, parent_elem=par)
        self.sep = sep
        self.has_sep_header = headersep
        self.tokenise_separated_values(labels) # sets `parts` attribute
        self._labels = labels
        if labels:
            self.as_df = _as_df.__get__(self)

    def tokenise_separated_values(self, sep_header_labels=None):
        n_parts = None
        if self.has_sep_header: # there should be a header, to be parsed for sep. values
            assert self.header, "Cannot parse header: list is unheadered"
            header_offset = 0
            if sep_header_labels:
                labsetcount = len(set(sep_header_labels))
                labsetcheck = labsetcount == labsetcount
                assert labsetcheck, f"{n_labels} labels =/= {labsetcount} values"
                assert "parts" not in sep_header_labels, "'parts' is a reserved label"
        elif self.header: # there is a header but not parsing for sep. values
            header_offset = 1
        else: # there is no header so nothing to skip
            header_offset = 0
        for node in self.all_nodes[header_offset:]:
            parts = node.contents.split(self.sep)
            if n_parts: # if sep. values count per node already set on first seen node
                lencheck = len(parts) == n_parts
                assert lencheck, f"{node} has {len(parts)} parts (expected {n_parts})"
            else:
                n_parts = len(parts)
                if sep_header_labels:
                    n_labels = len(sep_header_labels)
                    labcountcheck = n_labels == n_parts
                    assert labcountcheck, f"{n_labels} labels =/= {n_parts} values"
            if sep_header_labels:
                for label, val in zip(sep_header_labels, parts):
                    setattr(node, label, val)
            setattr(node, "parts", parts)
