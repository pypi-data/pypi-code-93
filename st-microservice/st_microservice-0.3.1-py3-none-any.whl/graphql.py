from typing import Union, List
import asyncio
from graphql import GraphQLField, GraphQLObjectType, GraphQLInterfaceType, GraphQLResolveInfo
from ariadne import load_schema_from_path, make_executable_schema, SchemaDirectiveVisitor
from ariadne.graphql import GraphQLError
from ariadne.asgi import GraphQL
from ariadne.types import Extension, SchemaBindable


class NoAuthenticationDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
            self,
            field: GraphQLField,
            object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        if field.resolve is None:
            raise Exception(f'Could not add directive to {object_type}\'s {field.ast_node.name.value} because it does not have a resolver')
        field.resolve.__require_authentication__ = False
        return field

    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__require_authentication__ = False
        return object_


class NeedPermissionDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        if field.resolve is None:
            raise Exception(f'Could not add directive to {object_type}\'s {field.ast_node.name.value} because it does not have a resolver')
        if self.args['strict']:
            field.resolve.__require_scope__ = self.args['scope']
        else:
            field.resolve.__hide_noscope__ = self.args['scope']
        return field

    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        if self.args['strict']:
            object_.__require_scope__ = self.args['scope']
        else:
            object_.__hide_noscope__ = self.args['scope']
        return object_


class AllFilterDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__all_filter__ = True
        return object_


class NoFilterDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        field.__no_filter__ = True
        return field


async def check_permission_middleware(resolver, obj, info: GraphQLResolveInfo, **args):
    """ GraphQL middleware that requires authentication by default """
    request = info.context['request']

    # Check for Authentication
    if hasattr(resolver, '__require_authentication__'):
        needs_auth = resolver.__require_authentication__
    elif hasattr(info.parent_type, '__require_authentication__'):
        needs_auth = info.parent_type.__require_authentication__
    else:
        needs_auth = True

    if needs_auth and not request.user.is_authenticated:
        raise GraphQLError(message='Requires Authentication')

    # check for Strict Permission
    if hasattr(resolver, '__require_scope__'):
        needs_scope = resolver.__require_scope__
    elif hasattr(info.parent_type, '__require_scope__'):
        needs_scope = info.parent_type.__require_scope__
    else:
        needs_scope = None

    if needs_scope is not None and needs_scope not in request.auth.scopes:
        raise GraphQLError(message=f'Requires Scope: {needs_scope}')

    # check for Loose Permission
    if hasattr(resolver, '__hide_noscope__'):
        hide_noscope = resolver.__hide_noscope__
    elif hasattr(info.parent_type, '__hide_noscope__'):
        hide_noscope = info.parent_type.__hide_noscope__
    else:
        hide_noscope = None

    if hide_noscope is not None and hide_noscope not in request.auth.scopes:
        return None

    # Return resolver
    if asyncio.iscoroutinefunction(resolver):
        return await resolver(obj, info, **args)
    else:
        return resolver(obj, info, **args)


class DBRollbackExtension(Extension):
    @staticmethod
    def has_errors(errors, context) -> None:
        context['request'].state.dbsession.rollback()


# Exported

def mount_graphql(app, schema_path, bindables: List[SchemaBindable], debug: bool):
    type_defs = load_schema_from_path(schema_path)

    schema = make_executable_schema(type_defs, bindables, directives={
        'no_authentication': NoAuthenticationDirective,
        'need_permission': NeedPermissionDirective,
        'all_filter': AllFilterDirective,
        'no_filter': NoFilterDirective
    })

    app.mount('/graphql', GraphQL(schema,
                                  debug=debug,
                                  middleware=[check_permission_middleware],
                                  extensions=[DBRollbackExtension]
                                  ))
    return app
