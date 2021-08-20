import ast
from typing import Iterable, List, Optional, Sequence, TYPE_CHECKING, Union
from urllib.error import HTTPError
import webbrowser

from cytoolz import update_in
import rich.pretty

from grid.cli import globals as env
from grid.metadata import __version__
from grid.sdk.client import create_gql_client
from grid.sdk.client.grid_gql import gql_execute, gql_subscribe

if TYPE_CHECKING:
    from grid.sdk.experiments import ExperimentName

# TODO(rlizzo): standardize callers so that these all take ``Client`` instances.


def get_grid_user_id(client) -> str:
    query = """
    query Login ($cliVersion: String!) {
        cliLogin (cliVersion: $cliVersion) {
            userId
            success
            message
        }
    }
    """
    res = gql_execute(client, query, cliVersion=__version__)['cliLogin']
    return res['userId']


def get_user_basic_info():
    client = create_gql_client()
    query = """
    query {
        getUser {
            userId
            isVerified
            completedSignup
            isBlocked
            username
            firstName
            lastName
            email
        }
    }
    """
    return gql_execute(client, query)['getUser']


def get_experiment_details_gql(experiment_id: str):
    client = create_gql_client()
    query = """
    query ($experimentId: ID!) {
        getExperimentDetails (experimentId: $experimentId) {
            name
            experimentId
            githubId
            commitSha
            status
            desiredState
            createdAt
            startedRunningAt
            finishedAt
            invocationCommands
            parameters {
                name
                value
            }
            userDetails {
                username
                id
                firstName
                lastName
            }
        }
    }
    """
    resp = gql_execute(client, query, experimentId=experiment_id)
    res = resp['getExperimentDetails']
    _r1 = update_in(res, ['status'], str.upper)
    return update_in(_r1, ['desiredState'], str.upper)


def get_experiment_status_gql(experiment_id: str):
    client = create_gql_client()
    query = """
    query ($experimentId: ID!) {
        getExperimentDetails (experimentId: $experimentId) {
            status
            desiredState
            createdAt
            startedRunningAt
            finishedAt
        }
    }
    """
    res = gql_execute(client, query, experimentId=experiment_id)['getExperimentDetails']
    _r1 = update_in(res, ['status'], str.upper)
    return update_in(_r1, ['desiredState'], str.upper)


def cancel_experiment(exp_id: str) -> None:
    client = create_gql_client()
    query = """
        mutation ($experimentId: ID!) {
                cancelExperiment(experimentId: $experimentId) {
                    success
                    message
                }
            }
        """
    params = {'experimentId': exp_id}
    result = gql_execute(client, query, **params)['cancelExperiment']
    if result['success'] is not True:
        raise RuntimeError(result['message'])


def experiment_id_from_name(name: 'ExperimentName') -> str:
    """Retrieves experiment ID from an experiment name.

    Parameters
    ----------
    name
        experiment name struct which has been generated from
        parsing user code.

    Returns
    -------
    str
        The experiment ID to be used.
    """
    client = create_gql_client()
    query = """
    query ($experimentName: String!, $username: String) {
        getExperimentId(experimentName: $experimentName, username: $username) {
            success
            message
            experimentId
        }
    }
    """
    params = {"experimentName": name.name, "username": name.username}
    result = gql_execute(client, query, **params)
    if not result["getExperimentId"]["success"]:
        if "Cannot find experiment" in result["getExperimentId"]["message"]:
            raise KeyError(
                f"Experiment {name} does not exist\n "
                "If you wish to fetch an experiment for somebody in "
                "your team, use <username>:<experiment-name> format."
            )
        raise ValueError(f"{result['getExperimentId']['message']}")
    return result["getExperimentId"]["experimentId"]


def get_runs(run_name: Optional[str] = '', team_id: Optional[str] = None) -> Sequence[dict]:
    """Get the config for runs and shallow description of all contained experiments

    TODO(rlizzo):
        evaluate if all return fields of `experiment` in GQL query below
        are actually required. Simplify if possible

    Parameters
    ----------
    client
        gql client instance
    run_name
        Optional parameter to filter run config return to a specific run name.
        If not set, then all runs for the client's authenticated user are
        returned (optionally filtered by team if `team_id` filter param is set.
    team_id
        Optional parameter to filter run config results on the intersection
        of both the client's authenticated user AND a team ID.

    Returns
    -------
    Sequence[dict]
        An unstructured mapping of run config, directly maps to the query
        string which is contained in the implementation of this function.
    """
    client = create_gql_client()
    params = {'runName': run_name, "teamId": team_id}

    query = """
        query (
            $runName: ID, $teamId: ID
        ) {
            getRuns (runName: $runName, teamId: $teamId) {
                name
                runId
                projectId
                clusterId
                createdAt
                description
                entrypoint
                estimatedHourlyCost
                userDetails {
                    username
                    id
                    firstName
                    lastName
                }
                scriptCommand
                config {
                    compute
                    hyperParams
                }
                nExperiments
                experiments {
                    name
                    experimentId
                    commitSha
                    status
                    desiredState
                    createdAt
                    startedRunningAt
                    finishedAt
                    invocationCommands
                    parameters {
                        name
                        value
                    }
                }
            }
        }
        """
    result = gql_execute(client, query, **params)['getRuns']
    return result


def get_runs_lookup_data(run_name: Optional[str] = '', team_id: Optional[str] = None) -> Sequence[dict]:
    """Find run names (and associated id) for authenticated user.

    Parameters
    ----------
    client
        gql client instance
    run_name
        Optional parameter to filter run config return to a specific run name.
        If not set, then all runs for the client's authenticated user are
        returned (optionally filtered by team if `team_id` filter param is set.
    team_id
        Optional parameter to filter run config results on the intersection
        of both the client's authenticated user AND a team ID.

    Returns
    -------
    Sequence[dict]
        An unstructured mapping of run config, directly maps to the query
        string which is contained in the implementation of this function.
    """
    client = create_gql_client()
    query = """
        query (
            $runName: ID, $teamId: ID
        ) {
            getRuns (runName: $runName, teamId: $teamId) {
                name
                runId
            }
        }
        """
    params = {'runName': run_name, "teamId": team_id}
    result = gql_execute(client, query, **params)['getRuns']
    return result


def cancel_run(run_name: str) -> None:
    client = create_gql_client()
    query = """
        mutation ($name: ID!) {
            cancelRun(name: $name) {
                success
                message
            }
        }
        """
    result = gql_execute(client, query, name=run_name)['cancelRun']
    if result['success'] is not True:
        raise RuntimeError(result['message'])


def experiment_archived_build_logs(exp_id: str) -> Iterable[dict]:
    """Retrievies build logs from the archive.

    Yields
    ------
    Dict[str, str]
        Log lines
    """
    client = create_gql_client()
    query = """
    query ($experimentId: ID!) {
        getBuildLogs(experimentId: $experimentId) {
            message
            timestamp
        }
    }
    """
    params = {'experimentId': exp_id}
    result = gql_execute(client, query, **params)
    # The backend will return end empty object if no pages of logs are available.
    if not result.get('getBuildLogs'):
        raise StopIteration
    for log in result['getBuildLogs']:
        yield log


def experiment_live_build_logs(exp_id: str, limit: Union[int, None]) -> Iterable[dict]:
    """Streams build logs from subscription API.

    Parameters
    ----------
    exp_id
        experiment id which build logs should be retrieved for.
    limit
        if integer, terminate the subscription after N number of lines
        have been written to the client. If None, then this subscription
        never terminates.

    Yields
    ------
    Union[str, str]
        Log lines
    """
    client = create_gql_client(websocket=True)
    query = """
    subscription ($experimentId: ID!, $tailLines:Int) {
        getLiveBuildLogs(
            experimentId: $experimentId,
            tailLines: $tailLines) {
                message
                timestamp
        }
    }
    """
    params = {"experimentId": exp_id, "tailLines": limit}
    for msg in gql_subscribe(client, query, variable_values=params).get("getLiveBuildLogs"):
        yield msg['tailLines']


def experiment_archived_logs(exp_id: str) -> Iterable[dict]:
    client = create_gql_client()
    query = """
    query GetLogs ($experimentId: ID!) {
        getArchiveExperimentLogs(experimentId: $experimentId) {
            lines {
                message
                timestamp
            }
        }
    }
    """
    params = {'experimentId': exp_id}
    result = gql_execute(client, query, **params)

    # The backend will return end empty object if no pages of logs are available.
    if not result.get('getArchiveExperimentLogs'):
        raise StopIteration
    for log in result['getArchiveExperimentLogs']['lines']:
        yield log


def experiment_live_logs(exp_id: str, n_lines: int) -> Iterable[dict]:
    # If the experiment isn't in a finished state, then do a subscription with live logs.
    client = create_gql_client(websocket=True)
    query = """
    subscription GetLogs ($experimentId: ID!, $nLines: Int!) {
        getLiveExperimentLogs(
            experimentId: $experimentId, nLines: $nLines) {
                message
                timestamp
        }
    }
    """
    params = {'experimentId': exp_id, 'nLines': n_lines}
    stream = gql_subscribe(client, query, variable_values=params)
    for log in stream:
        yield log['getLiveExperimentLogs']


def _check_user_github_token() -> bool:
    """Checks if user has a valid Github token available.

    If user doesn't have one, then redirect user to the Grid UI to fetch a new one.

    Returns
    -------
    has_token: bool
        Boolean indicating if user has valid token.
    """
    # Build query
    client = create_gql_client()
    query = """
        query CheckToken {
            checkUserGithubToken {
                hasValidToken
            }
        }
    """

    # Check if the user has a token. If she hasn't, then redirect
    # user to the /auth page to get a new Github token.
    try:
        result = gql_execute(client, query)
        has_token = result['checkUserGithubToken']['hasValidToken']
        if not has_token:
            auth_url = env.GRID_URL.replace("graphql", "auth")
            webbrowser.open(auth_url, new=2, autoraise=True)
            raise PermissionError(
                "Authentication tokens need to be renewed! Opening Grid "
                "on the browser so we can renew your authentication tokens."
            )
    except HTTPError as e:
        raise PermissionError(e)

    return has_token


def repository_presigned_url(package_name: str, cluster_id: Optional[str] = None):
    """Pre-signed URL for uploading repository package to S3
    """
    client = create_gql_client()
    query = """
    query ($path: String!, $clusterId: ID) {
        getLocalDirPresignedUrl(path: $path, clusterId: $clusterId) {
            presignedUrl
        }
    }
    """
    params = {"path": package_name, "clusterId": cluster_id}
    result = gql_execute(client, query, **params)
    return result["getLocalDirPresignedUrl"]["presignedUrl"]


def check_github_repo_accessible(github_repository: str) -> bool:
    """
    Checks if user has authoirized Grid to access a given Github repository.
    If the user did not, then redirect them to the
    Grid UI settings page to authorize.

    Parameters
    ----------
    github_repository: str
        Github repository URL or ID

    Returns
    -------
    is_accessible: bool
        Boolean indicating if the user authorized to access the Github repository,
    """
    client = create_gql_client()
    query = """
        query ($repositoryUrl: ID!) {
            isGithubRepositoryAccessible(repositoryUrl: $repositoryUrl) {
                isAccessible
            }
        }
    """
    result = gql_execute(client, query, repositoryUrl=github_repository)
    return result['isGithubRepositoryAccessible']['isAccessible']


def start_run_mutation(
    script_args, entrypoint, config_encoded, run_name, run_description, commit_sha, github_repository,
    invocation_command
):
    # Build GraphQL query
    client = create_gql_client()
    mutation = """
    mutation (
        $configString: String!
        $name: String!
        $description: String
        $commitSha: String
        $githubRepository: ID!
        $commandLineArgs: [String]!
        $invocationCommand: String!
        ) {
        trainScript (
            properties: {
                    githubRepository: $githubRepository
                    name: $name
                    description: $description
                    configString: $configString
                    commitSha: $commitSha
                    commandLineArgs: $commandLineArgs
                    invocationCommand: $invocationCommand
                }
        ) {
        success
        message
        name
        runId
        }
    }
    """

    #  Prepend the file name to the list of args and builds the query payload.
    script_args.insert(0, str(entrypoint))
    params = {
        'configString': config_encoded,
        'name': run_name,
        'description': run_description,
        'commitSha': commit_sha,
        'githubRepository': str(github_repository),
        'commandLineArgs': script_args,
        'invocationCommand': invocation_command
    }

    #  Send request to Grid.
    try:
        result = gql_execute(client, mutation, **params)
    except Exception as e:
        rich.pretty.pprint(e)
        message = ast.literal_eval(str(e))['message']
        CREDIT_CARD_ERROR_MESSAGE = "A credit card on file is needed in order to use a GPU"
        if CREDIT_CARD_ERROR_MESSAGE in message:
            PermissionError(message)
        raise


def estimate_run_cost_mutation(script_args, entrypoint, config_encoded):
    # Build GraphQL query
    client = create_gql_client()
    mutation = """
    mutation (
        $configString: String!
        $commandLineArgs: [String]!
        ) {
        estimateTrainScript (
            properties: {
                    configString: $configString
                    commandLineArgs: $commandLineArgs
                }
        ) {
        success
        message
        nExperiments
        estimatedHourlyCost
        }
    }
    """

    #  Prepend the file name to the list of args and builds the query payload.
    script_args.insert(0, str(entrypoint))
    params = {
        'configString': config_encoded,
        'commandLineArgs': script_args,
    }

    #  Send request to Grid.
    try:
        result = gql_execute(client, mutation, **params)
    except Exception as e:
        message = ast.literal_eval(str(e))['message']
        CREDIT_CARD_ERROR_MESSAGE = "A credit card on file is needed in order to use a GPU"
        if CREDIT_CARD_ERROR_MESSAGE in message:
            PermissionError(message)
        raise

    return result['estimateTrainScript']


def get_user_teams() -> List[dict]:
    client = create_gql_client()
    query = """
        query GetUserTeams {
            getUserTeams {
                success
                message
                teams {
                    id
                    name
                    createdAt
                    role
                    members {
                        id
                        username
                        firstName
                        lastName
                    }
                }
            }
        }
    """
    result = gql_execute(client, query)
    if not result['getUserTeams'] or not result['getUserTeams']['success']:
        raise RuntimeError(result['getUserTeams']["message"])
    return result['getUserTeams']['teams']


def get_available_datastores(team_id: Optional[str] = None):
    client = create_gql_client()
    query = """
        query GetDatastores ($teamId: ID){
            getDatastores(teamId: $teamId) {
                id
                name
                version
                size
                createdAt
                snapshotStatus
                clusterId
                userDetails {
                    id
                    username
                    firstName
                    lastName
                }
            }
        }
    """
    params = {'teamId': team_id}
    result = gql_execute(client, query, **params)
    return result['getDatastores']


def delete_datastore(name: str, version: int, cluster: Optional[str] = None):
    """Delete datastore for user

    Parameters
    ----------
    name
        Datastore name
    version
        Datastore version
    cluster
        cluster id to operate on

    Raises
    ------
    RuntimeError
        If datastore deletion fails
    """
    client = create_gql_client()
    mutation = """
        mutation (
            $name: String!
            $version: Int!
            $clusterId: String
            ) {
            deleteDatastore (
                properties: {
                        name: $name,
                        version: $version,
                        clusterId: $clusterId
                    }
            ) {
            success
            message
            }
        }
    """
    params = {'name': name, 'version': version, 'clusterId': cluster}
    result = gql_execute(client, mutation, **params)

    if not result['deleteDatastore']['success']:
        message = result['deleteDatastore']['message']
        raise RuntimeError(f'failed to delete datastore {name} with version {version}: {message}')


def create_datastore(name: str, source: str, cluster: Optional[str] = None):
    """Create datastore in Grids
    """
    # Create Grid datastore directly in Grid without uploading, since Grid will
    # handle extraction and creating a optimizted datastore automatically.
    client = create_gql_client()
    mutation = """
        mutation (
            $name: String!
            $source: String
            $clusterId: String
            ) {
            createDatastore (
                properties: {
                        name: $name
                        source: $source
                        clusterId: $clusterId
                    }
            ) {
            success
            message
            datastoreId
            datastoreVersion
            }
        }
    """

    params = {'name': name, 'source': source, 'clusterId': cluster}
    result = gql_execute(client, mutation, **params)
    success = result['createDatastore']['success']
    message = result['createDatastore']['message']
    if not success:
        raise ValueError(f"Unable to create datastore: {message}")

    res = result['createDatastore']
    res['datastoreVersion'] = int(res['datastoreVersion'])
    return res


def get_datastore_upload_multipart_presigned_urls(path: str, datastore_id: str, count: int):
    client = create_gql_client()
    query = """
        query GetMultiPartPresignedUrls (
            $path: String!,
            $datastoreId: ID!,
            $count: Int!
        ) {
            getMultiPartPresignedUrls (
                path: $path,
                datastoreId: $datastoreId,
                count: $count
            ) {
                uploadId
                presignedUrls {
                    url
                    part
                }
            }
        }
    """
    params = {
        'path': path,
        'count': count,
        'datastoreId': datastore_id,
    }
    result = gql_execute(client, query, **params)
    return result['getMultiPartPresignedUrls']


def complete_multipart_datastore_upload(datastore_id: str, upload_id: str, parts: str, path: str, cluster_id: str):
    client = create_gql_client()
    mutation = """
         mutation (
             $datastoreId: ID!
             $uploadId: String!
             $parts: JSONString!
             $path: String!
             $clusterId: String
             ) {
             completeMultipartDatastoreUpload (
                 properties: {
                         datastoreId: $datastoreId
                         uploadId: $uploadId
                         parts: $parts
                         path: $path
                         clusterId: $clusterId
                     }
             ) {
             success
             message
             }
         }
     """
    params = {
        'datastoreId': datastore_id,
        'uploadId': upload_id,
        'parts': parts,
        'path': path,
        'clusterId': cluster_id,
    }
    result = gql_execute(client, mutation, **params)
    success = result['completeMultipartDatastoreUpload']['success']
    message = result['completeMultipartDatastoreUpload']['message']
    if not success:
        raise ValueError(f"Unable to complete multi-part upload: {message}")


def complete_datastore_upload(datastore_id: str, size_mib: int):
    client = create_gql_client()
    mutation = """
        mutation (
            $datastoreId: ID!
            $sizeMib: Int!
            ) {
            completeDatastoreUpload (
                properties: {
                        datastoreId: $datastoreId
                        sizeMib: $sizeMib
                    }
            ) {
            success
            message
            }
        }
    """
    params = {'datastoreId': datastore_id, 'sizeMib': size_mib}
    result = gql_execute(client, mutation, **params)

    success = result['completeDatastoreUpload']['success']
    message = result['completeDatastoreUpload']['message']
    if not success:
        raise ValueError(f"Unable to complete datastore upload: {message}")


def get_user():
    client = create_gql_client()
    query = """
        query {
            getUser {
                isVerified
                completedSignup
                isBlocked
            }
        }
        """
    result = gql_execute(client, query)
    return result["getUser"]
