import enum


class RelationshipDirection(enum.Enum):
    UNDIRECTED = "UNDIRECTED"
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"


class RelationshipCardinality(enum.Enum):
    NONE = "None"
    UNIQUE_STRICT = "UNIQUE_STRICT"  # one single relationship between the same two nodes
    UNIQUE_LABEL = "UNIQUE_LABEL"  # one single relationship between source and any node with target label

    @classmethod
    def get_mandatory_cardinalities(cls):
        return [
            cls.UNIQUE_STRICT,
            cls.UNIQUE_LABEL,
        ]
