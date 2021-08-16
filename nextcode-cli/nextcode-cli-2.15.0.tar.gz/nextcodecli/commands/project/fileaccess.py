#!/usr/bin/env python
import click
import os
import json
from tabulate import tabulate

from nextcode.exceptions import ServerError
from nextcode.services.project.service import fmt_size
from ...utils import get_logger, abort, print_tab, dumps
from . import check_project

log = get_logger(name='commands.project', level='INFO')


@click.command("credentials")
@click.option('--create', is_flag=True, default=False, help='Create new credentials')
@click.option(
    '--raw', 'is_raw', is_flag=True, default=False, help='Raw JSON response from endpoint'
)
@click.pass_context
def credentials(ctx, create, is_raw):
    svc = ctx.obj.service
    try:
        ret = svc.get_credentials(create)
    except Exception as ex:
        abort(str(ex))
    if is_raw:
        print(json.dumps(ret, default=str))
        return
    else:
        click.echo("{0:22}{1}".format('AWS_ACCESS_KEY_ID', ret["aws_access_key_id"]))
        click.echo("{0:22}{1}".format('AWS_SECRET_ACCESS_KEY', ret["aws_secret_access_key"]))


@click.command("list")
@click.argument('path', required=False)
@click.option(
    '--raw', 'is_raw', is_flag=True, default=False, help='Raw JSON response from endpoint'
)
@click.pass_context
@check_project
def list_bucket(ctx, path, is_raw):
    """
    List files in the project tree
    """
    if not path:
        path = ""
    svc = ctx.obj.service
    ret = svc.list(path, raw=True)

    if is_raw:
        print(json.dumps(ret, default=str))
        return

    lst = []
    for r in ret:
        r["size"] = fmt_size(r["size"])
        try:
            r["modified"] = r["modified"].strftime("%b %d %H:%M")
        except Exception:
            pass
        if r["type"] == "file":
            r["name"] = r["name"].split("/")[-1]
        else:
            r["name"] = r["name"].split("/")[-2] + "/"
        lst.append([r["type"], r["size"], r["modified"], r["name"]])

    txt = tabulate(lst, headers=["type", "size", "modified", "name"])
    click.secho(f"Contents of {path}:", bold=True)
    print(txt)


@click.command()
@click.argument('filename', required=True)
@click.argument('path', required=True)
@click.pass_context
@check_project
def upload(ctx, filename, path):
    """
    Upload a file into the project tree
    """
    svc = ctx.obj.service
    try:
        remote_path = svc.upload(filename, path)
        click.secho(f"file has been uploaded to {remote_path}", bold=True)
    except Exception as e:
        log.debug(f"Error uploading {filename} to {path}: {e}")
        abort(str(e))


@click.command()
@click.argument('filename', required=True)
@click.argument('path', required=False)
@click.pass_context
@check_project
def download(ctx, filename, path):
    """
    Download a file from the project tree
    """
    if not path:
        path = "."
    svc = ctx.obj.service
    try:
        local_path = svc.download(filename, path)
        click.secho(f"file has been downloaded to {local_path}", bold=True)
    except Exception as e:
        log.debug(f"Error downloading {filename}: {e}")
        abort(str(e))


@click.command()
@click.argument('filename', required=True)
@click.option('--bytes', '-n', 'num_bytes', default=1024, help='Number of bytes to return')
@click.pass_context
@check_project
def head(ctx, filename, num_bytes):
    """
    Show the first n bytes from a file
    """
    svc = ctx.obj.service
    # TODO: Move into sdk
    bucket = svc.get_project_bucket()
    client = bucket.meta.client
    start_byte = 0
    stop_byte = num_bytes
    resp = client.get_object(
        Bucket=bucket.name, Key=filename, Range='bytes={}-{}'.format(start_byte, stop_byte)
    )
    contents = resp['Body'].read()
    try:
        # skip the last line since it's likely incomplete
        lines = contents.decode().split("\n")
        print("\n".join(lines[:-1]))
    except Exception:
        print(contents)


@click.command()
@click.argument('filename', required=True)
@click.pass_context
@check_project
def delete(ctx, filename):
    """
    Delete a file in the project tree
    """
    raise NotImplementedError("It is not a good idea to delete things.")
    svc = ctx.obj.service
    # TODO: Move into sdk?
    bucket = svc.get_project_bucket()
    resp = bucket.delete_objects(Delete={"Objects": [{"Key": filename}]})
