from datetime import date
from graphql.type.definition import GraphQLObjectType
from ariadne.types import GraphQLResolveInfo
from sqlalchemy.orm import Session


nulldate = date(1753, 1, 1)


def get_dbsession(info) -> Session:
    return info.context['request'].state.dbsession


def get_all_records(info, q):
    return get_dbsession(info).execute(q).scalars().unique().all()  # Todo: Watch out for that .unique()


def get_one_record(info, q):
    return get_dbsession(info).execute(q).scalars().first()


def get_one_field(info, q):
    return get_dbsession(info).execute(q).scalar()


def resolve_type_inspector(_, info: GraphQLResolveInfo, type_name):
    gqltype = info.schema.get_type(type_name)
    if gqltype is None or not isinstance(gqltype, GraphQLObjectType):
        return None

    result = {
        'filter_fields': [],
        'edit_fields': []
    }

    if hasattr(gqltype, '__all_filter__'):
        for field_name, field in gqltype.fields.items():
            if not hasattr(field, '__no_filter__'):
                result['filter_fields'].append(field_name)

    return result
