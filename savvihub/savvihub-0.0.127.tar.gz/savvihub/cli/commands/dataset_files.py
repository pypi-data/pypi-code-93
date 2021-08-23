import typer

from savvihub.api.exceptions import NotFoundAPIException
from savvihub.cli.commands.volume import volume_file_list, volume_file_remove, volume_file_copy
from savvihub.cli.exceptions import ExitException
from savvihub.cli.inputs.dataset import dataset_full_name_callback, download_dest_path_callback
from savvihub.cli.inputs.organization import organization_name_option
from savvihub.cli.typer import Typer, Context
from savvihub.cli.utils import parse_dataset, inquire_text

dataset_files_app = Typer()


@dataset_files_app.callback()
def main():
    """
    Manage files in the dataset
    """
    return


@dataset_files_app.command(user_required=True)
def ls(
    ctx: Context,
    dataset_full_name: str = typer.Argument(None, metavar='[DATASET]',
                                            help='{organization}/{dataset} format where organization is optional.',
                                            callback=dataset_full_name_callback),
    path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Path', '/')),
    recursive: bool = typer.Option(False, '-r', '--recursive', help='recursive flag'),
    directory: bool = typer.Option(False, '-d', '--directory', help='list the directory itself, not its contents')
):
    """
    List files in the dataset with prefix
    """
    organization_name, dataset_name, dataset_version_name = parse_dataset(dataset_full_name)
    if organization_name is None:
        organization_name = ctx.organization.name

    dataset = ctx.authenticated_client.dataset_read(organization_name, dataset_name)
    volume_file_list(ctx, dataset.volume_id, path, recursive, directory)


@dataset_files_app.command(user_required=True)
def rm(
    ctx: Context,
    dataset_full_name: str = typer.Argument(None, metavar='[DATASET]',
                                            help='{organization}/{dataset} format where organization is optional.',
                                            callback=dataset_full_name_callback),
    path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Path to delete', '')),
    recursive: bool = typer.Option(False, '-r', '-R', '--recursive',
                                   help='Remove directories and their contents recursively'),
):
    """
    Remove files in a dataset (SavviHub dataset files only)
    """
    organization_name, dataset_name, _ = parse_dataset(dataset_full_name)
    if organization_name is None:
        organization_name = ctx.organization.name

    dataset = ctx.authenticated_client.dataset_read(organization_name, dataset_name)
    volume_file_remove(ctx, dataset.volume_id, path, recursive)


@dataset_files_app.command(user_required=True)
def upload(
    ctx: Context,
    dataset_full_name: str = typer.Argument(None, metavar='[DATASET]',
                                            help='{organization}/{dataset} format where organization is optional.',
                                            callback=dataset_full_name_callback),
    source_path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Source file or directory path', '')),
    dest_path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Dest path', '/')),
    recursive: bool = typer.Option(False, '-r', '--recursive'),
    watch: bool = typer.Option(False, '-w', '--watch'),
):
    """
    Upload files to a dataset (SavviHub dataset only)
    """
    organization_name, dataset_name, _ = parse_dataset(dataset_full_name)
    if organization_name is None:
        organization_name = ctx.organization.name

    dataset = ctx.authenticated_client.dataset_read(organization_name, dataset_name)
    volume_file_copy(
        ctx,
        source_volume_id=None,
        source_path=source_path,
        dest_volume_id=dataset.volume_id,
        dest_path=dest_path,
        recursive=recursive,
        watch=watch,
    )


@dataset_files_app.command(user_required=True)
def download(
    ctx: Context,
    dataset_full_name: str = typer.Argument(None, metavar='DATASET',
                                            help='{organization}/{dataset} format where organization is optional.',
                                            callback=dataset_full_name_callback),
    source_path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Source file or directory path', '/')),
    dest_path: str = typer.Argument(None, callback=download_dest_path_callback),
):
    """
    Download files from a dataset
    """
    organization_name, dataset_name, _ = parse_dataset(dataset_full_name)
    if organization_name is None:
        organization_name = ctx.organization.name

    dataset = ctx.authenticated_client.dataset_read(organization_name, dataset_name)
    volume_file_copy(
        ctx,
        source_volume_id=dataset.volume_id,
        source_path=source_path,
        dest_volume_id=None,
        dest_path=dest_path,
        recursive=True,
        watch=False,
    )


@dataset_files_app.command(user_required=True)
def cp(
    ctx: Context,
    dataset_full_name: str = typer.Argument(None, metavar='DATASET',
                                            help='{organization}/{dataset} format where organization is optional.',
                                            callback=dataset_full_name_callback),
    source_path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Source file or directory path', '')),
    dest_path: str = typer.Argument(None, callback=lambda path: path or inquire_text('Dest path', '')),
    organization_name: str = organization_name_option,
    recursive: bool = typer.Option(False, '-r', '--recursive'),
    watch: bool = typer.Option(False, '-w', '--watch'),
):
    """
    Copy files within a dataset (SavviHub dataset files only)
    """
    organization_name_override, dataset_name, src_dataset_version_name = parse_dataset(dataset_full_name)
    if organization_name_override:
        organization_name = organization_name_override

    dataset = ctx.authenticated_client.dataset_read(organization_name, dataset_name)
    if src_dataset_version_name != 'latest':
        try:
            ctx.authenticated_client.dataset_version_read(dataset.volume_id, src_dataset_version_name)
        except NotFoundAPIException:
            raise ExitException(f'Invalid dataset dataset_version: {dataset_full_name}\n'
                                f'Please check your dataset and dataset_version exist in organization `{organization_name}`.')
    volume_file_copy(
        ctx,
        source_volume_id=dataset.volume_id,
        source_path=source_path,
        dest_volume_id=dataset.volume_id,
        dest_path=dest_path,
        recursive=recursive,
        watch=watch,
    )
