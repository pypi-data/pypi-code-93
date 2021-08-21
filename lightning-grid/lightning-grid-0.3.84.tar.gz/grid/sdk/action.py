import base64
from collections import OrderedDict
from inspect import signature
from pathlib import Path
import shlex
from typing import Any, Dict, List, Optional, Union
import warnings
import webbrowser

import yaml

import grid.cli.globals as env
import grid.sdk._gql.queries
from grid.sdk._gql.queries import check_github_repo_accessible, repository_presigned_url, start_run_mutation
from grid.sdk.datastore import list_all_available_datastores
from grid.sdk.source_code.dependency_manager import check_dependency_listing, find_package_manager
from grid.sdk.source_code.git import (
    _check_if_remote_head_is_different,
    _check_if_uncommited_files,
    add_git_root_path,
    check_github_repository,
    execute_git_command,
)
from grid.sdk.source_code.repository import LocalRepository
from grid.sdk.utils.name_generator import unique_name
from grid.sdk.utils.navigation import set_directory


def _check_run_name_is_valid(value: str):
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
            raise ValueError(
                f"Invalid Run name: {value} the Run name must be lower case "
                "alphanumeric characters or '-', start with an alphabetic "
                "character, and end with an alphanumeric character (e.g. 'my-name', "
                " or 'abc-123')."
            )

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
    dependency_file: Optional[str] = None
):
    """
    Generates a new default config file for user if user hasn't
    submitted one.
    """

    provider = {
        'vendor': "aws",
        'credentials': "n/a",
        'region': "us-east-1",
    }
    if cluster is not None:
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
                'disk_size': 200,
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
            dependency_file = add_git_root_path(dependency_file)

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

    return _grid_config


def _verify_entrypoint_script_is_valid(p: Path):
    """Verify if the entrypoint script is a file extension that grid can actually execute.
    """
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Entrypoint script file {p} does not exist.")

    if p.suffix not in ['.py', '.sh', '.jl']:
        raise ValueError(
            f'We only support Python (.py), shell (.sh), or Julia (.jl) scripts. Got: {p}.'
            f'Email support@grid.ai if you want to request support for this file type.'
        )


def _aws_node_to_nickname():
    aws_node_to_nicknames = OrderedDict({
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


def _resolve_instance_type_nickname(value):
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
        ValueError(f'{nickname} is not an available instance_type\n try one of these:\n{possible_options}')

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


def read_config(path: Union[str, Path]) -> dict:
    """
    Parameters
    ----------
    path:
        path to file on disk
    """
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'grid config file {path} does not exist')

    #  Loads the YML file as passed by the user.
    try:
        with open(path) as f:
            grid_config = yaml.safe_load(f.read())
        if not isinstance(grid_config, dict):
            raise Exception("Unexpected file structure")
    except Exception as e:
        raise ValueError(f'Could not load your YAML config file: {e}')

    #  Adds required structure to the base YML file, if that structure isn't there.
    if 'compute' not in grid_config:
        grid_config['compute'] = {}
    if 'train' not in grid_config['compute']:
        grid_config['compute']['train'] = {}
    return grid_config


def check_description_isnt_too_long(value: str):
    """Click callback that checks if the description isn't too long."""
    if value is not None and len(value) > 200:
        raise ValueError('Description should have at most ' f'200 characters, yours has {len(value)}.')
    return value


def validate_and_configure_datastore(grid_config: dict):
    """
    Validate the existence of provided datastore and user's access. Inject datastore id to the
    config, based on the name and version provided. If version is not provided, this function also
    injects the maximum version to the config
    """
    try:
        datastore_name = grid_config["compute"]["train"]["datastore_name"]
        datastore_version = grid_config["compute"]["train"]["datastore_version"]
        if isinstance(datastore_version, int):
            datastore_version = str(datastore_version)
    except:
        return

    if not datastore_name:
        return

    split = datastore_name.split(":")
    if len(split) > 2:
        raise ValueError(f"Error while parsing {datastore_name}. Use the format <username>:<datastore-name>")
    elif len(split) == 2:
        datastore_name = split[1]
        datastores = list_all_available_datastores(include_teams=True)
    else:
        datastores = list_all_available_datastores()

    usable_version = -1
    datastore_id = None
    for ds in sorted(datastores, key=lambda x: x.version):
        if datastore_name == ds.name and ds.snapshot_status == "succeeded":
            current_version = int(ds.version)
            if datastore_version and datastore_version == str(current_version):
                datastore_id = ds.datastore_id
                usable_version = datastore_version
                break
            usable_version = max(usable_version, current_version)
            datastore_id = ds.datastore_id

    if not datastore_id:
        raise ValueError(f'No ready-to-use datastore found with name {datastore_name} and version {datastore_version}')

    if datastore_version and datastore_version != str(usable_version):
        raise ValueError(f"Unable to list datastores with name {datastore_name} and version {datastore_version}")

    if not datastore_version:
        warnings.warn(
            f'No --grid_datastore_version passed for datastore: {datastore_name}. '
            f'Using version: {usable_version}'
        )

    # inject valid details back to config
    grid_config["compute"]["train"]["datastore_id"] = datastore_id
    grid_config["compute"]["train"]["datastore_name"] = datastore_name
    grid_config["compute"]["train"]["datastore_version"] = str(usable_version)

    return grid_config


def start_run(
    entrypoint: Path,
    script_args: str = '',
    strategy: str = 'grid_search',
    trials: int = None,
    framework: str = 'lightning',
    dependency_file: Optional[str] = None,
    instance_type: str = 't2.medium',
    use_spot: bool = False,
    cpus: int = 0,
    gpus: int = 0,
    memory: Optional[str] = None,
    datastore_name: Optional[str] = None,
    datastore_version: Optional[str] = None,
    datastore_mount_dir: Optional[str] = None,
    scratch_size: Optional[int] = None,
    scratch_mount_path: str = '/tmp/scratch',
    name: Optional[str] = None,
    description: Optional[str] = None,
    cluster: Optional[str] = None,
    localdir: bool = False,
    dockerfile: Optional[str] = None,
    config: Optional[Union[str, Path]] = None
) -> str:
    """Runs scripts in remote infrastructure.

    Returns
    -------
    str
        run name which was started
    """

    _invocation_args = {}
    sig = signature(start_run)
    for p_name, param in sig.parameters.items():
        if p_name == ['entrypoint', 'script_args']:
            continue
        if locals()[p_name] != param.default:
            _invocation_args[p_name] = locals()[p_name]

    if config is not None:
        #  Adds required structure to the base YML file, if that structure isn't there.
        config = read_config(config)
    else:
        config = {}

    if name is not None:
        name = _check_run_name_is_valid(name)
    else:
        name = unique_name()

    if strategy not in ['grid_search', 'random_search']:
        raise ValueError(f"strategy {strategy} is not valid.")

    check_description_isnt_too_long(description)
    instance_type = _resolve_instance_type_nickname(instance_type)

    if framework not in ['lightning', 'torch', 'tensorflow', 'julia', 'torchelastic']:
        raise ValueError(framework)

    _verify_entrypoint_script_is_valid(Path(entrypoint))
    script_arguments = shlex.split(script_args)

    shlex_g_args = ' '.join([shlex.quote(f'--{k}') + ' ' + shlex.quote(f'{v}') for k, v in _invocation_args.items()])
    shlex_entrypoint = shlex.quote(f'{entrypoint}')
    shlex_script_args = ' '.join([shlex.quote(x) for x in shlex.split(script_args)])
    invocation_command = shlex.quote(f'grid run {shlex_g_args} {shlex_entrypoint} {shlex_script_args}')

    # make a fun random name when user does not pass in a name
    name = unique_name() if name is None else name

    #  If the user has not passed a grid config file, then generate one with a set
    #  of default options. We'll add a default instance and the user's default credentials.
    if not config:
        _grid_config = _generate_default_grid_config(
            instance_type=instance_type,
            cluster=cluster,
            use_spot=use_spot,
            grid_strategy=strategy,
            grid_trials=trials,
            gpus=gpus,
            memory=memory,
            cpus=cpus,
            datastore_name=datastore_name,
            datastore_version=datastore_version,
            datastore_mount_dir=datastore_mount_dir,
            framework=framework,
            localdir=localdir,
            dockerfile=dockerfile,
            scratch_size=scratch_size,
            scratch_mount_path=scratch_mount_path,
            dependency_file=dependency_file
        )

    else:
        _grid_config = config
        _grid_config['compute'].setdefault('train', {})
        _grid_config['compute']['train'].setdefault('localdir', localdir)
        _grid_config['compute']['train'].setdefault('dockerfile', dockerfile)

    validate_and_configure_datastore(grid_config=_grid_config)

    # Warn user if they have not specified a cpu or gpu number so cpus will be set to 1
    cpus = _grid_config['compute']['train'].get('cpus')
    gpus = _grid_config['compute']['train'].get('gpus')
    if not cpus and not gpus:
        _grid_config['compute']['train']['cpus'] = 1

    #  Send to client.
    return train(
        config=_grid_config,
        run_name=name,
        run_description=description,
        entrypoint=entrypoint,
        script_args=script_arguments,
        invocation_command=invocation_command,
        localdir=localdir,
        dependency_file=dependency_file,
    )


def train(
    config: Dict[str, Any],
    run_name: str,
    run_description: str,
    entrypoint: Path,
    script_args: List[str],
    invocation_command: str,
    localdir: bool = False,
    dependency_file=None
) -> str:
    """
    Submits a Run to backend from a local script.

    Parameters
    ----------
    config: dict
        YAML config
    run_name: str
        Run name
    run_description: str
        Run description.
    entrypoint: str
        Entrypoint script.
    script_args: List[str]
        Script arguments passed from command line.
    invocation_command: str
    localdir: bool
        If True, trigger the local directory run workflow
    dependency_file: str
        Dependency file path. Defaults to None
    """
    #  Base64-encode the config object either passed
    #  or constructed.
    config_encoded = base64.b64encode(yaml.dump(config).encode('ascii')).decode('ascii')
    env.logger.debug(config_encoded)

    # we will be using `github_repository` and `commit_sha` as a repository ID
    # and checksum version temporarily; this will change when we call `createRun`
    # directly

    if localdir:
        # Checking dependencies and suggesting when needed
        repository_path = Path(entrypoint).parent.absolute()
        with set_directory(repository_path):
            check_dependency_listing(repo_root=repository_path, dependency_file=dependency_file)

            _entrypoint = entrypoint

            # get path from entrypoint
            repository = LocalRepository(path=repository_path)

            cluster_id = config["compute"]["provider"].get("cluster")
            presigned_url = repository_presigned_url(package_name=f"{repository.version}.tar.gz", cluster_id=cluster_id)
            # hack to avoid collision between spinner and rich progress
            repository.upload(url=presigned_url)
            github_repository = repository_path
            commit_sha = repository.version

    # only apply git checks in case this is a git run
    else:
        any_repo_path = Path(entrypoint).parent
        with set_directory(any_repo_path):
            # Checking dependencies and suggesting when needed
            check_dependency_listing(repo_root=any_repo_path, dependency_file=dependency_file)

            grid.sdk._gql.queries._check_user_github_token()

            check_github_repository()

            # Check if repository contains uncommitted files.
            _check_if_uncommited_files()

            # Check if remote is in sync with local.
            _check_if_remote_head_is_different()

            #  Get commit SHA
            commit_sha = execute_git_command(['rev-parse', 'HEAD'])

            #  Get repo name
            github_repository = execute_git_command(["config", "--get", "remote.origin.url"])

            #  Clean up the repo name
            github_repository = github_repository.replace('git@github.com:', 'github.com/')
            github_repository = github_repository.replace('.git', '')

            #  Add the root path to the entrypoint script.
            _entrypoint = add_git_root_path(entrypoint)
            _entrypoint = Path(entrypoint).relative_to(any_repo_path)

            if not check_github_repo_accessible(github_repository):
                settings_url = env.GRID_URL.replace("graphql", "") + "#/settings?tabId=integrations"
                webbrowser.open(settings_url, new=2, autoraise=True)
                raise PermissionError(
                    f'Grid cannot access {github_repository}. Please grant access on the settings page: {settings_url}'
                )

    start_run_mutation(
        script_args=script_args,
        entrypoint=str(_entrypoint),
        config_encoded=config_encoded,
        run_name=run_name,
        run_description=run_description,
        commit_sha=commit_sha,
        github_repository=github_repository,
        invocation_command=invocation_command
    )

    return run_name
