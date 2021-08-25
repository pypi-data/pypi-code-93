class BaseElem:
    "Base class for any element (both block-level and doc-level)."
    def __init__(self, nodes=None, nodelists=None):
        if nodes:
            self.nodes = nodes
        elif nodelists:
            self.items = nodelists
