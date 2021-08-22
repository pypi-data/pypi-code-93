import enum


class EncodingType(str, enum.Enum):
    SERIAL = "SERIAL"
    NODES = "NODES"
    DICKE = "DICKE"
