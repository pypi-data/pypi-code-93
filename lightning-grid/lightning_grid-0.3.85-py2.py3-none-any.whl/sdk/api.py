import os
from pathlib import Path
from typing import Iterable, List, Optional, Union

from grid.openapi import Externalv1Cluster, V1InstanceType
from grid.openapi.api import cluster_service_api
from grid.sdk._gql.queries import experiment_id_from_name, get_grid_user_id, get_runs_lookup_data
from grid.sdk.action import start_run
from grid.sdk.auth import Credentials
from grid.sdk.client import create_swagger_client
from grid.sdk.client.grid_gql import gql_client
from grid.sdk.datastore import Datastore, list_all_available_datastores
from grid.sdk.experiments import Experiment, ExperimentName
from grid.sdk.runs import Run

__all__ = [
    'login', "create_run", "list_runs", "get_run", "cancel_run", "get_experiment_by_name", "get_experiment_by_id",
    "get_build_logs", "get_experiment_logs", "cancel_experiment", "Run", "Datastore", "list_datastores",
    "get_instance_types", "list_clusters"
]


def login(
    username: Optional[str] = None,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None,
    *,
    _url="https://platform.grid.ai"  # noqa - For testing purposes only. not user facing.
):
    """Log in with your grid.ai credentials for usage of the SDK in the running process.

    All parameters are optional. Calling ``login()`` without parameters will check if
    the ``GRID_USER_ID`` and ``GRID_API_KEY`` env vars have been set (using those if
    available), otherwise it will check for the file ``credentials.json`` in the
    machines ``$HOME/.grid`` directory (if it exists).

    If no credentials have been stored, then you must pass in your API key and either
    your username or user id (if you know it). Your user id and API key can be found
    by navigating to *** INSERT INSTRUCTIONS TO FIND KEY HERE ***.

    Parameters
    ----------
    username
        your grid username. This is either be your github username or email address,
        depending on what you use when signing into the grid platform at:
        https://platform.grid.ai

    user_id
        Your grid user id. This can be found by ** INSERT INSTRUCTIONS HERE **
    api_key
        Your grid API key. This can be found by ** INSERT INSTRUCTIONS HERE **
    """
    if user_id and api_key:
        creds = Credentials(user_id=user_id, api_key=api_key)
    elif username and api_key:
        creds = Credentials(user_id=username, api_key=api_key)
        client = gql_client(url=_url + "/graphql", creds=creds)
        user_id = get_grid_user_id(client=client)
        creds = Credentials(user_id=user_id, api_key=api_key)
    elif (username or user_id) or api_key:
        raise ValueError("Either (`user_id` OR `username`) AND `api_key` need to be set, or none set.")
    else:
        creds = Credentials.from_locale()

    os.environ['GRID_USER_ID'] = creds.user_id
    os.environ['GRID_API_KEY'] = creds.api_key
    os.environ['GRID_URL'] = _url
    creds = Credentials.from_locale()
    # warmup cache. can take ~2 sec on first call
    _ = gql_client(url=_url + '/graphql', creds=creds)


def create_run(
    entrypoint: Path,
    script_args: str = '',
    strategy: str = 'grid_search',
    trials: int = None,  # if strategy == random
    framework: str = 'lightning',
    dependency_file: Optional[str] = None,
    instance_type: str = 't2.medium',
    use_spot: bool = False,
    cpus: int = 0,  # if < 1 use max on instance
    gpus: int = 0,  # if < 1 and gpus are on machine, use max on machine.
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
) -> 'Run':
    """Create a run from some configuration

    Parameters
    ----------
    entrypoint: Path,
    script_args: str = '',
    strategy: str = 'grid_search',
    trials: int = None,  # if strategy == random
    framework: str = 'lightning',
    dependency_file: Optional[str] = None,
    instance_type: str = 't2.medium',
    use_spot: bool = False,
    cpus: int = 0,  # if < 1 use max on instance
    gpus: int = 0,  # if < 1 and gpus are on machine, use max on machine.
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

    Returns
    -------
    Run
        the run object which was started
    """
    run_name = start_run(
        entrypoint=entrypoint,
        script_args=script_args,
        strategy=strategy,
        trials=trials,
        framework=framework,
        dependency_file=dependency_file,
        instance_type=instance_type,
        use_spot=use_spot,
        cpus=cpus,
        gpus=gpus,
        memory=memory,
        datastore_name=datastore_name,
        datastore_version=datastore_version,
        datastore_mount_dir=datastore_mount_dir,
        scratch_size=scratch_size,
        scratch_mount_path=scratch_mount_path,
        name=name,
        description=description,
        cluster=cluster,
        localdir=localdir,
        dockerfile=dockerfile,
        config=config
    )
    return get_run(run_name)


def list_runs() -> List[str]:
    """Find the name of every run which you have access to.

    Returns
    -------
    List[str]
        all run names.
    """
    name_ids = get_runs_lookup_data()
    return [d['name'] for d in name_ids]


def get_run(name: str) -> Run:
    """Retrive a Run object by providing its name.

    Parameters
    ----------
    name
        the name of the run you want to retrive.

    Returns
    -------
    Run
        an object whose properties and methods allow you to iterate over
        experiments, ask for build logs, experiment statuses in bulk, , logs, and
        statuses, as well as perform certain administrative operations such
        as canceling runs.

    TODO
    ----
    * Allow users on a team to call ``get_run()`` with a string in the
      format of  ``username:run_name`` to retrieve their teammates' run.
    """
    return Run(name=name)


def cancel_run(name: str) -> List[str]:
    """Cancel all PENDING or RUNNING experiments within a run

    Parameters
    ----------
    name
        name of the run to cancel.

    Returns
    -------
    List[str]
        name of the experiments which have either been cancelled in the
        run or which which have previously reached a terminal state:
        "SUCCEEDED", "FAILED", or "CANCELLED".
    """
    return get_run(name).cancel()


def get_experiment_by_name(name: str) -> Experiment:
    """Retrive an experiment object by providing it's name.

    Parameters
    ----------
    name
        the name of the experiment you want to retrive.

        If you are part of a GridAI Teams account, you can retrieve
        one of your teammates experiments by providing the name in
        the following format: ``username:experiment_name``

    Returns
    -------
    Experiment
        an object whose properties and methods allow you natively ask Grid
        to retrieve up to date information, artifacts metrics, logs, and
        statuses, as well as perform certain administrative operations such
        as canceling a running experiment.
    """
    name = ExperimentName.from_external_format(name)
    exp_id = experiment_id_from_name(name)
    return Experiment._init_via_gql_query(exp_id=exp_id)


def get_experiment_by_id(exp_id: str) -> Experiment:
    """Retrive an experiment object by providing it's unique id.

    The id of an experiment is generated by Grid when the experiment is created.
    It can be found throughout the Experiment and Run objects by querying an
    experiment objects ``.id`` property.

    Parameters
    ----------
    exp_id
        the id of the experiment you want to retrive.

        If you are part of a GridAI Teams account, no change is needed in
        the formatting of the input to retrieve one of your teammates
        experiments. Just passing the id will perform a unique lookup for
        you.

    Returns
    -------
    Experiment
        an object whose properties and methods allow you natively ask Grid
        to retrieve up to date information, artifacts metrics, logs, and
        statuses, as well as perform certain administrative operations such
        as canceling a running experiment.
    """
    return Experiment._init_via_gql_query(exp_id=exp_id)


def get_build_logs(run_name: Optional[str] = None, exp_name: Optional[str] = None) -> Iterable[str]:
    """Output a run or experiment's build logs.

    If the build is currently executing, looping over the iterator will yield
    logs lines for as long as the build continues. If the build is finished,
    then all log lines are available to be iterated over immediatly and no
    wait period is required.

    TODO(rlizzo): how does Teams work here?
                  can you use ``username:experiment_name`` to get build logs?

    Parameters
    ----------
    run_name
        name of a run to retrieve the build logs for.
    exp_name
        name of an experiment to retrieve the build logs for.

    Yields
    -------
    Iterable[str]
        Iterator where each element is a single line of the build log output.
        The first element return is the first line in the build log.

    TODO
    ----
    * Allow users on a team to call ``get_build_logs()`` with a string in
      the format of  ``username:run_name`` to retrieve their teammates' logs.
    """
    if (run_name and exp_name) or (not run_name and not exp_name):
        raise ValueError(
            "One - and only one - of args `run_name`/`exp_name` must be provided.\n"
            f"Recieved run_name={run_name} and exp_name={exp_name}"
        )
    if run_name:
        return get_run(run_name).build_logs()
    else:
        return get_experiment_by_name(exp_name).build_logs()


def get_experiment_logs(name: str) -> List[str]:
    """
    If the experiment is currently executing, looping over the iterator
    will yield logs lines for as long as the experiment continues. If
    the experiment is finished, then all log lines are available to be
    iterated over immediatly and no wait period is required.

    Parameters
    ----------
    name
        name of an experiment to retrieve the logs for.

    Yields
    -------
    Iterable[str]
        Iterator where each element is a single line of the experiment
        stdout log output. The first element return is the first line
        in the build log.

    TODO
    ----
    * Allow users on a team to call ``get_experiment_logs()`` with a string in
      the format of  ``username:experiment_name`` to retrieve their teammates' logs.
    """
    return get_experiment_by_name(name).logs()


def cancel_experiment(name: str) -> str:
    """Cancel a PENDING or RUNNING experiment.

    Parameters
    ----------
    name
        name of the experiment to cancel.

    Returns
    -------
    str
        name of the experiment which has been cancelled.
    """
    return get_experiment_by_name(name).cancel()


def get_instance_types(cluster_id: str) -> List[V1InstanceType]:
    """
    Get the instance types for the given cluster
    """
    api_client = create_swagger_client()
    cluster_api = cluster_service_api.ClusterServiceApi(api_client)
    resp = cluster_api.cluster_service_list_cluster_instance_types(id=cluster_id)
    return resp.instance_types


def list_clusters() -> List[Externalv1Cluster]:
    """
    List the clusters for the user
    """
    api_client = create_swagger_client()
    cluster_api = cluster_service_api.ClusterServiceApi(api_client)
    resp = cluster_api.cluster_service_list_clusters()
    return resp.clusters


def list_datastores(include_teams: bool = False) -> List[Datastore]:
    """List datastores for user / teams

    Parameters
    ----------
    include_teams:
        if True, returns a list of datastores of the everyone in the team
    """
    return list_all_available_datastores(include_teams=include_teams)
