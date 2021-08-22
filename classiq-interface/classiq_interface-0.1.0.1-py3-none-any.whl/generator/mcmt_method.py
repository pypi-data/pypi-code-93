import enum


class McmtMethod(str, enum.Enum):
    vchain = "vchain"
    recursive = "recursive"
    standard = "standard"
