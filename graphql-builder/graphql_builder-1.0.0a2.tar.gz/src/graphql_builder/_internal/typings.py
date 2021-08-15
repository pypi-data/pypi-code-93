from typing import Any, Dict, Iterator, Optional, Protocol, TypeVar

from .build_state import GraphQLBuildState
from .template import GraphQLChainMap

__all__ = ("FieldBuilderT", "NestableFieldBuilderT")


class GraphQLFieldBuilderProtocol(Protocol):
    def __init__(self) -> None:
        ...

    def _append(self, substitutions: Dict[str, Any]) -> None:
        ...

    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        ...


class GraphQLNestableFieldBuilderProtocol(Protocol):
    def __init__(self, substitutions: Dict[str, Any]) -> None:
        ...

    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        ...


FieldBuilderT = TypeVar("FieldBuilderT", bound=GraphQLFieldBuilderProtocol)
NestableFieldBuilderT = TypeVar(
    "NestableFieldBuilderT", bound=GraphQLNestableFieldBuilderProtocol
)
