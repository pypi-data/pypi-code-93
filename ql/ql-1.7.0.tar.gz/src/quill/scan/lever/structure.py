from .tokens import Suffix, Prefix, tokenise_line

__all__ = ["Doc", "BlockDoc", "NodeBlock"]

class BlockDoc:
    """
    Document formed by a list of one or more `NodeBlock` elements,
    created upon reading file lines (newlines will be stripped).
    """

    def __init__(self, lines):
        self._initblocks(lines)

    def _add_nodeblock(self, lines, line_no, block_no):
        self.blocks.append(NodeBlock(lines, line_no, block_no))

    def _initblocks(self, doc_lines):
        doc_lines = [l.rstrip("\n") for l in doc_lines]
        self.blocks = []
        current_line_block = []
        for line_no, l in enumerate(doc_lines):
            if l == "" and current_line_block:
                self._add_nodeblock(current_line_block, line_no, self.n_blocks)
                current_line_block = []
            else:
                current_line_block.append(l)
        if current_line_block:
            self._add_nodeblock(current_line_block, line_no+1, self.n_blocks)

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        self._blocks = blocks

    @property
    def n_blocks(self):
        return len(self.blocks)

    def __repr__(self):
        s = "s" if (self.n_blocks != 1) else ""
        return f"Document of {self.n_blocks} block{s}"

class NodeBlock:
    def __init__(self, block_lines, line_no, block_no):
        self._nodes = []  # private property
        self.start_line = line_no - len(block_lines) + 1
        self.end_line = line_no
        self.number = block_no
        self.tokenise_lines(block_lines)

    @property
    def nodes(self):
        return self._nodes

    def add_node(self, node):
        self._nodes.append(node)

    @property
    def _nodecount(self):
        return len(self.nodes)

    def __repr__(self):
        return (f"Block {self.number} of {self._nodecount} "
                f"nodes (L{self.start_line}-L{self.end_line})")

    def tokenise_lines(self, block_lines):
        "Populate nodes property"
        if block_lines[0].endswith("\n"):
            raise ValueError("Strip off newlines before passing into `NodeBlock`!")
        tokenised = []
        for i, l in enumerate(block_lines):
            line_no = self.start_line + i
            n = tokenise_line(l, line_no, self.number, seen=tokenised)
            tokenised.append(n)
        # Since preceding lines' nodes are modified in the processing
        # of subsequent lines, only add nodes to block after finishing.
        for node in tokenised:
            self.add_node(node)
        return
