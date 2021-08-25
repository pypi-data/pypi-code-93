from .structure import BlockDoc
from .blockelems import *  # temporary
from .docelems import DocLists
from .lists import parse_nodes_to_list, BlockList, SepBlockList
from pandas import DataFrame
from ...manifest.parsing import read_man, read_man_df
from ...fold.ns_util import ns
from .git import _has_clean_wt

__all__ = ["Doc"]

class PartsList(list):
    """
    Simple list class which provides a pandas DataFrame method which will be
    bound to the `Doc` instance (via a descriptor).
    """
    def __init__(self, parts, part_keys=None):
        self.extend(parts)
        self.part_keys = part_keys

    def as_df(self):
        datadict = {k: [n[i] for n in self] for (i,k) in enumerate(self.part_keys)}
        return DataFrame.from_dict(datadict)

class Doc(BlockDoc):
    def __init__(self, lines, listparseconfig=None):
        super().__init__(lines)  # block tokenisation pass, creating nodes property
        if listparseconfig is None:
            listparseconfig = {"listclass": BlockList}
        elif listparseconfig.get("listclass") == "auto":
            listparseconfig.update({"listclass": BlockList})
        elif "sep" in listparseconfig and "listclass" not in listparseconfig:
            # helper: do not require passing the list class itself, assume it from `sep`
            sep_listconfig_keys = ["sep", "headersep", "labels"]
            cfg = {k:v for (k,v) in listparseconfig.items() if k in sep_listconfig_keys}
            for k in sep_listconfig_keys:
                if k in listparseconfig:
                    del listparseconfig[k]
            listparseconfig.update({"listclass": SepBlockList, "listconfig": cfg})
        self._parse(listparseconfig)  # tokenised block parsing, creating lists property
        if hasattr(self, "all_parts") and self.all_parts.part_keys:
            self.as_df = self.all_parts.as_df
        if self.list:
            self.repos = property(read_man).__get__(self)
            self.repos_df = property(read_man_df).__get__(self)

    def _parse(self, listparseconfig=None):
        "May add other configs later, but for now just wrap the lists method."
        # populate the `lists` property by parsing all blocks' nodes
        self._parse_lists(**listparseconfig) # expand out dict as named arguments

    def _parse_lists(self, listclass=None, part_keys=None, listconfig=None,
            strict_list_breaks=True):
        """
        Note that for separator-delimited lists, `labels` (in `listconfig`) is for
        setting the names of node attributes of each delimited value, while
        `part_keys` sets column names on the pandas DataFrame.
        """
        # TODO strict_list_breaks param
        all_blocklists = []
        for block in self.blocks:
            nodes = block.nodes
            # yields blocklist objects
            bl_generator = parse_nodes_to_list(nodes, listconfig, listclass)
            blocklists = list(bl_generator)  # exhaust generator
            all_blocklists.extend(blocklists)  # flat list: all BlockList objects in Doc
        # `DocLists` object from list of BlockList objects
        self.lists = DocLists(all_blocklists)
        if listclass is SepBlockList:
            pk = part_keys
            # N.B. maybe use an Enum rather than have to pass actual class?
            self.all_parts = PartsList([
                n.parts
                for l in self.lists
                for n in (l.all_nodes if l.has_sep_header else l.nodes)
            ], part_keys=pk)
        # TODO: wasteful to store nodes twice: just store index for header/list items

    @property
    def lists(self):
        # What I really want here is the union, over all blocks in the Doc,
        # of each's block's lines' output from parse_nodes_to_list
        # which will probably necessitate a more complicated structure,
        # in some dedicated class which manages lists by block
        return self._lists

    @property
    def list(self):
        if len(self.lists) == 1:
            return self.lists[0]
        else:
            return None

    @lists.setter
    def lists(self, ll):
        self._lists = ll

    @property
    def _doc_repr(self):
        "Private property to enable access from MMD superclass"
        block_repr = super().__repr__()
        cont = ", containing "
        parsed_list_repr = self.lists.repr_str if self.lists else ""
        parsed_repr = f"{cont}{parsed_list_repr}" if self.lists else ""
        return f"{block_repr}{parsed_repr}"

    def __repr__(self):
        return self._doc_repr

    def check_manifest(self):
        domains = self.repos_df.domain
        self.repos_df["local"] = [domain in ns for domain in domains]
        self.repos_df["clean"] = [_has_clean_wt(d) for d in domains if d in ns]
