from . import context
from agilicus.agilicus_api import (
    FileShareService,
    FileShareServiceSpec,
)

from .input_helpers import build_updated_model
from .input_helpers import update_org_from_input_or_ctx
from .output.table import (
    spec_column,
    status_column,
    format_table,
    metadata_column,
)


def list_file_share_services(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    query_results = apiclient.app_services_api.list_file_share_services(**kwargs)
    return query_results.file_share_services


def add_file_share_service(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    spec = FileShareServiceSpec(**kwargs)
    model = FileShareService(spec=spec)
    return apiclient.app_services_api.create_file_share_service(model).to_dict()


def _get_file_share_service(ctx, apiclient, file_share_service_id, **kwargs):
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.app_services_api.get_file_share_service(
        file_share_service_id, **kwargs
    )


def show_file_share_service(ctx, file_share_service_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return _get_file_share_service(
        ctx, apiclient, file_share_service_id, **kwargs
    ).to_dict()


def delete_file_share_service(ctx, file_share_service_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.app_services_api.delete_file_share_service(
        file_share_service_id, **kwargs
    )


def update_file_share_service(ctx, file_share_service_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    get_args = {}
    update_org_from_input_or_ctx(get_args, ctx, **kwargs)
    mapping = _get_file_share_service(ctx, apiclient, file_share_service_id, **get_args)

    mapping.spec = build_updated_model(FileShareServiceSpec, mapping.spec, kwargs)
    return apiclient.app_services_api.replace_file_share_service(
        file_share_service_id, file_share_service=mapping
    ).to_dict()


def format_file_share_services_as_text(ctx, shares):
    columns = [
        metadata_column("id"),
        spec_column("org_id"),
        spec_column("name"),
        spec_column("share_name"),
        spec_column("local_path"),
        spec_column("connector_id"),
        status_column("share_uri"),
    ]

    return format_table(ctx, shares, columns)
