import os
from typing import List, Optional

import typer
import yaml

from savvihub.cli.constants import PROJECT_TYPE_VERSION_CONTROL, PROJECT_TYPE_CLI_DRIVEN
from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context
from savvihub.cli.utils import inquire_list, inquire_text


def experiment_config_file_callback(ctx: Context, filepath: str) -> Optional[str]:
    if not filepath:
        return

    if not os.path.isfile(filepath):
        raise ExitException(f'File does not exist: {filepath}')

    try:
        yaml.safe_load(filepath)
    except yaml.YAMLError:
        raise ExitException(f'Invalid YAML: {filepath}')

    with open(filepath, 'r') as stream:
        configs = yaml.load(stream, Loader=yaml.FullLoader)

    ctx.spec['experiment'] = configs['spec']['experiment']


def message_callback(ctx: Context, message: str) -> str:
    if message:
        ctx.store['message'] = message
        return ctx.store['message']

    if ctx.spec['experiment'].get('message'):
        ctx.store['message'] = ctx.spec['experiment'].get('message')
        return ctx.store['message']

    inquirer_message = ""
    if ctx.project.type == PROJECT_TYPE_VERSION_CONTROL:
        inquirer_message = "Message(set to commit message if you passed empty)"
    elif ctx.project.type == PROJECT_TYPE_CLI_DRIVEN:
        inquirer_message = "Message"

    message = inquire_text(inquirer_message)
    ctx.store['message'] = message
    return ctx.store['message']


def start_command_callback(ctx: Context, start_command: str) -> str:
    if start_command:
        ctx.store['start_command'] = start_command
        return ctx.store['start_command']

    if ctx.spec['experiment'].get('start_command'):
        ctx.store['start_command'] = ctx.spec['experiment'].get('start_command')
        return ctx.store['start_command']

    start_command = inquire_text("Start command", "python main.py")
    ctx.store['start_command'] = start_command
    return ctx.store['start_command']


def cluster_name_callback(ctx: Context, cluster_name: str) -> str:
    assert ctx.params['organization_name']

    clusters = ctx.authenticated_client.cluster_list(ctx.params['organization_name']).clusters
    clusters = {c.name: c for c in clusters if c.status == 'connected'}

    cluster_name = cluster_name.strip()
    if not cluster_name:
        cluster_name = ctx.spec['experiment'].get('cluster')
    
    if cluster_name:
        if cluster_name in clusters:
            ctx.store['cluster'] = clusters[cluster_name]
        else:
            raise ExitException(f'Cluster not found: {cluster_name}')

    elif len(clusters) == 1:
        selected_cluster = list(clusters.values())[0]
        ctx.store['cluster'] = selected_cluster
        typer.echo(
            f'The cluster is automatically set to '
            f'`{selected_cluster.name}{" (SavviHub)" if selected_cluster.is_savvihub_managed else f" (Custom)"}`.'
        )

    else:
        selected_cluster = inquire_list(
            "Please choose a cluster",
            [(f'{x.name}{" (SavviHub)" if x.is_savvihub_managed else f" ({x.name})"}', x) for x in clusters.values()]
        )
        ctx.store['cluster'] = selected_cluster

    return ctx.store['cluster'].name


def image_url_callback(ctx: Context, image_url: str) -> str:
    assert ctx.params['organization_name'] and ctx.params['processor_type']

    image_url = image_url.strip()
    if image_url:
        ctx.store['image_url'] = image_url
        return image_url

    image_url = ctx.spec['experiment'].get('image_url')

    images = ctx.authenticated_client.kernel_image_list(ctx.params['organization_name']).results
    images = {i.image_url: i for i in images if i.processor_type == ctx.params['processor_type']}

    if not image_url:
        selected_image = inquire_list(
            "Please choose a kernel image",
            [(f'{x.image_url} ({x.name})', x.image_url) for x in images.values()],
        )
        ctx.store['image_url'] = selected_image
    
    return ctx.store['image_url']


def env_vars_callback(ctx: Context, env_vars: List[str]) -> List[str]:
    if ctx.spec['experiment'].get('env_vars'):
        if not isinstance(ctx.spec['experiment'].get('env_vars'), List):
            raise ExitException(f'Invalid environment variables in YAML')
        env_vars += tuple(ctx.spec['experiment']['env_vars'])

    ctx.store['env_vars'] = []
    for env_var in env_vars:
        try:
            env_key, env_value = env_var.split("=", 1)
            ctx.store['env_vars'].append({
                'key': env_key,
                'value': env_value,
            })
        except ValueError:
            raise ExitException(f'Cannot parse environment variable: {env_var}')
    
    return ctx.store['env_vars']
