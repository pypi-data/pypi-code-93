from aenum import NamedConstant
from ...__share__ import classproperty

__all__ = ["tokenise_line", "Prefix", "Suffix", "Node"]

def has_precedent(seen, prefix):
    """
    Check if there is a seen node with a given prefix.
    No need to do this for suffixes as their precedent only ever checked
    for directly preceding.
    """
    return any([n.prefix is prefix for n in seen])


def lever_config_dict():
    """
    Return default parser config.
    """
    return {
        # Permit `Prefix.ListInit` without directly preceding `Suffix.ListInit`
        "ALLOW_LIST_WITHOUT_SUFFIX_INIT": True,
    }


def tokenise_line(line, line_no, block_no, seen=None, config=None):
    """
    Follow rules for prefix and suffix token order, splitting
    the string into `(prefix, contents, suffix)`. Optionally
    specify `custom_config` dict to override defaults from
    `lever_config_dict`.
    """
    ############ Begin config instantation ###########
    default_config = lever_config_dict()
    if config:
        # Only allow custom config keys also present in default_config dict
        config = {k: v for k, v in config.items() if k in default_config}
        config = {**default_config, **config}  # override default config
    else:
        config = default_config
    ############## Read config variables ##############
    # TODO: just read into locals if config gets any more complicated
    ALLOW_LIST_WITHOUT_SUFFIX_INIT = config.get("ALLOW_LIST_WITHOUT_SUFFIX_INIT")
    ############# End config instantation #############
    seen = seen if seen else []  # avoid default mutable arg gotcha
    penultimate = seen[-1] if seen else None  # directly preceding
    node = Node(prefix=None, contents=line, suffix=None, line_no=line_no, block_no=block_no)
    if line == "":
        node.prefix = Prefix.BlankNode
    elif line.startswith("-:"):
        if line[2] == "'":
            node.prefix = Prefix.Because
        elif line[2] == ".":
            node.prefix = Prefix.Therefore
        elif penultimate:
            if penultimate.prefix is Prefix.Question:
                node.prefix = Prefix.Answer
                # Keep a record of the location of its paired node
                penultimate.paired_to = (block_no, line_no)
                node.paired_to = (penultimate.block_no, penultimate.line_no)
            elif penultimate.contents.endswith(":"):
                # Mark penultimate line's suffix as beginning a list
                penultimate.suffix = Suffix.InitList
                node.prefix = Prefix.InitList
            elif ALLOW_LIST_WITHOUT_SUFFIX_INIT:
                node.prefix = Prefix.InitList
            else:
                print(f"Falling through... {node.contents}")
        elif ALLOW_LIST_WITHOUT_SUFFIX_INIT:
            node.prefix = Prefix.InitList
        # (Question not implemented here)
    elif line.startswith("-?"):
        node.prefix = Prefix.Question
    elif line.startswith("-,"):
        if line[2] == ":" and has_precedent(seen, Prefix.InitList):
            # For now consider a list 'open' indefinitely while the block is
            # i.e. until blank line (TODO implement break at section divider)
            node.prefix = Prefix.ContList
        elif line[2] == ",":
            node.prefix = Prefix.Ascent
        elif line[2] == "?":
            node.prefix = Prefix.ContQuestion
        else:
            node.prefix = Prefix.FollowOn
    elif line.startswith("-."):
        if line[2] == ".":
            node.prefix = Prefix.Descent
        elif line[2] == ",":
            node.prefix = Prefix.ContDesc
    elif line.startswith("-#"):
        max_header = 8 # 1-based count of header levels
        start_at = len(Prefix.Header1.str)
        confirmed_levels = 1
        for i,l in enumerate(line[start_at : start_at + max_header]):
            if l != "#":
                break
            else:
                confirmed_levels += 1
        if confirmed_levels > max_header:
            raise ValueError(f"Can't parse header beyond level {max_header} ('{line}')")
        header_name = f"Header{confirmed_levels}"
        node.prefix = Prefix.token_from_name(header_name)
    elif line.startswith("-~==~-"):
        node.prefix = Prefix.SectBreak
    elif line.startswith("-"):
        node.prefix = Prefix.PlainNode
    else:
        raise ValueError(f"Unable to tokenise line: '{line}'")
    # If this succeeded without raising an error, make contents
    return node


class Affix(NamedConstant):
    """
    Affixes following the MMD 'lever' format specification.
    """

    @classmethod
    def name_from_tokenseq(cls, tok):
        """
        IN: the string matched by the token. OUT: the node name or
        a list of names if the token name is not unique.
        """
        matches = cls.tokseq2name_multidict.get(tok)
        if matched:
            if len(matched) == 1:
                [matched] = matched
        else:
            raise KeyError(f"{tok} not a valid Affix token sequence")
        return matched

    #@classproperty
    #def tokseq2name_dict(cls):
    #    "KEY: the string matched by the token. VAL: the node name."
    #    # N.B. does not assume the token-matching string is unique
    #    d = {k: v._value_ for k,v in Prefix.__members__.items()}
    #    return d

    @classproperty
    def tokseq2name_multidict(cls):
        "KEY: the string matched by the token(s). VAL: list of node name(s)."
        # N.B. does not assume the token-matching string is unique
        d = {
                v._value_: [
                    k
                    for k in cls._members_
                    if cls._members_.get(k)._value_ == v._value_
                ]
                for v in cls._members_.values()
            }
        return d

    @classmethod
    def token_from_name(cls, name):
        "IN: the node name. OUT: the token (a `NamedConstant` object)."
        return cls.name2tok_dict.get(name)

    @classproperty
    def name2tok_dict(cls):
        "KEY: the node name. VAL: the token (a `NamedConstant` object)."
        d = {v._name_: v for v in cls._members_.values()}
        return d

    @property
    def str(self):
        return self._value_

    def is_named(self, name):
        return self._name_ == name


class Prefix(Affix):
    """
    Prefixes following the MMD 'lever' format specification. Capital
    letters indicate token symbols [A to F, as well as G_ ('gap')].
    Headings levels 1-8 are named Ha through Hh. Empty lines are named Z_.
    Note that a blank line and a section break are given as a prefix although
    they each span the entire line (underscore indicates a 'terminating prefix').
    """

    PlainNode = "-"  # A or Cb [if line ends with colon and precedes C"
    FollowOn = "-,"  # Ac
    InitList = "-:"  # B [default: indicating a list]
    Answer = "-:"  # Cr [if penultimate line was C]
    ContList = "-,:"  # Bc
    Question = "-?"  # C
    ContQuestion = "-,?"  # Cc
    Descent = "-.."  # D
    ContDesc = "-.,"  # Dc
    Ascent = "-,,"  # Du
    Therefore = "-:."  # E
    Because = "-:'"  # F
    SectBreak = "-~==~-"  # G_
    Header1 = "-#" # Ha
    Header2 = "-##" # Hb
    Header3 = "-###" # Hc
    Header4 = "-####" # Hd
    Header5 = "-#####" # He
    Header6 = "-######" # Hf
    Header7 = "-#######" # Hg
    Header8 = "-########" # Hh
    BlankNode = "" # Z_


class Suffix(Affix):
    """
    Suffixes following the MMD 'lever' format specification'.
    """

    InitList = ":"

class Node:
    """
    Provide a simple string-repr while storing the Prefix and Suffix
    as properties (intervening `contents` is just a string for now).
    """

    def __init__(self, prefix=None, contents=None, suffix=None, line_no=None, block_no=None):
        self.prefix = prefix
        self.contents = contents
        self.suffix = suffix
        self.line_no = line_no
        self.block_no = block_no

    def __repr__(self):
        pre = self.prefix.str if self.prefix else ""
        con = self.contents if self.contents else ""
        suf = self.suffix.str if self.suffix else ""
        return f"{pre}{con}{suf}"

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, p):
        if hasattr(self, "_prefix"):
            # modifying an already set prefix so must also modify `self.contents`
            ex_prefix = self.prefix
            if ex_prefix:
                assert self.contents, "Tried to change prefix on contents-less Node"
                self.contents = ex_prefix.str + self.contents  # reconstitute
            if p:
                self.contents = self.contents[len(p.str) :]
        if p:
            assert isinstance(p, Prefix)  # either `None` or `Prefix` NamedConstant
        self._prefix = p

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, c):
        self._contents = c

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, s):
        if hasattr(self, "_suffix"):
            # modifying an already set suffix so must also modify `self.contents`
            ex_suffix = self.suffix
            if ex_suffix:
                assert self.contents, "Tried to change suffix on content-less Node"
                self.contents = self.contents + ex_suffix.str
            if s:
                self.contents = self.contents[: -len(s.str)]
        if s:
            assert isinstance(s, Suffix)  # either `None` or `Suffix` NamedConstant
        self._suffix = s
