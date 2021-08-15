from enum import Enum

__all__ = ("GraphQLOperationType",)


class GraphQLOperationType(Enum):
    QUERY = "query"
    MUTATION = "mutation"
