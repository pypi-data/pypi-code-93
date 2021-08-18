import os
import time
from collections import defaultdict
from urllib.parse import urlparse

import typer
from terminaltables import AsciiTable

from openapi_client import ResponseVolume
from savvihub.api.exceptions import NoSuchFileOrDirectoryAPIException
from savvihub.api.downloader import Downloader
from savvihub.api.uploader import Uploader
from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Typer, Context
from savvihub.common.utils import sizeof_fmt, remove_suffix

volume_app = Typer()


def refine_volume_path(
    path_arg,
    raise_if_not_empty=False,
    raise_if_not_dir=False,
    raise_if_not_exist=False,
    remote_only=False,
):
    if path_arg.startswith('svds://'):
        raise ExitException('[Error] Use \'sv://\' for volumes.')

    if path_arg.startswith('sv://'):
        return path_arg, True
    elif remote_only:
        return 'sv://' + path_arg, True

    path = os.path.abspath(path_arg)
    if os.path.exists(path):
        if not os.path.isdir(path) and raise_if_not_dir:
            raise ExitException(f'Must specify directory: {path_arg}')
        if raise_if_not_empty and len(os.listdir(path)) > 0:
            raise ExitException(f'Must specify empty directory: {path_arg}')
    else:
        if raise_if_not_exist:
            raise ExitException(f'Must specify directory: {path_arg}')

    return path, False


def parse_remote_volume_path(remote_path: str) -> (ResponseVolume, str, str):
    # sv://1:dataset_version/path/to/files
    u = urlparse(remote_path)
    volume_dataset_version = u.netloc
    split_dataset_version = volume_dataset_version.split(':', 1)
    volume_id = int(split_dataset_version[0])
    file_path = u.path.lstrip('/')

    dataset_version = split_dataset_version[1] if len(split_dataset_version) == 2 else 'latest'

    return volume_id, dataset_version, file_path


@volume_app.callback()
def main():
    """
    Manage files in the volume
    """


@volume_app.command(auth_required=True)
def ls(
    ctx: Context,
    source_path_arg: str = typer.Argument(...),
    recursive: bool = typer.Option(False, '-r', '--recursive', help='recursive flag'),
    directory: bool = typer.Option(False, '-d', '--directory', help='list the directory itself, not its contents')
):
    """
    List files in the dataset with prefix
    """
    source_path, is_source_remote = refine_volume_path(source_path_arg, raise_if_not_exist=True, remote_only=True)

    volume_id, dataset_version, path = parse_remote_volume_path(source_path)
    volume_file_list(ctx, volume_id, path, recursive, directory)


@volume_app.command(auth_required=True)
def rm(
    ctx: Context,
    source_path_arg: str = typer.Argument(...),
    recursive: bool = typer.Option(False, '-r', '-R', '--recursive',
                                   help='Remove directories and their contents recursively'),
):
    """
    Remove files in the volume with path
    """
    source_path, is_source_remote = refine_volume_path(source_path_arg, raise_if_not_exist=True, remote_only=True)

    volume_id, dataset_version, path = parse_remote_volume_path(source_path)
    volume_file_remove(ctx, volume_id, path, recursive)


@volume_app.command(auth_required=True)
def cp(
    ctx: Context,
    source_path_arg: str = typer.Argument(...),
    dest_path_arg: str = typer.Argument(...),
    recursive: bool = typer.Option(False, '-r', '--recursive'),
    watch: bool = typer.Option(False, '-w', '--watch'),
):
    source_path, is_source_remote = refine_volume_path(source_path_arg, raise_if_not_exist=True)
    dest_path, is_dest_remote = refine_volume_path(dest_path_arg)

    source_volume_id = dest_volume_id = None
    if is_source_remote:
        source_volume_id, _, source_path = parse_remote_volume_path(source_path)
    if is_dest_remote:
        dest_volume_id, _, dest_path = parse_remote_volume_path(dest_path)

    volume_file_copy(ctx, source_volume_id, source_path,
                     dest_volume_id, dest_path,
                     recursive, watch)


def volume_file_list(ctx: Context, volume_id: int, path: str, recursive: bool, directory: bool):
    client = ctx.authenticated_client

    if recursive and directory:
        raise ExitException('[Error] -r and -d options cannot be used in one command')
    elif recursive:
        files = client.volume_file_list(volume_id, path=path, recursive=True).results
    elif directory:
        if not path:
            raise ExitException('[Error] path must be specified to run -d option')

        file = client.volume_file_read(volume_id, path)
        files = [file] if file is not None else None
    else:
        files = client.volume_file_list(volume_id, path=path, recursive=False).results

    if files is None:
        raise ExitException('No such file or directory.')

    if len(files) == 0:
        raise ExitException('This directory is empty.', exit_code=0)

    print_file_list(files, recursive)


def volume_file_remove(ctx: Context, volume_id: int, path: str, recursive: bool):
    client = ctx.authenticated_client
    try:
        file = client.volume_file_read(volume_id, path)
    except NoSuchFileOrDirectoryAPIException:
        raise ExitException('[Error] Request entity not found')

    if file.is_dir:
        if not recursive:
            raise ExitException('[Error] Remove directory should use -r option')

        deleted_files = client.volume_file_delete(volume_id, path, True).deleted_files
    else:
        deleted_files = client.volume_file_delete(volume_id, path, False).deleted_files

    if not deleted_files:
        raise ExitException('[Error] Server error')

    typer.echo('Successfully deleted files:')
    print_file_list(deleted_files, True)


def print_file_list(files, recursive):
    files = sorted(files, key=lambda f: f.path if recursive else (not f.is_dir, f.path))

    table_content = []
    for file in files:
        row = [file.path if recursive else file.path.rsplit('/', 1)[-1],
               '' if file.is_dir else sizeof_fmt(file.size)]
        if file.is_dir:
            row[0] += '/'
        table_content.append(row)

    table = AsciiTable(table_content)
    table.inner_column_border = False
    table.inner_heading_row_border = False
    table.inner_footing_row_border = False
    table.outer_border = False

    typer.echo(table.table)


def volume_file_copy(ctx: Context, source_volume_id, source_path, dest_volume_id, dest_path, recursive, watch):
    client = ctx.authenticated_client
    while True:
        if source_volume_id is not None and dest_volume_id is not None:
            volume_file_copy_remote_to_remote(
                client,
                source_volume_id, source_path,
                dest_volume_id, dest_path,
                recursive,
            )

        elif source_volume_id is not None and dest_volume_id is None:
            volume_file_copy_remote_to_local(
                client,
                source_volume_id, source_path,
                dest_path,
                recursive,
            )

        elif source_volume_id is None and dest_volume_id is not None:
            volume_file_copy_local_to_remote(
                client,
                source_path,
                dest_volume_id, dest_path,
                recursive,
            )
        else:
            typer.echo('Use \'svds://\' scheme for remote files')
            return

        if not watch:
            return

        time.sleep(10)


def volume_file_copy_remote_to_remote(
    client,
    source_volume_id, source_path,
    dest_volume_id, dest_path,
    recursive,
):
    # remote -> remote
    if source_volume_id != dest_volume_id:
        raise ExitException('Currently files can be copied only within the same volume.')

    source_file = client.volume_file_read(source_volume_id, source_path)
    if source_file is None:
        raise ExitException(f'No such file or directory: {source_path}')

    if source_file.is_dir and not recursive:
        raise ExitException(f'Source path is a directory, you should call with --recursive option.')

    try:
        dest_file = client.volume_file_read(dest_volume_id, dest_path)
    except NoSuchFileOrDirectoryAPIException:
        pass
    else:
        if source_file.is_dir and not dest_file.is_dir:
            raise ExitException(f'Source path is a directory, but destination path is a file.')
    finally:
        resp = client.volume_file_copy(
            source_volume_id, source_path,
            dest_path, recursive=recursive,
        )
        typer.echo('Successfully copied files:')
        print_file_list(resp.copied_files, True)


def volume_file_copy_remote_to_local(
    client,
    source_volume_id, source_path,
    dest_path,
    recursive,
):
    hashmap = defaultdict(lambda: '')
    try:
        source_file = client.volume_file_read(source_volume_id, source_path)
    except NoSuchFileOrDirectoryAPIException:
        raise ExitException(f'Source file does not exist: {source_path}')

    if source_file.is_dir:
        if not recursive:
            raise ExitException(f'Source path is a directory, you should call with --recursive option.')

        if os.path.exists(dest_path) and not os.path.isdir(dest_path):
            raise ExitException(f'Destination path is not a directory: {dest_path}')

        # download directory
        typer.echo('Fetching file metadata...')
        files = client.volume_file_list(
            source_volume_id,
            path=source_path,
            recursive=True,
            need_download_url=True,
        ).results
        files = [file for file in files if hashmap[file.path] != file.hash]

        if source_path.endswith('/'):
            for file in files:
                file.path = file.path.replace(source_path, '', 1)
        else:
            dir_name = os.path.dirname(source_path)
            for file in files:
                if dir_name:
                    file.path = file.path.replace(dir_name + '/', '', 1)

        typer.echo(f'Found {len(files)} files to download.')
        if len(files) > 0:
            typer.echo('Downloading...')
            Downloader.bulk_download(dest_path, files, progressable=typer.progressbar)
            for file in files:
                hashmap[file.path] = file.hash
            typer.echo('Successfully downloaded.')
    else:
        # download file
        dest_file_path = dest_path
        if os.path.isdir(dest_path):
            dest_file_path = os.path.join(dest_path, os.path.basename(source_file.path))

        Downloader.download(dest_file_path, source_file, progressable=typer.progressbar)
        hashmap[source_file.path] = source_file.hash
        typer.echo('Successfully downloaded.')


def volume_file_copy_local_to_remote(
    client,
    source_path,
    dest_volume_id, dest_path,
    recursive,
):
    hashmap = defaultdict(lambda: '')
    if not os.path.exists(source_path):
        raise ExitException(f'No such file or directory: {source_path}')

    try:
        dest_file = client.volume_file_read(dest_volume_id, dest_path)
    except NoSuchFileOrDirectoryAPIException:
        dest_file = None

    if os.path.isdir(source_path):
        if not recursive:
            raise ExitException(f'Source path is a directory, you should call with --recursive option.')

        files = Uploader.get_files_to_upload(source_path, hashmap)
        if dest_file is None:
            # x/y/dir1/ -> c/ (not exist)
            # x/y/dir1/file1/ -> c/file1
            dest_base_path = dest_path
        elif dest_file.is_dir:
            # x/y/dir1/ -> c/ (exist path)
            # x/y/dir1/file1/ -> c/dir1/file1
            if source_path.endswith('/'):
                dest_base_path = dest_path
            else:
                dest_base_path = os.path.join(dest_path, os.path.basename(remove_suffix(source_path, "/")))
        else:
            raise ExitException(f'Destination path is not a directory: {dest_path}')

        typer.echo(f'Found {len(files)} files to upload.')
        if len(files) > 0:
            typer.echo('Uploading...')
            resp = Uploader.bulk_upload(client, source_path, files, dest_volume_id, dest_base_path)
            typer.echo('Successfully uploaded.')
            return resp
    else:
        # x/y/dir1/file1 ->
        if dest_file is None:
            if dest_path.endswith('/'):
                resp = Uploader.upload(client, source_path, dest_volume_id, os.path.join(dest_path, os.path.basename(source_path)))
            else:
                resp = Uploader.upload(client, source_path, dest_volume_id, dest_path)
        elif dest_file.is_dir:
            resp = Uploader.upload(client, source_path, dest_volume_id, os.path.join(dest_path, os.path.basename(source_path)))
        else:
            resp = Uploader.upload(client, source_path, dest_volume_id, dest_path)
        typer.echo('Successfully uploaded.')
        return resp
