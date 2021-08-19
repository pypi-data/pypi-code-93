import concurrent.futures
import datetime
import time

import pendulum
import pytest
from dagster import RunRequest, daily_schedule, graph, op, repository, sensor
from dagster.core.host_representation.origin import RegisteredRepositoryLocationOrigin
from dagster.core.launcher.base import LaunchRunContext
from dagster.core.workspace.dynamic_workspace import DynamicWorkspace
from dagster.grpc.types import (
    ExecutionPlanSnapshotArgs,
    ExternalScheduleExecutionArgs,
    PartitionArgs,
    PartitionNamesArgs,
    PartitionSetExecutionParamArgs,
    PipelineSubsetSnapshotArgs,
    SensorExecutionArgs,
)
from dagster.serdes import deserialize_json_to_dagster_namedtuple
from dagster.utils.error import SerializableErrorInfo
from dagster_cloud.api.dagster_cloud_api import (
    DagsterCloudApi,
    DagsterCloudApiGrpcResponse,
    DagsterCloudApiSuccess,
    DagsterCloudApiUnknownCommandResponse,
    LaunchRunArgs,
    TerminateRunArgs,
)
from dagster_cloud.daemon.dagster_cloud_api_daemon import DagsterCloudApiDaemon
from dagster_cloud.workspace.origin import CodeDeploymentMetadata
from ursula.storage.host_cloud.cloud_storage.schema import (
    RepositoryLocationsDataTable,
    RepositoryLocationsTable,
)
from ursula.user_code.workspace import dagster_cloud_api_call


def _add_location(cloud_storage, location_name="location"):
    cloud_storage.add_location(
        location_name,
        deployment_metadata=CodeDeploymentMetadata(python_file=__file__),
    )

    return RegisteredRepositoryLocationOrigin(location_name)


@pytest.fixture(name="cloud_api_daemon")
def cloud_api_daemon_fixture():
    return DagsterCloudApiDaemon()


@pytest.fixture(name="user_code_launcher")
def user_code_launcher_fixture(agent_instance):
    user_code_launcher = agent_instance.user_code_launcher

    yield user_code_launcher


@pytest.fixture(name="workspace")
def dynamic_workspace_fixture(user_code_launcher):
    with DynamicWorkspace(user_code_launcher) as workspace:
        yield workspace


@pytest.fixture(name="cloud_storage")
def cloud_storage_fixture(host_instance):
    cloud_storage = host_instance.cloud_storage

    yield cloud_storage

    with cloud_storage.transaction() as conn:
        conn.execute(RepositoryLocationsDataTable.delete())
        conn.execute(RepositoryLocationsTable.delete())


@pytest.fixture(name="user_cloud_agent_request_storage")
def user_agent_request_storage_fixture(host_instance):
    user_cloud_agent_request_storage = host_instance.user_cloud_agent_request_storage

    yield user_cloud_agent_request_storage

    user_cloud_agent_request_storage.wipe()


@pytest.fixture(name="repository_location")
def repository_location_fixture(cloud_api_daemon, agent_instance, workspace, cloud_storage):
    repository_location_origin = _add_location(cloud_storage)

    next(cloud_api_daemon.run_iteration(agent_instance, workspace))
    workspace.grpc_server_registry.reconcile()

    repository_location = workspace.get_location(repository_location_origin)

    yield repository_location


@op
def success():
    time.sleep(1)


@graph
def success_graph():
    success()


@daily_schedule(
    name="daily_success_job", pipeline_name="success_job", start_date=datetime.datetime(2020, 1, 1)
)
def daily_success_job(_):
    return {}


@sensor(name="success_job_sensor", pipeline_name="success_job")
def success_job_sensor():
    yield RunRequest(run_key=None)


success_job = success_graph.to_job(name="success_job")


@repository
def repo():
    return [success_job, daily_success_job, success_job_sensor]


def _assert_responses_for_requests(
    requests,
    num_requests,
    user_cloud_agent_request_storage,
    response_type=(DagsterCloudApiGrpcResponse, DagsterCloudApiSuccess),
):
    assert len(requests) == num_requests

    for request in requests:
        serialized_response = user_cloud_agent_request_storage.get_response(request.request_id)
        response = deserialize_json_to_dagster_namedtuple(serialized_response)
        print(response)
        assert isinstance(response, response_type)

        assert response.thread_telemetry


def _run_to_request_completion(cloud_api_daemon, agent_instance, workspace):
    # Submit requests to thread pool
    next(cloud_api_daemon.run_iteration(agent_instance, workspace))

    # Wait for all futures to return before processing
    futures = [
        future_context.future
        for future_context in cloud_api_daemon.request_ids_to_future_context.values()
    ]
    concurrent.futures.wait(futures)

    # Process all finished requests
    next(cloud_api_daemon.run_iteration(agent_instance, workspace))

    # Assert that dictionary of future contexts is empty
    assert not cloud_api_daemon.request_ids_to_future_context


def test_initial_run_iteration_populates_workspace(
    cloud_api_daemon,
    agent_instance,
    workspace,
    cloud_storage,
):
    repository_location_origin = _add_location(cloud_storage)

    with pytest.raises(Exception):
        workspace.get_location(repository_location_origin)

    next(cloud_api_daemon.run_iteration(agent_instance, workspace))
    workspace.grpc_server_registry.reconcile()

    assert workspace.get_location(repository_location_origin)


def test_repeated_run_iteration_populates_workspace_only_once(
    cloud_api_daemon,
    agent_instance,
    workspace,
    cloud_storage,
):
    repository_location_origin_one = _add_location(cloud_storage, location_name="location1")

    next(cloud_api_daemon.run_iteration(agent_instance, workspace))

    repository_location_origin_two = _add_location(cloud_storage, location_name="location2")

    next(cloud_api_daemon.run_iteration(agent_instance, workspace))
    workspace.grpc_server_registry.reconcile()

    assert workspace.get_location(repository_location_origin_one)

    with pytest.raises(Exception):
        workspace.get_location(repository_location_origin_two)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_check_for_workspace_updates(
    cloud_api_daemon,
    agent_instance,
    workspace,
    cloud_storage,
    user_cloud_agent_request_storage,
    num_requests,
):
    repository_location_origin_one = _add_location(cloud_storage, location_name="location1")

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    repository_location_origin_two = _add_location(cloud_storage, location_name="location2")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.CHECK_FOR_WORKSPACE_UPDATES,
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)
    workspace.grpc_server_registry.reconcile()

    assert workspace.get_location(repository_location_origin_one)
    assert workspace.get_location(repository_location_origin_two)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_execution_plan(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_EXECUTION_PLAN,
            ExecutionPlanSnapshotArgs(
                pipeline_origin=external_pipeline.get_external_origin(),
                solid_selection=external_pipeline.solid_selection,
                run_config={},
                mode="default",
                step_keys_to_execute=None,
                pipeline_snapshot_id=external_pipeline.identifying_pipeline_snapshot_id,
                known_state=None,
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_subset_external_pipeline_result(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_SUBSET_EXTERNAL_PIPELINE_RESULT,
            PipelineSubsetSnapshotArgs(
                pipeline_origin=external_pipeline.get_external_origin(),
                solid_selection=None,
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_config(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_repository = repository_location.get_repository("repo")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_CONFIG,
            PartitionArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
                partition_name="2020-01-01",
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_tags(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_repository = repository_location.get_repository("repo")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_TAGS,
            PartitionArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
                partition_name="2020-01-01",
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_names(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_repository = repository_location.get_repository("repo")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_NAMES,
            PartitionNamesArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_set_execution_param_data(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_repository = repository_location.get_repository("repo")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_SET_EXECUTION_PARAM_DATA,
            PartitionSetExecutionParamArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
                partition_names=["2020-01-01"],
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_schedule_execution_data(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_repository = repository_location.get_repository("repo")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_SCHEDULE_EXECUTION_DATA,
            ExternalScheduleExecutionArgs(
                repository_origin=external_repository.get_external_origin(),
                instance_ref=agent_instance.get_ref(),
                schedule_name="daily_success_job",
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_sensor_execution_data(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    num_requests,
):
    external_repository = repository_location.get_repository("repo")

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.GET_EXTERNAL_SENSOR_EXECUTION_DATA,
            SensorExecutionArgs(
                repository_origin=external_repository.get_external_origin(),
                instance_ref=agent_instance.get_ref(),
                sensor_name="success_job_sensor",
                last_completion_time=None,
                last_run_key=None,
                cursor=None,
            ),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_launch_run(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    host_instance,
    repository_location,
    num_requests,
):
    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    pipeline_run = host_instance.create_run_for_pipeline(
        pipeline_def=success_job,
        external_pipeline_origin=external_pipeline.get_external_origin(),
    )

    requests = []
    for _ in range(num_requests):
        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.LAUNCH_RUN,
            LaunchRunArgs(pipeline_run=pipeline_run),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_terminate_run(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    host_instance,
    repository_location,
    num_requests,
):
    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    pipeline_run = host_instance.create_run_for_pipeline(
        pipeline_def=success_job,
        external_pipeline_origin=external_pipeline.get_external_origin(),
    )

    launcher = workspace.grpc_server_registry.run_launcher()

    requests = []
    for _ in range(num_requests):
        launcher.launch_run(LaunchRunContext(pipeline_run=pipeline_run, workspace=workspace))

        request = dagster_cloud_api_call(
            user_cloud_agent_request_storage,
            DagsterCloudApi.TERMINATE_RUN,
            TerminateRunArgs(pipeline_run=pipeline_run),
            wait_for_response=False,
        )

        requests.append(request)

    _run_to_request_completion(cloud_api_daemon, agent_instance, workspace)

    _assert_responses_for_requests(requests, num_requests, user_cloud_agent_request_storage)


def test_future_timed_out(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
    repository_location,
    monkeypatch,
):
    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    original_submit = cloud_api_daemon.executor.submit

    def submit(*args, **kwargs):
        future = original_submit(*args, **kwargs)
        future.set_exception(concurrent.futures.TimeoutError)

        return future

    monkeypatch.setattr(cloud_api_daemon.executor, "submit", submit)

    dagster_cloud_api_call(
        user_cloud_agent_request_storage,
        DagsterCloudApi.GET_EXTERNAL_EXECUTION_PLAN,
        ExecutionPlanSnapshotArgs(
            pipeline_origin=external_pipeline.get_external_origin(),
            solid_selection=external_pipeline.solid_selection,
            run_config={},
            mode="default",
            step_keys_to_execute=None,
            pipeline_snapshot_id=external_pipeline.identifying_pipeline_snapshot_id,
            known_state=None,
        ),
        wait_for_response=False,
    )

    result = next(cloud_api_daemon.run_iteration(agent_instance, workspace))

    assert isinstance(result, SerializableErrorInfo)
    assert result.cls_name == "TimeoutError"


def test_unknown_api(
    cloud_api_daemon,
    agent_instance,
    workspace,
    user_cloud_agent_request_storage,
):

    cloud_api_daemon._process_api_request(  # pylint: disable=protected-access
        {"requestId": "foobar", "requestApi": "DO_THE_HOKEY_POKEY", "requestBody": ""},
        agent_instance,
        workspace,
        pendulum.now("UTC").timestamp(),
    )

    serialized_response = user_cloud_agent_request_storage.get_response("foobar")
    response = deserialize_json_to_dagster_namedtuple(serialized_response)
    assert isinstance(response, DagsterCloudApiUnknownCommandResponse)
    assert response.thread_telemetry
