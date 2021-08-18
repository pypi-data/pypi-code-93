from urllib.parse import urlparse

import typer
from terminaltables import AsciiTable

from savvihub.cli.commands.dataset_files import dataset_files_app
from savvihub.cli.constants import (
    DATASET_PATH_PARSE_SCHEME_S3_WITH_SEPERATOR,
    DATASET_PATH_PARSE_SCHEME_GS_WITH_SEPERATOR,
    DATASET_PATH_PARSE_SCHEME_S3,
    DATASET_PATH_PARSE_SCHEME_GS,
    DATASET_SOURCE_TYPE_AWS_S3,
    DATASET_SOURCE_TYPE_GCP_GS,
    WEB_HOST,
)
from savvihub.cli.exceptions import ExitException
from savvihub.cli.inputs.dataset import dataset_full_name_callback
from savvihub.cli.inputs.organization import organization_name_option
from savvihub.cli.typer import Typer, Context
from savvihub.cli.utils import parse_dataset

dataset_app = Typer()
dataset_app.add_typer(dataset_files_app, name='files')


@dataset_app.callback()
def main():
    """
    Manage the collection of data
    """
    return


@dataset_app.command(user_required=True)
def list(
    ctx: Context,
    organization_name: str = organization_name_option,
):
    """
    Show datasets
    """
    client = ctx.authenticated_client
    dataset_list = client.dataset_list(organization_name).results
    if len(dataset_list) == 0:
        typer.echo(f'No datasets found in `{organization_name}` organization.')
    else:
        table = AsciiTable([
            ['ORGANIZATION/NAME', 'SOURCE TYPE'],
            *[[f'{d.organization.name}/{d.name}', d.source.type] for d in dataset_list],
        ])
        table.inner_column_border = False
        table.inner_heading_row_border = False
        table.inner_footing_row_border = False
        table.outer_border = False

        typer.echo(table.table)


@dataset_app.command(user_required=True)
def create(
    ctx: Context,
    dataset_full_name: str = typer.Argument(..., metavar='DATASET',
                                            help='{organization}/{dataset} format where organization is optional.'),
    is_version_enabled: bool = typer.Option(False, "-v", "--versioning", help="Enable or disable versioning."),
    path_arg: str = typer.Option(None, "-u", "--url", help="S3 or GoogleStorage url starting with s3:// or gs://."),
    aws_role_arn: str = typer.Option(None, "--aws-role-arn", help="Required to create S3 dataset."),
    version_path_arg: str = typer.Option(None, "-vu", "--version-url", help="Required to version S3 or GoogleStorage dataset."),
    description: str = typer.Option(None, "-m", help="Dataset description."),
):
    """
    Create a dataset
    """
    client = ctx.authenticated_client
    organization_name, dataset_name, _ = parse_dataset(dataset_full_name)
    if organization_name is None:
        organization_name = ctx.organization.name

    if path_arg:
        if not (path_arg.startswith(DATASET_PATH_PARSE_SCHEME_S3_WITH_SEPERATOR)
                or path_arg.startswith(DATASET_PATH_PARSE_SCHEME_GS_WITH_SEPERATOR)):
            raise ExitException(f"path should start with \"s3://\" or \"gs://\"")

        r = urlparse(path_arg)
        if is_version_enabled:
            if not version_path_arg:
                raise ExitException("Versioning bucket path is required to version S3 or GoogleStorage.")
            if r.scheme == DATASET_PATH_PARSE_SCHEME_S3:
                if not version_path_arg.startswith(DATASET_PATH_PARSE_SCHEME_S3_WITH_SEPERATOR):
                    raise ExitException(f"path should start with \"s3://\"")
                if path_arg.startswith(version_path_arg):
                    raise ExitException("data bucket path shouldn't be a child directory of version bucket path")
                if version_path_arg.startswith(path_arg):
                    raise ExitException("version bucket path shouldn't be a child directory of data bucket path")
            if r.scheme == DATASET_PATH_PARSE_SCHEME_GS:
                raise ExitException("Currently versioning is not allowed for GoogleStorage.")
            # if not version_path_arg.startswith(DATASET_PATH_PARSE_SCHEME_GS_WITH_SEPERATOR):
            #     raise ExitException(f"path should start with \"gs://\"")

        if r.scheme == DATASET_PATH_PARSE_SCHEME_GS:
            dataset = client.dataset_gs_create(organization_name, dataset_name, False, description, path_arg)
        elif r.scheme == DATASET_PATH_PARSE_SCHEME_S3:
            if not aws_role_arn:
                raise ExitException("AWS Role ARN is required for S3 users")
            dataset = client.dataset_s3_create(
                organization_name,
                dataset_name,
                False,
                description,
                path_arg,
                aws_role_arn,
                is_version_enabled,
                version_path_arg,
            )
        else:
            raise ExitException("Only Google Cloud Storage and Amazon S3 are supported at the moment.")
    else:
        dataset = client.dataset_create(organization_name, dataset_name, is_version_enabled, description)

    if not dataset:
        return

    if dataset_name != dataset.name:
        typer.echo(f'Duplicate dataset name: {dataset_name}')

    typer.echo(
        f'Dataset {dataset.name} is created.\n'
        f'Full dataset info at:\n'
        f'    {WEB_HOST}/{dataset.organization.name}/datasets/{dataset.name}\n'
    )


@dataset_app.command(user_required=True)
def describe(
    ctx: Context,
    dataset_full_name: str = typer.Argument(None, metavar='[DATASET]',
                                            help='{organization}/{dataset} format where organization is optional.',
                                            callback=dataset_full_name_callback),
):
    """
    Describe the dataset information in detail
    """
    organization_name, dataset_name, _ = parse_dataset(dataset_full_name)
    if organization_name is None:
        organization_name = ctx.organization.name

    dataset = ctx.authenticated_client.dataset_read(organization_name, dataset_name)
    typer.echo(
        f'Name: {dataset.name}\n'
        f'Versioning: {dataset.is_version_enabled}\n'
        f'Volume ID: {dataset.volume_id}\n'
        f'Organization: {dataset.organization.name}'
    )

    source = dataset.source
    if source.type == DATASET_SOURCE_TYPE_AWS_S3:
        typer.echo(f'Source: s3://{source.bucket_name}/{source.path}')
    elif source.type == DATASET_SOURCE_TYPE_GCP_GS:
        typer.echo(f'Source: gs://{source.bucket_name}/{source.path}')

    typer.echo(
        '\n'
        f'Full dataset info at:\n'
        f'    {WEB_HOST}/{dataset.organization.name}/datasets/{dataset.name}\n'
    )
