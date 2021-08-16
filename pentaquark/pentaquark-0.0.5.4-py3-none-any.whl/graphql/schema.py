# import enum
import re
import logging
from ariadne import QueryType, MutationType, make_executable_schema, gql

from pentaquark.constants import SEPARATOR, START_NODE_ALIAS, MANAGER_ATTRIBUTE_NAME
from pentaquark.graphql.mixins import GraphQLTypeBuilder
from pentaquark.registry import node_registry
from .scalars import uuid_scalar

logger = logging.getLogger(__name__)


def create_type_defs(type_defs="", qs="", ms="") -> str:
    """
    Loop over registered models and generate types
    :return: a gql schema (str)
    """
    types = type_defs + "type SuccessOutput {success: Boolean } "
    types += "scalar UUID "
    input_types = ""
    queries = qs
    mutations = ms
    connection_mutations = {}
    for name, node_cls in node_registry.items():
        if not node_cls.is_bound():
            continue
        if name == "Node":
            continue
        graphql_builder = GraphQLTypeBuilder(node_cls)
        types += graphql_builder.to_graphql_type()
        i = graphql_builder.to_graphql_input_type()
        if i:
            input_types += i
        id_i = graphql_builder.to_graphql_id_input_type()
        if id_i:
            input_types += id_i
        id_f = graphql_builder.to_graphql_filter_input_type()
        if id_f:
            input_types += id_f
        q = graphql_builder.to_graphql_queries()
        if q:
            queries += q
        m = graphql_builder.to_graphql_mutations()
        if m:
            mutations += m
        c = graphql_builder.to_graphql_connection_mutations()
        if c:
            connection_mutations.update(c)
    result = f"{types}\n"
    if input_types:
        result += f"{input_types}\n"
    if queries:
        result += f"type Query{{ {queries} }}\n"
    if mutations or connection_mutations:
        if connection_mutations:
            for c in connection_mutations.values():
                mutations += c
        result += f"type Mutation {{ {mutations} }}\n"
    return gql(result)


def inner_type(field_type):
    try:
        return inner_type(field_type.of_type)
    except AttributeError:
        return str(field_type)


def create_query_type():
    query = QueryType()
    for name, node_cls in node_registry.items():
        if not node_cls.is_bound():
            continue
        type_name = name.lower()
        query.set_field(
            type_name, query_resolver
        )
        query.set_field(
            f"{type_name}s", query_resolver
        )
    return query


def create_mutation_type():
    mutation = MutationType()
    for name, node_cls in node_registry.items():
        if not node_cls.is_bound():
            continue
        type_name = node_cls.get_label()
        mutation.set_field(
            f"create{type_name}", mutation_resolver,
        )
        mutation.set_field(
            f"update{type_name}", mutation_resolver,
        )
        mutation.set_field(
            f"createOrUpdate{type_name}", mutation_resolver,
        )
        mutation.set_field(
            f"delete{type_name}", mutation_resolver,
        )
        for rn in node_cls._relationships:
            mutation.set_field(
                f"connect{node_cls.get_label()}To{rn.title()}", mutation_resolver
            )
    return mutation


def flatten_field_nodes(field_nodes, start="", field_name=""):
    res = []
    for field in field_nodes:
        try:
            selection = field.selection_set.selections
            if field.name.value == field_name:
                new_start = ""
            elif start == "":
                new_start = field.name.value
            else:
                new_start = start + SEPARATOR + field.name.value
            res.extend(flatten_field_nodes(selection, start=new_start))
        except AttributeError:
            if start == "":
                res.append(field.name.value)
            else:
                res.append(start + SEPARATOR + field.name.value)
    return res


def _return_list(type_name, return_type):
    return type_name != str(return_type)


def query_resolver(obj, info, **kwargs):
    """

    :param obj:
    :param info:
    :param kwargs: parameters inside ex: movie(title: "X") => kwargs = {"title": "X"}
    :return:
    """
    type_name = inner_type(info.return_type)
    node_class = node_registry[type_name]
    # pagination
    order_by = kwargs.pop("orderBy", None)
    limit = kwargs.pop("limit", None)
    skip = kwargs.pop("skip", None)

    if "filters" in kwargs:
        res = node_class.q.match(**kwargs["filters"])
    else:
        res = node_class.q.match(**kwargs)

    if order_by:
        res = res.order_by(order_by)
    if limit:
        res = res.limit(limit)
    if skip:
        res = res.skip(skip)

    # format return values by parsing graphQL query string
    ret_values = flatten_field_nodes(info.field_nodes, start=START_NODE_ALIAS, field_name=info.field_name)
    # TODO: add graphql_properties requirements here
    # perform db query
    for r in ret_values:
        res = res.returns(r)
    objects = res.returns(*ret_values).all()
    # format result, include graphql_properties if any
    final_result = []
    for o in objects:
        final_result.append(o.to_graphql_return(ret_values, context={}))
    if _return_list(type_name, info.return_type):
        return final_result
    if len(final_result) > 1:
        raise ValueError("More than one value")
    try:
        final_result = final_result[0]
    except IndexError:
        final_result = None
    return final_result


def _connect_mutation_resolver(obj, info, **kwargs):
    mutation_name = info.field_name
    match = re.match(r"connect(?P<source>[a-zA-Z_]+)To(?P<rel>[a-zA-Z_]+)", mutation_name)
    if not match:
        raise Exception(f"Unknown operation {mutation_name}")
    groups = match.groupdict()
    node_class = node_registry[groups["source"]]
    source = getattr(node_class, MANAGER_ATTRIBUTE_NAME).match(**kwargs["start"]).one()
    rn = groups["rel"].lower()
    rel = getattr(source, rn)
    target = getattr(rel.rel_property.get_target_node_class(), MANAGER_ATTRIBUTE_NAME).match(**kwargs["end"]).one()
    rel.connect(target)
    res = {
       "success": True,
    }
    print(res)
    return res


def _create_mutation_resolver(node_class, input_data):
    logger.debug("MUTATION RESOLVER CREATE %s, data=%s", node_class, input_data)
    return node_class.q.create(**input_data)


def _update_mutation_resolver(node_class, pk, input_data):
    logger.debug("MUTATION RESOLVER UPDATE %s, id=%s, data=%s", node_class, pk, input_data)
    instance = node_class.q.match(
        **{
            node_class.get_id_property_name(): pk
        }
    ).one()
    for k, v in input_data.items():
        setattr(instance, k, v)
    instance.save()
    return instance


def _delete_mutation_resolver(field_name, pk):
    type_name = field_name.removeprefix("delete")
    node_class = node_registry[type_name]
    logger.debug("try deleting %s, %s", node_class, pk)
    instance = node_class.q.match(
        **{
            node_class.get_id_property_name(): pk
        }
    ).one()
    logger.info(f"DELETING {instance}")
    return instance.detach_delete()


def mutation_resolver(obj, info, **kwargs):
    logger.debug("MUTATION RESOLVER %s, %s", info, kwargs)
    if "connect" in info.field_name:
        return _connect_mutation_resolver(obj, info, **kwargs)
    if "delete" in info.field_name:
        try:
            _delete_mutation_resolver(info.field_name, kwargs["id"])
            return {"success": True}
        except Exception as e:
            logger.error(f"GRAPHQL: deleting node {info.field_name} with id {kwargs['id']} failed with error {e}")
            return {"success": False}
    type_name = inner_type(info.return_type)
    node_class = node_registry[type_name]
    if "createOrUpdate" in info.field_name:
        if pk := kwargs.get("id"):
            instance = _update_mutation_resolver(node_class, pk, kwargs["input"])
        else:
            instance = _create_mutation_resolver(node_class, kwargs["input"])
    elif "create" in info.field_name:
        instance = _create_mutation_resolver(node_class, kwargs.get("input", {}))
    elif "update" in info.field_name:
        instance = _update_mutation_resolver(node_class, kwargs["id"], kwargs["input"])
    else:
        instance = None
    return query_resolver(obj, info, **instance.get_id_dict())


def create_executable_schema(type_defs="", queries="", mutations="", ext_qt=None, ext_mt=None):
    type_defs = create_type_defs(type_defs, queries, mutations)
    qt = create_query_type()
    mt = create_mutation_type()
    if ext_qt:
        qt = [qt, ext_qt]
    if ext_mt:
        mt = [mt, ext_mt]
    return make_executable_schema(type_defs, qt, mt, uuid_scalar)

#
# class GraphQLProperty:
#     def __init__(self, is_required=False):
#         pass
#
#     def to_graphql(self, value):
#         pass
#
#     def from_graphql(self, value):
#         pass
#
#
# class GraphQLMethodProperty(GraphQLProperty):
#     def __init__(self, is_required=False, graphql_type="String", requires=None):
#         super().__init__(is_required=is_required)
#
#
# class GraphQLType:
#     def schema(self):
#         pass
#
#
# class GraphQlTypeType(enum.Enum):
#     DEFAULT = "default"
#     INPUT = "input"
#
#
# graphql_type_registry = []
#
#
# class GraphQLModelType:
#     class Meta:
#         type = GraphQlTypeType.DEFAULT
#         model = None
#         include_fields = '__all__'
#         exclude_fields = []
#
#
# class Movie:
#     pass
#
# #
# # class MovieType(GraphQlType):
# #     nb_actors = GraphQLMethodProperty(requires=["actors"], graphql_type="Int", is_required=False)
# #
# #     class Meta:
# #         model = Movie
# #         include_fields = "__all__"
# #
# #     def get_nb_actors(self):
# #         return len(self.object.actors.all())
#
#
# """
# props = included_props
#
# .returns(
#     *[p.name for p in props],
#     *[*p.requires for p in props]
# )
# """
