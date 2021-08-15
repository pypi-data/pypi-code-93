from abc import ABC, ABCMeta, abstractmethod
from typing import Any, ClassVar, Dict, Iterator, List, Optional, Type, Union, overload

from .build_state import GraphQLBuildState
from .enums import GraphQLOperationType
from .fields import GraphQLField, GraphQLFieldBase, GraphQLNestableField
from .template import GraphQLChainMap, GraphQLTemplate
from .typings import FieldBuilderT, NestableFieldBuilderT
from .utils import minify_graphql_call

__all__ = (
    "GraphQLFieldBuilder",
    "GraphQLNestableFieldBuilder",
    "GraphQLOperationBuilder",
)


class _GraphQLFieldBuilderBase(ABC):
    TEMPLATE: ClassVar[str]
    _TEMPLATE_OBJ: ClassVar[GraphQLTemplate]
    COST: ClassVar[int] = 1

    def __init__(self) -> None:
        if not hasattr(self.__class__, "TEMPLATE"):
            raise RuntimeError("The class does not have an TEMPLATE attribute set.")

    def __init_subclass__(cls) -> None:
        if hasattr(cls, "TEMPLATE"):
            cls.TEMPLATE = minify_graphql_call(cls.TEMPLATE)
            template_obj = GraphQLTemplate(cls.TEMPLATE)
            template_obj.check_string_placeholders()
            cls._TEMPLATE_OBJ = template_obj

    @abstractmethod
    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        ...


class _GraphQLNestableBuilder:
    def __init__(self) -> None:
        super().__init__()
        self._fields: Dict[str, GraphQLFieldBase[Any]] = {}


class _GraphQLNestableFieldBuilderMeta(ABCMeta):
    @overload
    def __get__(
        self: Type[NestableFieldBuilderT], instance: None, owner: Any
    ) -> Type[NestableFieldBuilderT]:
        ...

    @overload
    def __get__(
        self: Type[NestableFieldBuilderT],
        instance: _GraphQLNestableBuilder,
        owner: Any,
    ) -> GraphQLNestableField[NestableFieldBuilderT]:
        ...

    def __get__(
        self: Type[NestableFieldBuilderT],
        instance: Optional[_GraphQLNestableBuilder],
        owner: Any,
    ) -> Union[
        GraphQLNestableField[NestableFieldBuilderT], Type[NestableFieldBuilderT]
    ]:
        if instance is None:
            return self
        builder_name = self.__name__
        builder: Optional[GraphQLNestableField[NestableFieldBuilderT]]
        builder = instance._fields.get(builder_name)  # type: ignore[assignment]
        if builder is None:
            builder = instance._fields[builder_name] = GraphQLNestableField(self)
        return builder


class _GraphQLFieldBuilderMeta(ABCMeta):
    @overload
    def __get__(
        self: Type[FieldBuilderT], instance: None, owner: Any
    ) -> Type[FieldBuilderT]:
        ...

    @overload
    def __get__(
        self: Type[FieldBuilderT], instance: _GraphQLNestableBuilder, owner: Any
    ) -> GraphQLField[FieldBuilderT]:
        ...

    def __get__(
        self: Type[FieldBuilderT],
        instance: Optional[_GraphQLNestableBuilder],
        owner: Any,
    ) -> Union[GraphQLField[FieldBuilderT], Type[FieldBuilderT]]:
        if instance is None:
            return self
        builder_name = self.__name__
        builder: Optional[GraphQLField[FieldBuilderT]]
        builder = instance._fields.get(builder_name)  # type: ignore[assignment]
        if builder is None:
            builder = instance._fields[builder_name] = GraphQLField(self)
        return builder


class GraphQLOperationBuilder(_GraphQLNestableBuilder):
    OPERATION_TYPE: ClassVar[GraphQLOperationType]
    MAX_COST: ClassVar[Optional[int]]

    def __init__(self) -> None:
        if not hasattr(self.__class__, "OPERATION_TYPE"):
            raise RuntimeError(
                "The class does not have an OPERATION_TYPE attribute set."
            )
        if not hasattr(self.__class__, "MAX_COST"):
            raise RuntimeError("The class does not have an MAX_COST attribute set.")
        super().__init__()

    def _get_call_from_parts(self, parts: List[str]) -> str:
        joined_parts = "\n".join(parts)
        parts.clear()
        return f"{self.OPERATION_TYPE.value} {{\n{joined_parts}\n}}"

    def iter_calls(self) -> Iterator[str]:
        build_state = GraphQLBuildState(self)
        substitutions = GraphQLChainMap()
        substitutions.maps = []
        parts = []

        for field in self._fields.values():
            for call in field.iter_calls(build_state, substitutions):
                if call is not None:
                    parts.append(call)
                    continue

                if not parts:
                    raise ValueError(
                        "The cost of a single partial call in"
                        f" {field.__class__.__name__} exceeds max cost set for"
                        f" {self.__class__.__name__}."
                    )

                yield self._get_call_from_parts(parts)

        if parts:
            yield self._get_call_from_parts(parts)


class GraphQLNestableFieldBuilder(
    _GraphQLNestableBuilder,
    _GraphQLFieldBuilderBase,
    metaclass=_GraphQLNestableFieldBuilderMeta,
):
    def __init__(self, substitutions: Dict[str, Any]) -> None:
        super().__init__()
        self.substitutions = substitutions

    def _get_call_from_parts(
        self, parts: List[str], template_substitutions: GraphQLChainMap
    ) -> str:
        template_substitutions["nested_call"] = "\n".join(parts)
        parts.clear()
        return self._TEMPLATE_OBJ.substitute(template_substitutions)

    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        substitutions = parent_substitutions.new_child(self.substitutions)
        template_substitutions = substitutions.new_child()
        parts: List[str] = []
        is_first_yield = True
        if build_state.should_end_call(self.COST):
            is_first_yield = False
            yield None

        for field in self._fields.values():
            for call in field.iter_calls(build_state, substitutions):
                if call is not None:
                    parts.append(call)
                    continue

                if not parts:
                    if not is_first_yield:
                        raise ValueError(
                            "The cost of a single partial call in"
                            f" {field.__class__.__name__} exceeds max cost set for"
                            f" {build_state.operation_builder.__class__.__name__}."
                        )
                    continue

                is_first_yield = False
                yield self._get_call_from_parts(parts, template_substitutions)
                yield None
                if build_state.should_end_call(self.COST):
                    raise ValueError(
                        "The cost of a single partial call in"
                        f" {field.__class__.__name__} exceeds max cost set for"
                        f" {build_state.operation_builder.__class__.__name__}."
                    )

        if parts:
            yield self._get_call_from_parts(parts, template_substitutions)
        else:
            build_state.current_cost -= self.COST


class GraphQLFieldBuilder(_GraphQLFieldBuilderBase, metaclass=_GraphQLFieldBuilderMeta):
    def __init__(self) -> None:
        super().__init__()
        self.field_substitutions: List[Dict[str, Any]] = []

    def _append(self, substitutions: Dict[str, Any]) -> None:
        self.field_substitutions.append(substitutions)

    def iter_calls(
        self, build_state: GraphQLBuildState, parent_substitutions: GraphQLChainMap
    ) -> Iterator[Optional[str]]:
        substitutions = parent_substitutions.new_child()
        for substitutions.maps[0] in self.field_substitutions:
            if build_state.should_end_call(self.COST):
                yield None
            yield self._TEMPLATE_OBJ.substitute(substitutions)
