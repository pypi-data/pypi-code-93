import os
from pathlib import Path
from typing import Optional

import inquirer
from sshpubkeys import SSHKey, InvalidKeyError

from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context


def ssh_public_key_value_callback(ctx: Context, key_path: str) -> str:
    if not key_path:
        key_path = inquirer.prompt([inquirer.Text(
            'question',
            message='SSH public key path',
            default=f'{Path.home()}/.ssh/id_ed25519.pub',
        )], raise_keyboard_interrupt=True).get('question')

    try:
        with open(key_path, 'r') as f:
            ssh_public_key_value = f.read()
    except FileNotFoundError:
        raise ExitException('Key file not found.')

    ssh = SSHKey(ssh_public_key_value, strict=True)
    try:
        ssh.parse()
    except InvalidKeyError as e:
        raise ExitException('Invalid key:', e)
    except NotImplementedError as e:
        raise ExitException('Invalid key type:', e)

    ctx.store['ssh_key_name'] = ssh.comment
    ctx.store['ssh_key_filename'] = os.path.basename(key_path)
    return ssh_public_key_value


def ssh_key_name_callback(ctx: Context, name: str) -> str:
    if name:
        return name

    return inquirer.prompt([inquirer.Text(
        'question',
        message='SSH public key name',
        default=ctx.store.get('ssh_key_name'),
    )], raise_keyboard_interrupt=True).get('question')


def ssh_private_key_path_callback(ctx: Context, key_path: str) -> Optional[str]:
    if key_path:
        return key_path

    ssh_keys_response = ctx.authenticated_client.ssh_key_list()
    if len(ssh_keys_response.ssh_keys) == 0:
        raise ExitException('At least one ssh public key should be added.\n'
                            'Please run `savvihub ssh keys add`.')

    home = Path.home()

    for ssh_key in ssh_keys_response.ssh_keys:
        key_path = f'{home}/.ssh/{ssh_key.filename.rstrip(".pub")}'
        if os.path.exists(key_path):
            return key_path

    for key_path in (f'{home}/.ssh/id_rsa', f'{home}/.ssh/id_ed25519'):
        if os.path.exists(key_path):
            return key_path

    return None
