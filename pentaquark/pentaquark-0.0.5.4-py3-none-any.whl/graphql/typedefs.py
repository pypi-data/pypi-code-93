"""
Needed to build a graphql api:
- types
- input types
- queries
- mutations

Goal: make GraphQL customizable, while keeping the number of queries
as small as possible
"""
import enum

from ariadne import make_executable_schema, QueryType, MutationType

# from pentaquark.graphql.mixins import GraphQLTypeBuilder
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Union

ALL_FIELDS = "__all_fields__"
ALL_RELATIONSHIPS = "__all_relationships__"


class TypeDefsTypes(enum.Enum):
    TYPE = "type"
    INPUT = "input"
    QUERY = "query"
    MUTATION = "mutation"


def action(action_type=TypeDefsTypes.QUERY, input_type="", output_type="", name=""):
    def action_wrapper(func, **kwargs):
        return func(**kwargs)
    return action_wrapper


def query(**kwargs):
    return action(action_type=TypeDefsTypes.QUERY, **kwargs)


def mutation(**kwargs):
    return action(action_type=TypeDefsTypes.MUTATION, **kwargs)


def typedef(def_type=TypeDefsTypes.QUERY):
    def typedef_wrapper(func, **kwargs):
        return func(**kwargs)
    return typedef_wrapper


@dataclass
class GraphqlType:
    name: str

    def get_name(self):
        return self.name

    def get_properties(self):
        return {}


@dataclass
class GraphqlModelType(GraphqlType):
    model: Any
    include: Union[list, str] = None
    exclude: Union[list, str] = None

    def get_properties(self):
        if self.include == ALL_FIELDS:
            props = self.model._properties
        elif self.exclude is not None:
            props = [p for p in self.model._properties if p not in self.exclude]
        else:
            props = [p for p in self.model._properties if p not in self.include]
        return {
            p.name: p.graphql_type for p in props
        }


@dataclass
class Query:
    type: str
    name: str
    input_type_name: str
    output_type_name: str
    resolver: Callable

    def __post_init__(self):
        if self.type and self.type not in [TypeDefsTypes.QUERY, TypeDefsTypes.MUTATION]:
            raise ValueError(f"{self.type} is invalid")

    # default methods, that can be overridden on demand
    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_input_type_name(self):
        return self.input_type_name

    def get_output_type_name(self):
        return self.output_type_name

    def get_resolver(self):
        return self.resolver


class ModelGraphQL:
    model = None

    def _query(self, *args, **kwargs):
        pass

    def _mutate(self, *args, **kwargs):
        pass

    @typedef(def_type=TypeDefsTypes.INPUT)
    def input_type(self):
        pass

    @mutation()
    def create(self, **kwargs):  # resolver
        pass

    @mutation(input_type="", output_type="", name="")
    def update(self, **kwargs):  # resolver
        pass

    @mutation()
    def create_or_update(self, **kwargs):  # resolver
        pass

    def to_type_defs(self):
        pass


# import enum
#
#
# class ValidationError(Exception):
#     pass
#
#
# class TypeDefsTypes(enum.Enum):
#     TYPE = "type"
#     INPUT = "input"
#     QUERY = "query"
#     MUTATION = "mutation"
#
#
# class TypeDef:
#     def __init__(self, name, properties, args=None, typ=TypeDefsTypes.TYPE, resolver=None):
#         self.type = typ
#         self.name = name
#         self.properties = properties
#         self.args = args
#         self.resolver = None
#
#     def _to_prop_list(self):
#         return "\n".join(
#             f"{k}: {v}" for k, v in self.properties.items()
#         )
#
#     def _to_arg_list(self):
#         return ",".join(
#             f"{k}: {v}" for k, v in self.args.items()
#         )
#
#     def _to_prefix(self):
#         if self.args:
#             return f"{self.type.value} ({self._to_arg_list()})"
#         return self.type.value
#
#     def to_graphql(self):
#         return f"""{self._to_prefix()} {{
#             {self._to_prop_list()}
#         }}
#         """
#
#     def bin_resolver(self, func):
#         self.resolver = func
#
#

class SchemaBuilder:
    def __init__(self, defs, scalars):
        pass

    def _query_type(self):
        pass

    def _mutation_type(self):
        pass

    def _types(self):
        pass

    def type_defs(self):
        pass


def create_executable_schema(defs: list[TypeDefsTypes], scalars=None):
    """This is the main function, called

    :param defs: list of TypeDefsTypes that will be translated
        to a GraphQL schema
    """
    sb = SchemaBuilder(defs, scalars)
    type_defs = sb.type_defs()
    query_type = QueryType()
    mutation_type = MutationType()
    for d in defs:
        type_defs += d.to_type_defs()
        qts = d.query_types()
        for qt in qts:
            query_type.set_field(
                qt.name,
                qt.resolver
            )
        mts = d.mutation_types()
        for mt in mts:
            mutation_type.set_field(
                mt.name,
                mt.resolver
            )

    return make_executable_schema(
        type_defs, query_type, mutation_type, *(scalars or [])
    )
