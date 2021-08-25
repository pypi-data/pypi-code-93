from .parser import Doc

__all__ = ["MMD"]

class MMD(Doc):
    def __init__(self, mmd_lines, listparseconfig=None):
        super().__init__(mmd_lines, listparseconfig=listparseconfig)

    def __repr__(self):
        return f"Parsed MMD file ({self._doc_repr})"
