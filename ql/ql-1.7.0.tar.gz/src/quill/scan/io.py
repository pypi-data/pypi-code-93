from .lever import MMD

__all__ = ["mmd"]

def mmd(filepath, listparseconfig=None):
    with open(filepath) as f:
        mmd_lines = f.readlines()
    return MMD(mmd_lines, listparseconfig=listparseconfig)
