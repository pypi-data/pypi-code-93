import click
from shutil import which
from pathlib import Path
import subprocess
import os
import dateutil.parser

import requests

from ocean import api, code, utils
from ocean.main import pass_env


@click.group(cls=utils.AliasedGroup)
def cli():
    pass


@cli.command()
@click.argument("name")
@click.argument("path")
@pass_env
def upload(ctx, name, path):
    if which("rsync") is None:
        print(
            """rsync is not installed in host. Please install rsync using below guide.
        
## Ubuntu, Debian
$ apt update
$ apt install rsync

## Centos, RHEL, Fedora
$ yum install rsync

## Brew
$ brew update
$ brew install rsync
"""
        )
        return

    if not Path(path).exists():
        print(f"{path} is not valid file path.")
        return

    file_size = os.path.getsize(path)

    data = {"filename": name, "name": Path(path).name, "dataSize": file_size}
    response = api.post(ctx, code.API_DATASYNC, data=data)
    # response = api.datasync_create(ctx, name, Path(path).name, file_size)
    if response.status_code == 409:  # TODO: 이미 올라간 데이터셋을 오버라이드하기? (변경사항 생긴것만 업로드하기)
        print(f'Data name "{name}" already exists.')
        return

    rsync_metadata = response.json()
    datasyncer_endpoint = rsync_metadata["dataSyncerEndpoint"]
    datasyncer_ip = datasyncer_endpoint.split(":")[0]

    rsync_command = "rsync --progress -av {} {}::{}/{}/".format(
        path, datasyncer_ip, rsync_metadata["rsyncModule"], ctx.get_username()
    )
    subprocess.call(rsync_command.split())

    # Bootstrap data node는 data syncer 또한 서빙하고 있다고 가정한다.
    data_distribute_endpoint = f"http://{datasyncer_endpoint}/sync"
    print("\nCompleted upload data to server. Starting to distribute data to servers..")
    res = requests.post(
        data_distribute_endpoint,
        json={
            "target_servers": ["*"],
            "filename": Path(path).name,
            "username": utils.get_username(),
            "name": name,
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(utils.get_token()),
        },
    )

    if res.status_code != 200:
        print("Failed to request data distribution.")
    else:
        print(
            f'Succeeded to request data distribution. Use "ocean data list" to check progress.'
        )


@cli.command()
@pass_env
def list(ctx):
    res = api.get(ctx, "/api/datasync")
    datasync_list = res.json()

    width = 30
    print(
        "Created".ljust(width),
        "Data Name".ljust(width),
        "Uploaded File Name".ljust(width),
        "Upload Status".ljust(width),
        sep="",
    )
    for datasync in datasync_list:
        date = dateutil.parser.isoparse(datasync["createdAt"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        print(
            date.ljust(width),
            datasync["name"].ljust(width),
            datasync["filename"].ljust(width),
            datasync["status"].ljust(width),
            sep="",
        )
