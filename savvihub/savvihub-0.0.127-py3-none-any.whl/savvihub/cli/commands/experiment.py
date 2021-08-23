from datetime import datetime
from typing import List

import typer
from terminaltables import AsciiTable

from openapi_client import (
    ModelKernelResourceSpecField,
    ProtoVolumeMountRequest,
    ProtoVolumeMountRequestSourceCLIDrivenProject,
    ProtoVolumeMountRequestSourceProject,
    ProtoVolumeMountRequestSourceVersionControlProject,
    ProtoVolumeMountRequests,
)
from savvihub.cli.commands.volume import volume_file_list, volume_file_copy
from savvihub.cli.constants import WEB_HOST, PROJECT_TYPE_VERSION_CONTROL, PROJECT_TYPE_CLI_DRIVEN
from savvihub.cli.exceptions import ExitException
from savvihub.cli.formatter import TreeFormatter
from savvihub.cli.inputs.experiment import (
    cluster_name_callback,
    env_vars_callback,
    image_url_callback,
    message_callback,
    start_command_callback,
)
from savvihub.cli.inputs.experiment import experiment_config_file_callback
from savvihub.cli.inputs.git import git_branch_callback, git_ref_callback, git_diff_callback
from savvihub.cli.inputs.organization import organization_name_option
from savvihub.cli.inputs.project import project_name_option, local_project_callback
from savvihub.cli.inputs.resource import (
    cpu_limit_callback,
    gpu_limit_callback,
    gpu_type_callback,
    memory_limit_callback,
    processor_type_callback,
    resource_name_callback,
)
from savvihub.cli.inputs.volume import dataset_mount_callback
from savvihub.cli.typer import Typer, Context
from savvihub.common.utils import (
    parse_time_to_ago,
    short_string,
)

experiment_output_app = Typer()
experiment_app = Typer()
experiment_app.add_typer(experiment_output_app, name='output')


@experiment_app.callback()
def main():
    """
    Run the machine learning experiment
    """
    return


def parse_resource_spec(resource_spec):
    if not resource_spec.name:
        resource_desc = "[Custom]"
        if resource_spec.processor_type == "gpu":
            resource_desc += "g" + str(int(resource_spec.gpu_limit)) + "."
        resource_desc += "c" + str(int(resource_spec.cpu_limit)) + "."
        resource_desc += "r" + resource_spec.memory_limit[:-2]
        return resource_desc
    return resource_spec.name


@experiment_app.command(user_required=True)
def list(
    ctx: Context,
    organization_name: str = organization_name_option,
    project_name: str = project_name_option,
):
    """
    Display a list of experiments
    """
    experiments = ctx.authenticated_client.experiment_list(organization_name, project_name).results
    if not experiments:
        raise ExitException(f'There is no experiment in `{project_name}` project.')

    table = AsciiTable([
        ['NUMBER', 'NAME', 'STATUS', 'CREATED', 'RESOURCE', 'MESSAGE'],
        *[[e.number, e.name, e.status, parse_time_to_ago(e.created_dt),
           parse_resource_spec(e.kernel_resource_spec),
           f'"{short_string(e.message, 25)}"']
          for e in experiments],
    ])
    table.inner_column_border = False
    table.inner_heading_row_border = False
    table.inner_footing_row_border = False
    table.outer_border = False

    typer.echo(table.table)


@experiment_app.command(user_required=True)
def describe(
    ctx: Context,
    organization_name: str = organization_name_option,
    project_name: str = project_name_option,
    experiment_number_or_name: str = typer.Argument(..., help="The unique experiment number or name"),
):
    """
    Describe the experiment in details
    """
    experiment = ctx.authenticated_client.experiment_read(organization_name, project_name, experiment_number_or_name)
    timezone = datetime.now().astimezone().tzinfo

    root = TreeFormatter()
    root.add_child(f'Number: {experiment.number}',
                   f'Name: {experiment.name}',
                   f'Created: {experiment.created_dt.astimezone(timezone)}',
                   f'Updated: {experiment.updated_dt.astimezone(timezone)}',
                   f'Git Commit: ({experiment.git_ref[:7]}) {experiment.message}')

    if experiment.source_code_link:
        root.add_child(f'Source code link: {experiment.source_code_link[0].url}')

    if experiment.git_diff_file:
        git_diff_file_desc = TreeFormatter('Git Diff File:')
        git_diff_file_desc.add_child(f'URL: {experiment.git_diff_file.download_url["url"]}')
        root.add_child(git_diff_file_desc)

    root.add_child(f'Status: {experiment.status}',
                   f'Tensorboard: {experiment.tensorboard or "N/A"}')

    # Kernel Image Description
    kernel_image_desc = TreeFormatter('Kernel Image:')
    kernel_image_desc.add_child(f'Name: {experiment.kernel_image.name}',
                                f'URL: {experiment.kernel_image.image_url}',
                                f'Language: {experiment.kernel_image.language or "N/A"}')
    root.add_child(kernel_image_desc)

    # Resource Spec Description
    resource_spec_desc = TreeFormatter('Resource Spec:')
    resource_spec_desc.add_child(f'Name: {experiment.kernel_resource_spec.name}',
                                 f'CPU Type: {experiment.kernel_resource_spec.name}',
                                 f'CPU Limit: {experiment.kernel_resource_spec.cpu_limit}',
                                 f'Memory Limit: {experiment.kernel_resource_spec.memory_limit}',
                                 f'GPU Type: {experiment.kernel_resource_spec.gpu_type}',
                                 f'GPU Limit: {experiment.kernel_resource_spec.gpu_limit}')
    root.add_child(resource_spec_desc)

    # Datasets Description
    datasets_desc = TreeFormatter('Datasets:')
    found = False
    for volume_mount in experiment.volume_mounts.mounts:
        if volume_mount.source_type == 'dataset':
            dataset_desc = TreeFormatter(volume_mount.dataset.dataset.name)
            dataset_desc.add_child(f'Mount Path: {volume_mount.path}')
            datasets_desc.add_child(dataset_desc)
            found = True
    if not found:
        datasets_desc.add_child('Dataset Not Found')
    root.add_child(datasets_desc)

    # Histories Description
    histories_desc = TreeFormatter('Histories:')
    if not experiment.histories:
        histories_desc.add_child('History Not Found')
    else:
        for history in experiment.histories:
            history_desc = TreeFormatter(history.status)
            history_desc.add_child(f'Started: {datetime.fromtimestamp(history.started_timestamp, tz=timezone).strftime("%Y-%m-%d %H:%M:%S.%f%z")}',
                                   f'Ended: {datetime.fromtimestamp(history.ended_timestamp, tz=timezone).strftime("%Y-%m-%d %H:%M:%S.%f%z") if history.ended_timestamp else "N/A"}')
            histories_desc.add_child(history_desc)
    root.add_child(histories_desc)

    # Plots Description
    plots_desc = TreeFormatter('Plots:')
    full_plots_info_desc = TreeFormatter('Full plots at:')
    full_plots_info_desc.add_child(f'{WEB_HOST}/{organization_name}/{project_name}/experiments/{experiment.number}/plots')
    plots_desc.add_child(full_plots_info_desc)
    root.add_child(plots_desc)
    root.add_child(f'Start Command: {experiment.start_command}')

    typer.echo(root.format())


@experiment_app.command(user_required=True)
def logs(
    ctx: Context,
    organization_name: str = organization_name_option,
    project_name: str = project_name_option,
    experiment_number_or_name: str = typer.Argument(..., help="The unique experiment number or name"),
    tail: int = typer.Option(200, "--tail"),
    detail: bool = typer.Option(False, "--detail", hidden=True),
    all: bool = typer.Option(False, "--all", hidden=True),
):
    """
    Display the last fifty lines of the experiment logs
    """
    client = ctx.authenticated_client

    kwargs = {}
    if not all:
        kwargs = {'limit': tail}
    if detail:
        kwargs = {'with_event_log': 'true'}

    experiment_logs = client.experiment_logs(
        organization_name, project_name, experiment_number_or_name, **kwargs).logs

    all_logs = []
    for _, logs in experiment_logs.items():
        all_logs.extend(logs)

    timezone = datetime.now().astimezone().tzinfo
    log_str = ''
    for log in sorted(all_logs, key=lambda x: x.timestamp):
        log_str += f'[{datetime.fromtimestamp(log.timestamp, tz=timezone).strftime("%H:%M:%S.%f")}] {log.message}\n'

    typer.echo(log_str)
    typer.echo(
        f'Full logs at:\n'
        f'    {WEB_HOST}/{organization_name}/{project_name}/experiments/{experiment_number_or_name}/logs\n'
    )


@experiment_app.command(user_required=True)
def run(
    ctx: Context,
    organization_name: str = organization_name_option,
    project_name: str = project_name_option,
    file: str = typer.Option(None, "--file", "-f", callback=experiment_config_file_callback, help="Experiment config file"),
    message: str = typer.Option("", "--message", "-m", callback=message_callback, help="Experiment message"),
    start_command: str = typer.Option("", "--start-command", callback=start_command_callback,
                                      help="Start command"),
    cluster_name: str = typer.Option("", "--cluster", "-c", callback=cluster_name_callback,
                                     help="Cluster name"),
    resource_name: str = typer.Option(None, "--resource", "-r", callback=resource_name_callback,
                                      help="Resource name (for savvihub-managed cluster)"),
    processor_type: str = typer.Option(None, "--processor-type", callback=processor_type_callback,
                                       help="cpu or gpu (for custom cluster)"),
    cpu_limit: float = typer.Option(0, "--cpu-limit", callback=cpu_limit_callback,
                                    help="Number of vCPUs (for custom cluster)"),
    memory_limit: str = typer.Option(None, "--memory-limit", callback=memory_limit_callback,
                                     help="Memory capacity (ex: 4Gi, 500Mi)"),
    gpu_type: str = typer.Option(None, "--gpu-type", callback=gpu_type_callback,
                                 help="GPU product name such as Tesla-K80 (for custom cluster)"),
    gpu_limit: int = typer.Option(0, "--gpu-limit", callback=gpu_limit_callback,
                                  help="Number of GPU cores (for custom cluster)"),
    image_url: str = typer.Option("", "--image", "-i", callback=image_url_callback,
                                  help="Kernel docker image URL"),
    dataset_mounts: List[str] = typer.Option([], "--dataset", "-d", callback=dataset_mount_callback,
                                             help="Dataset mounted path"),
    env_vars: List[str] = typer.Option([], "-e", callback=env_vars_callback, help="Environment variables"),
    ignore_git_diff: bool = typer.Option(False, "--ignore-git-diff", help="Ignore git diff flag"),
    git_branch: str = typer.Option(None, "--git-branch", callback=git_branch_callback, help="Git branch name"),
    git_ref: str = typer.Option(None, "--git-ref", callback=git_ref_callback, help="Git commit SHA"),
    git_diff_arg: str = typer.Option(None, "--git-diff", callback=git_diff_callback, help="Git diff file URL"),
    local_project: str = typer.Option(None, "--local-project", callback=local_project_callback,
                                      help="Local project file URL"),
    output_dir: str = typer.Option("/output/", "--output-dir",
                                   help="A directory to which the experiment result output files to be stored."),
    working_dir: str = typer.Option(None, "--working-dir", help="If not present, use `/work/{project_name}`."),
    root_volume_size: str = typer.Option(None, "--root-volume-size", help="Root volume size"),
):
    """
    Run an experiment in SavviHub
    """
    resource_spec = resource_spec_id = None
    if ctx.store['cluster'].is_savvihub_managed:
        resource_spec_id = ctx.store['resource_spec_id']
    else:
        resource_spec = ModelKernelResourceSpecField(
            processor_type=processor_type,
            cpu_type='Any',
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            gpu_type=gpu_type,
            gpu_limit=gpu_limit,
        )

    project_volume_mount = ProtoVolumeMountRequestSourceProject(
        project_id=ctx.project.id,
    )
    project_mount_path = "/work/"
    if ctx.project.type == PROJECT_TYPE_VERSION_CONTROL:
        project_volume_mount.project_type = PROJECT_TYPE_VERSION_CONTROL
        project_volume_mount.version_control_project = ProtoVolumeMountRequestSourceVersionControlProject(
            project_branch=git_branch,
            project_git_ref=git_ref,
            project_git_diff=ctx.store.get('git_diff_uploaded_path')
        )
        project_mount_path += f"{project_name}"
    elif ctx.project.type == PROJECT_TYPE_CLI_DRIVEN:
        project_volume_mount.project_type = PROJECT_TYPE_CLI_DRIVEN
        project_volume_mount.cli_driven_project = ProtoVolumeMountRequestSourceCLIDrivenProject(
            local_project=ctx.store.get('local_project_uploaded_path')
        )

    volume_mounts_requests = ctx.store['dataset_mounts'] + [
        ProtoVolumeMountRequest(
            mount_type='output',
            mount_path=output_dir,
        ),
        ProtoVolumeMountRequest(
            mount_type='project',
            mount_path=project_mount_path,
            project=project_volume_mount,
        ),
    ]
    if project_mount_path != '/work/':
        volume_mounts_requests.append(ProtoVolumeMountRequest(
            mount_type='empty-dir',
            mount_path='/work/'
        ))

    experiment = ctx.authenticated_client.experiment_create(
        organization=organization_name,
        project=project_name,
        message=message,
        cluster_name=ctx.store['cluster'].name,
        image_url=image_url,
        resource_spec_id=resource_spec_id,
        resource_spec=resource_spec,
        start_command=start_command,
        env_vars=ctx.store['env_vars'],
        volume_mounts=ProtoVolumeMountRequests(
            root_volume_size=root_volume_size,
            working_dir=working_dir,
            requests=volume_mounts_requests,
        ),
    )

    typer.echo(
        f'Experiment {experiment.number} is running. Check the experiment status at below link\n'
        f'{WEB_HOST}/{organization_name}/{project_name}/experiments/{experiment.number}'
    )


@experiment_output_app.callback()
def output_main():
    """
    Manage experiment output files
    """


@experiment_output_app.command(user_required=True)
def ls(
    ctx: Context,
    organization_name: str = organization_name_option,
    project_name: str = project_name_option,
    experiment_number_or_name: str = typer.Argument(..., help="The unique experiment number or name"),
    path: str = typer.Argument(None, help='Output file path'),
    recursive: bool = typer.Option(False, '-r', '--recursive', help='recursive flag'),
    directory: bool = typer.Option(False, '-d', '--directory',
                                   help='list the directory itself, not its contents'),
):
    """
    List the output files of the experiment
    """
    experiment = ctx.authenticated_client.experiment_read(organization_name, project_name, experiment_number_or_name)
    if len(experiment.volume_mounts.mounts) > 0:
        for volume_mount in experiment.volume_mounts.mounts:
            if volume_mount.source_type == 'output':
                volume_file_list(ctx, volume_mount.volume.volume.id, 'latest', path or '', recursive, directory)
    else:
        raise ExitException('No output volume mounted.')


@experiment_output_app.command(user_required=True)
def download(
    ctx: Context,
    organization_name: str = organization_name_option,
    project_name: str = project_name_option,
    experiment_number_or_name: str = typer.Argument(..., help="The unique experiment number or name"),
    dest_path: str = typer.Argument(None, help='The files will be downloaded to ./output if omitted.'),
):
    """
    Download experiment output files
    """
    experiment = ctx.authenticated_client.experiment_read(organization_name, project_name, experiment_number_or_name)
    if len(experiment.volume_mounts.mounts) > 0:
        for volume_mount in experiment.volume_mounts.mounts:
            if volume_mount.source_type == 'output':
                volume_file_copy(
                    ctx, volume_mount.volume.volume.id,
                    '', None, dest_path or './output',
                    recursive=True, watch=False)
                break
    else:
        raise ExitException('No output volume mounted.')
