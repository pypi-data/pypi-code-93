from abc import ABC, abstractmethod
from typing import Any, Generic, Iterator, List, Optional, Type, TypeVar

from .build_state import GraphQLBuildState
from .template import GraphQLChainMap
from .typings import FieldBuilderT, NestableFieldBuilderT

__all__ = ("GraphQLField", "GraphQLFieldBase", "GraphQLNestableField")

_T = TypeVar("_T")


class GraphQLFieldBase(Generic[_T], ABC):
    def __init__(self, builder_cls: Type[_T]) -> None:
        self.builder_cls = builder_cls

    @abstractmethod
    def __call__(self, **kwargs: Any) -> Optional[_T]:
        ...

    @abstractmethod
    def append(self, **kwargs: Any) -> Optional[_T]:
        ...

    @abstractmethod
    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        ...


class GraphQLNestableField(GraphQLFieldBase[NestableFieldBuilderT]):
    def __init__(self, builder_cls: Type[NestableFieldBuilderT]) -> None:
        super().__init__(builder_cls)
        self.builders: List[NestableFieldBuilderT] = []

    def __call__(self, **kwargs: Any) -> NestableFieldBuilderT:
        return self.append(**kwargs)

    def append(self, **kwargs: Any) -> NestableFieldBuilderT:
        builder = self.builder_cls(kwargs)
        self.builders.append(builder)
        return builder

    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        for builder in self.builders:
            yield from builder.iter_calls(build_state, parent_substitutions)


class GraphQLField(GraphQLFieldBase[FieldBuilderT]):
    def __init__(self, builder_cls: Type[FieldBuilderT]) -> None:
        super().__init__(builder_cls)
        self.builder = self.builder_cls()

    def __call__(self, **kwargs: Any) -> None:
        self.builder._append(kwargs)

    def append(self, **kwargs: Any) -> None:
        self.builder._append(kwargs)

    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        yield from self.builder.iter_calls(build_state, parent_substitutions)
