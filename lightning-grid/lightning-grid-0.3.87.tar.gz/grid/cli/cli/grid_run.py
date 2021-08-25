from collections import OrderedDict
import json
from pathlib import Path
import shlex
import sys
from typing import Any, Dict, Optional

import click

from grid.cli import rich_click
from grid.cli.cli.utilities import read_config_callback, validate_config
from grid.cli.client import Grid
import grid.cli.globals as env
from grid.cli.types import WorkflowType
from grid.cli.utilities import check_description_isnt_too_long
from grid.sdk.action import validate_and_configure_datastore
from grid.sdk.source_code.dependency_manager import find_package_manager
from grid.sdk.utils.name_generator import unique_name


def _check_run_name_is_valid(_ctx, _param, value):
    """Click callback that checks if a Run contains reserved names."""
    if value is not None:
        fail = False

        #  Check if the input is alphanumeric.
        _run_name = value.replace('-', '')
        if not _run_name.isalnum():
            fail = True

        #  Check if the allowed `-` character is not used
        #  at the end of the string.
        elif value.endswith('-') or value.startswith('-'):
            fail = True

        #  Check that the run name does not contain any
        #  uppercase characters.
        elif any(x.isupper() for x in value):
            fail = True

        if fail:
            raise click.BadParameter(
                f"""

            Invalid Run name: {value} the Run name must be lower case
            alphanumeric characters or '-', start with an alphabetic
            character, and end with an alphanumeric character (e.g. 'my-name',
            or 'abc-123').

                """
            )

    return value


def _check_ignore_warnings_flag(ctx, _param, value):
    """
    Click callback that assigns the value of the ignore warnings callback
    to a global variable.
    """
    if value is not None:
        env.IGNORE_WARNINGS = value

    return value


def _generate_default_grid_config(
    instance_type: str,
    cluster: Optional[str] = None,
    use_spot: Optional[bool] = None,
    grid_strategy: Optional[str] = None,
    grid_trials: Optional[int] = None,
    gpus: Optional[int] = None,
    memory: str = None,
    cpus: Optional[int] = None,
    datastore_name: Optional[str] = None,
    datastore_version: Optional[int] = None,
    datastore_mount_dir: Optional[str] = None,
    framework: Optional[str] = None,
    localdir: Optional[bool] = None,
    dockerfile: Optional[bool] = None,
    scratch_size: Optional[int] = None,
    scratch_mount_path: Optional[str] = None,
    dependency_file: Optional[str] = None,
):
    """
    Generates a new default config file for user if user hasn't
    submitted one.
    """

    #  Relevant defaults for user.
    #  TODO: Pull from user profile when we have
    #  that information collected.
    provider = {
        'vendor': "aws",
        'credentials': "n/a",
        'region': 'us-east-1',
    }
    if cluster:
        provider['cluster'] = cluster

    _grid_config = {
        'compute': {
            'provider': provider,
            'train': {
                'framework': framework,
                'datastore_name': datastore_name,
                'datastore_version': datastore_version,
                'datastore_mount_dir': datastore_mount_dir,
                'instance': instance_type,
                'use_spot': use_spot or False,
                'nodes': 0,  # How many nodes are created at first.
                'gpus': gpus,
                'memory': memory,
                'cpus': cpus,
                'scratch': [],
                'localdir': localdir,
                'dockerfile': dockerfile,
            }
        }
    }

    if dependency_file:
        package_manager = find_package_manager(dependency_file)
        if not localdir:
            dependency_file = Grid.add_git_root_path(dependency_file)
        _grid_config['compute']['train']['dependency_file_info'] = {
            'package_manager': package_manager,
            'path': dependency_file
        }

    if scratch_size:
        _grid_config['compute']['train']['scratch'].append({'size_gb': scratch_size, 'mount_path': scratch_mount_path})

    #  We add a `hyper_params` key to the default config
    #  if the user has passed the `grid_strategy` argument.
    if grid_strategy:
        if not _grid_config.get('hyper_params'):
            _grid_config['hyper_params'] = {}

        _grid_config['hyper_params'] = {'settings': {'strategy': grid_strategy}, 'params': {}}

        #  We also add the key trials if that has been
        #  passed. trials is only valid when doing a `random_search`
        #  at the moment. Our parser will not be bothered by its
        #  presence if we pass it by default.
        if grid_trials:
            _grid_config['hyper_params']['settings']['trials'] = grid_trials

    if env.DEBUG:
        click.echo('Grid Config used:')
        click.echo(_grid_config)

    return _grid_config


def _check_is_valid_extension(ctx, _param, value):
    """Click callback that checks if a file is a Python script."""
    if value is None or not value.exists():
        raise click.BadParameter(f"Script must be a file.")

    if value is not None:
        valid_file_types = ['.py', '.sh', '.jl']
        if not any(value.name.endswith(e) for e in valid_file_types):
            support_email = click.style('support@grid.ai', fg='green')
            message = (
                f'We only support Python (.py), shell (.sh), or Julia (.jl) scripts. Got: {value}.'
                f'Email {support_email} if you want to request support for this file type.'
            )
            raise click.BadParameter(message)

        ctx.params['entrypoint'] = value
        return value
    return None


def _aws_node_to_nickname():
    aws_node_to_nicknames = OrderedDict({
        # AWS
        'p3.16xlarge': '8_v100_16gb',
        'p3dn.24xlarge': '8_v100_32gb',
        'g4dn.metal': '8_t4_16gb',
        'p2.8xlarge': '8_k80_12gb',
        'p3.8xlarge': '4_v100_16gb',
        'g4dn.12xlarge': '4_t4_16gb',
        'g3.16xlarge': '4_m60_8gb',
        'g3.8xlarge': '2_m60_8gb',
        'p3.2xlarge': '1_v100_16gb',
        # 'p4d.24xlarge': '8_a100_40gb',  # currently not supported
        'g4dn.8xlarge': '1_t4_16gb',
        'g4dn.4xlarge': '1_t4_16gb',
        'g4dn.2xlarge': '1_t4_16gb',
        'g4dn.xlarge': '1_t4_16gb',
        'g4dn.16xlarge': '1_t4_16gb',
        'p2.xlarge': '1_k80_12gb',
        'g3s.xlarge': '1_m60_8gb',
        'g3.4xlarge': '1_m60_8gb',
        't2.large': '2_cpu_8gb',
        't2.medium': '2_cpu_4gb'
    })
    return aws_node_to_nicknames


def _nickname_to_aws_nodes():
    aws_node_to_nickname = _aws_node_to_nickname()
    aws_nickname_to_node = {v: k for k, v in aws_node_to_nickname.items()}
    return aws_nickname_to_node


def _resolve_instance_type_nickname(ctx, _param, value):
    """
    Enables instance type shortcuts like:
    2_cpu_4gb for t2.large
    """
    nickname = value.lower()

    aws_nickname_to_node = _nickname_to_aws_nodes()

    # validate potential options for the node name
    possible_values = list(aws_nickname_to_node.keys()) + list(aws_nickname_to_node.values())
    if nickname not in possible_values:
        possible_options = '\n'.join(list(aws_nickname_to_node.keys()))
        click.BadParameter(f'{nickname} is not an available instance_type\n try one of these:\n{possible_options}')

    instance_type = nickname

    # if the value has _ then it's a nickname
    if '_' in nickname:
        instance_type = aws_nickname_to_node[nickname]
    return instance_type


def _get_instance_types(ctx, args, incomplete):
    # TODO: these should be retrieved from backend
    return list(_aws_node_to_nickname().keys())


def _parse_script_args(args):
    """Small state machine to parse the script name and script args __before__ the click parser is called."""
    flags = ['--', '--ignore_warnings']

    # states: 'parameter_name', 'parameter_value', 'flag', 'script_name', 'script_arg'
    state = None

    click_args = []
    script_name = None
    script_args = []

    for arg in args:
        arg = str(arg)
        if state in ['script_name', 'script_arg']:
            script_args.append(arg)
        else:
            if arg.startswith('--'):
                if arg in flags:
                    state = 'flag'
                else:
                    state = 'parameter_name'
            elif state == 'parameter_name':
                state = 'parameter_value'
            else:
                state = 'script_name'
                script_name = arg

            if state != 'script_name':
                click_args.append(arg)
    return click_args, script_name, script_args


def _encode_script_args(args):
    """Parse the script args and encode them as JSON. Prepend the JSON as a '--script_args_json' parameter."""
    args, file, script_args = _parse_script_args(args)
    if file is not None:
        args = ['--script_args_json'] + [f'{json.dumps(script_args)}'] + args + [file]
    return args


class _NestedCommand(click.Command):
    def parse_args(self, ctx, args):
        args = _encode_script_args(args)
        return super().parse_args(ctx, args)


@rich_click.command(
    cls=rich_click.deprecate_grid_options(_NestedCommand), context_settings=dict(ignore_unknown_options=True)
)
@click.option(
    '--config',
    'config',
    type=click.File('r'),
    required=False,
    callback=read_config_callback,
    help='Path to Grid config YML'
)
@click.option('--name', 'name', type=str, required=False, help='Name for this run', callback=_check_run_name_is_valid)
@click.option(
    '--description',
    'description',
    type=str,
    required=False,
    help='Run description; useful for note-keeping',
    callback=check_description_isnt_too_long
)
@click.option('--cluster', 'cluster', type=str, required=False)
@click.option(
    '--strategy',
    'strategy',
    type=click.Choice(['grid_search', 'random_search'], case_sensitive=False),
    required=False,
    help='Hyperparameter search strategy'
)
@click.option('--trials', 'trials', type=int, required=False, help='Number of trials to run hyper parameter search')
@click.option(
    '--instance_type',
    'instance_type',
    type=str,
    default='t2.medium',
    help='Instance type to start training session in',
    autocompletion=_get_instance_types,
    callback=_resolve_instance_type_nickname
)
@click.option('--gpus', 'gpus', type=int, required=False, default=0, help='Number of GPUs to allocate per experiment')
@click.option(
    '--cpus',
    'cpus',
    type=int,
    required=False,
    default=0,  # Default will be set to 1 after alerting user
    help='Number of CPUs to allocate per experiment'
)
@click.option('--memory', 'memory', type=str, required=False, help='How much memory an experiment needs')
@click.option(
    '--datastore_name', 'datastore_name', type=str, required=False, help='Datastore name to be mounted in training'
)
@click.option(
    '--datastore_version',
    'datastore_version',
    type=str,
    required=False,
    help='Datastore version to be mounted in training'
)
@click.option(
    '--datastore_mount_dir',
    'datastore_mount_dir',
    type=str,
    required=False,
    help='Directory to mount Datastore in training job'
)
@click.option(
    '--framework',
    'framework',
    type=click.Choice(['lightning', 'torch', 'tensorflow', 'julia', 'torchelastic'], case_sensitive=False),
    required=False,
    default='lightning',
    help='Framework to use in training'
)
@click.option(
    '--use_spot',
    'use_spot',
    is_flag=True,
    required=False,
    help='Use spot instance. The spot instances, or preemptive instance can be shut down at will'
)
@click.option(
    '--ignore_warnings',
    is_flag=True,
    required=False,
    help='If we should ignore warning when executing commands',
    callback=_check_ignore_warnings_flag
)
@click.option(
    '--script_args_json',
    type=str,
    required=False,
    hidden=True,
)
@click.option(
    '--scratch_size', type=int, required=False, help='The size in GB of the scratch space attached to the experiment'
)
@click.option(
    '--scratch_mount_path',
    type=str,
    required=False,
    help='The mount path to mount the scratch space',
    default='/tmp/scratch',
)
@click.option(
    '-l',
    '--localdir',
    is_flag=True,
    required=False,
)
@click.option('-d', '--dockerfile', type=str, required=False, help="Dockerfile for the image building")
@click.option(
    '--dependency_file',
    type=str,
    required=False,
    help="Dependency file path. If not provided and if either "
    "`requirements.txt` or `environment.yml` is present "
    "in the current-working-directory, that'll be used"
)
@rich_click.argument('script', type=Path, callback=_check_is_valid_extension, help='The name of the script to run.')
@rich_click.argument('script_args', nargs=-1, type=click.UNPROCESSED, help='Arguments to be passed to the script.')
@click.pass_context
def run(
    ctx, script: str, entrypoint: Path, config: Optional[Dict], name: Optional[str], cluster: Optional[str],
    strategy: Optional[str], trials: Optional[int], instance_type: str, gpus: Optional[int], description: Optional[str],
    ignore_warnings: bool, script_args_json: Optional[str], script_args: Optional[Any], memory: Optional[str],
    cpus: Optional[int], datastore_name: Optional[str], datastore_version: Optional[str],
    datastore_mount_dir: Optional[str], framework: Optional[str], use_spot: Optional[bool], scratch_size: Optional[int],
    scratch_mount_path: Optional[str], localdir: Optional[bool], dockerfile: Optional[str],
    dependency_file: Optional[str]
) -> None:
    """Runs scripts in remote infrastructure."""
    # Captures all other user arguments that are not
    # parsed automatically.
    script_arguments = list(script_args)
    if script_args_json is not None:
        script_arguments += json.loads(script_args_json)

    # Captures invocation command exactly as it was
    # typed in the terminal. pipe.quote maintains original
    # quotation used in the CLI. We'll replace absolute
    # grid executable path with the `grid` alias.
    sys.argv[0] = "grid"
    invocation_command = " ".join(map(shlex.quote, sys.argv))

    if env.DEBUG:
        click.echo(f"Script Arguments {script_arguments}")
        click.echo(f"Entrypoint Script: {entrypoint}")
        click.echo(f"Hyperparams Search Strategy: {strategy}")
        click.echo(f"GPUs Requested: {gpus}")
        click.echo(f"Spot Requested: {use_spot}")

    client = Grid()
    client.check_is_blocked()

    # make a fun random name when user does not pass in a name
    if name is None:
        name = unique_name()

    #  If the user has not passed a grid config file,
    #  then generate one with a set of default options.

    if not config:
        _grid_config = _generate_default_grid_config(
            cluster=cluster,
            grid_strategy=strategy,
            grid_trials=trials,
            instance_type=instance_type,
            gpus=gpus,
            memory=memory,
            cpus=cpus,
            datastore_name=datastore_name,
            datastore_version=datastore_version,
            datastore_mount_dir=datastore_mount_dir,
            framework=framework,
            use_spot=use_spot,
            scratch_size=scratch_size,
            scratch_mount_path=scratch_mount_path,
            localdir=localdir,
            dockerfile=dockerfile,
            dependency_file=dependency_file
        )

    else:
        _grid_config = config
        # if config file is passed but overwriting `localdir`
        if not _grid_config.get('compute'):
            raise click.BadParameter("Invalid config: missing `compute` key.")
        if not _grid_config['compute'].get('train'):
            raise click.BadParameter("Invalid config: missing `train` key.")

        if _grid_config['compute']['train'].get('localdir') is None:
            _grid_config['compute']['train']['localdir'] = localdir
        if _grid_config['compute']['train'].get('dockerfile') is None:
            _grid_config['compute']['train']['dockerfile'] = dockerfile

    validate_config(cfg=_grid_config)
    validate_and_configure_datastore(grid_config=_grid_config)

    # Warn user if they have not specified a cpu or gpu number so cpus will be set to 1
    cpus = _grid_config['compute']['train'].get('cpus')
    gpus = _grid_config['compute']['train'].get('gpus')
    if not cpus and not gpus:
        _grid_config['compute']['train']['cpus'] = 1

    #  Send to client.
    client.train(
        config=_grid_config,
        kind=WorkflowType.SCRIPT,
        run_name=name,
        run_description=description,
        entrypoint=entrypoint,
        script_args=script_arguments,
        invocation_command=invocation_command,
        localdir=localdir,
        dependency_file=dependency_file,
    )
