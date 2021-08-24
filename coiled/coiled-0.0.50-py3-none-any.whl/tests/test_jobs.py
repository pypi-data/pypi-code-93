import asyncio
import time
from os import environ

import coiled
import pytest
from asgiref.sync import sync_to_async
from dask.distributed import Client

from backends.types import BackendChoices

from ..errors import ServerError
from ..utils import ExperimentalFeatureWarning

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.test_group("test_jobs"),
]


@pytest.mark.asyncio
async def test_create_start_stop_job(sample_user, cloud, software_env, cleanup):

    job_name = "my-app"
    if not environ.get("TEST_BACKEND", BackendChoices.IN_PROCESS) == "aws":
        # NOTE: if not testing against AWS, this will be running locally; don't
        # run a long-lived command!
        command = ["sleep", "2"]
    else:
        command = ["python", "-vvv", "-m", "http.server"]
    await cloud.create_job_configuration(
        name=job_name,
        command=command,
        cpu=2,
        memory="4 GiB",
        software=software_env,
        ports=[8000],
    )

    results = await cloud.list_job_configurations()
    assert job_name in results
    assert results[job_name]["software"] == software_env
    assert results[job_name]["cpu"] == 2
    assert results[job_name]["command"] == command
    assert not await cloud.list_jobs()

    job_instance_name = await cloud.start_job(configuration=job_name)

    while True:
        results = await cloud.list_jobs()
        if len(results) == 0:
            await asyncio.sleep(0.1)
        else:
            break
    assert len(results) == 1
    name = list(results)[0]
    assert name == job_instance_name
    assert results[name]["configuration"] == f"{sample_user.user.username}/{job_name}"

    await cloud.stop_job(name=name)

    # Ensure there are no running jobs
    assert not await cloud.list_jobs()


@pytest.mark.xfail(reason="https://github.com/coiled/cloud/issues/1961")
@pytest.mark.asyncio
async def test_start_job_nondefault_aws_region(
    sample_user, cloud, software_env, cleanup
):

    job_name = "my-app"
    region = "us-east-1"

    await cloud.create_job_configuration(
        name=job_name,
        command=["which", "dask"],
        software=software_env,
        ports=[8000],
    )

    await cloud.start_job(job_name, backend_options={"region": region})

    while True:
        results = await cloud.list_jobs()
        if len(results) == 0:
            await asyncio.sleep(0.1)
        else:
            break

    assert len(results) == 1
    name = list(results)[0]

    await cloud.stop_job(name=name)

    # Ensure there are no running jobs
    assert not await cloud.list_jobs()


@pytest.mark.asyncio
async def test_jobs_experimental(sample_user, cloud, software_env, cleanup):
    with pytest.warns(ExperimentalFeatureWarning, match="create_job_configuration"):
        coiled.create_job_configuration(
            name="my-app",
            command=["python", "--version"],
            software=software_env,
        )


@pytest.mark.asyncio
async def test_create_list_delete_job_configurations(
    sample_user, cloud, software_env, cleanup
):

    job_name = "my-app"
    command = ["python", "--version"]
    await cloud.create_job_configuration(
        name=job_name,
        command=["python", "--version"],
        cpu=2,
        memory="4 GiB",
        software=software_env,
        ports=[8000],
    )

    # Ensure output is formatted as expected
    results = await cloud.list_job_configurations()
    assert job_name in results
    assert results[job_name]["software"] == software_env
    assert results[job_name]["cpu"] == 2
    assert results[job_name]["command"] == command

    await cloud.delete_job_configuration(job_name)
    assert not await cloud.list_job_configurations()


@pytest.mark.asyncio
async def test_update_job_configuration(sample_user, cloud, software_env, cleanup):

    job_name = "my-app"
    command = ["python", "--version"]
    await cloud.create_job_configuration(
        name=job_name,
        command=command,
        cpu=2,
        memory="4 GiB",
        software=software_env,
        ports=[8000],
    )

    results = await cloud.list_job_configurations()
    assert results[job_name]["software"] == software_env
    assert results[job_name]["cpu"] == 2
    assert results[job_name]["command"] == command
    assert results[job_name]["ports"] == [8000]

    # Update and ensure changes are reflected in output of list_job_configurations
    command = ["python", "-vvv", "--version"]
    await cloud.create_job_configuration(
        name=job_name,
        command=command,
        cpu=4,
        memory="16 GiB",
        software=software_env,
        ports=[],
    )

    results = await cloud.list_job_configurations()
    assert results[job_name]["software"] == software_env
    assert results[job_name]["cpu"] == 4
    assert results[job_name]["command"] == command
    assert results[job_name]["ports"] == []


@pytest.mark.asyncio
@pytest.mark.xfail(reason="https://github.com/coiled/cloud/issues/3100")
async def test_jobs_listable_clusters_not(
    cloud, software_env, cluster_configuration, cleanup
):
    # Ensure that process configurations associated with a cluster
    # don't show up in the output of list_job_configurations

    await cloud.create_job_configuration(
        name="my-job",
        command=["python", "--version"],
        software=software_env,
    )

    results = await cloud.list_job_configurations()
    assert len(results) == 1

    async with coiled.Cluster(
        asynchronous=True, cloud=cloud, configuration=cluster_configuration
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)
            results = await cloud.list_job_configurations()
            assert len(results) == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_jobs_limit(sample_user, cloud, software_env, cleanup):
    # Set CPU limit to 1 core
    sample_user.membership.limit = 1
    await sync_to_async(sample_user.membership.save)()  # type: ignore
    # Make sure it doesn't go away quickly
    if not environ.get("TEST_BACKEND", BackendChoices.IN_PROCESS) == "aws":
        command = ["sleep", "2"]
    else:
        command = ["python", "-vvv", "-m", "http.server"]

    job_name = "my-app"
    await cloud.create_job_configuration(
        name=job_name,
        software=software_env,
        command=command,
    )
    # Can start one job
    await cloud.start_job(configuration=job_name)
    # Attempting to start another raises a limit error
    with pytest.raises(ServerError, match="CPU limit"):
        await cloud.start_job(configuration=job_name)


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-1")
async def test_jupyterlab_job_logs(sample_user, cloud, cleanup, docker_prune):
    await cloud.create_software_environment(
        name="base-notebook",
        container="jupyter/base-notebook",
    )
    app_name = "my-app"
    await cloud.create_job_configuration(
        name=app_name,
        command=["start.sh", "jupyter", "lab"],
        cpu=2,
        memory="4 GiB",
        software="base-notebook",
        ports=[8888],
    )
    job_name = await cloud.start_job(configuration=app_name)
    job_id = await cloud.get_job_by_name(job_name)
    start_time = time.time()
    while True:
        jobs = await cloud.list_jobs()
        if len(jobs):
            break
        else:
            assert time.time() < start_time + 15
            await asyncio.sleep(0.5)
    # Logs take a while to appear on AWS
    start_time = time.time()
    while True:
        try:
            logs = await cloud.job_logs(job_id=job_id)
            if logs["Process"]:
                break
        except Exception:
            pass
        assert time.time() < start_time + 120
        await asyncio.sleep(0.5)
    assert logs
    await cloud.stop_job(name=job_name)


@pytest.mark.asyncio
async def test_job_configuration_files(
    sample_user, cloud, software_env, cleanup, tmp_path
):

    tmp_file = tmp_path / "foo.txt"
    with open(tmp_file, "w") as f:
        f.write("bar")

    job_name = "my-app"
    await cloud.create_job_configuration(
        name=job_name,
        software=software_env,
        command=["python", "--version"],
        files=[str(tmp_file)],
    )

    results = await cloud.list_job_configurations()
    assert results[job_name]["files"] == ["foo.txt"]


@pytest.mark.skipif(
    not environ.get("TEST_BACKEND", BackendChoices.IN_PROCESS) == "aws",
    reason="ECS only test?",
)
@pytest.mark.asyncio
async def test_completed_job_updates_status_stopped(
    sample_user, cloud, software_env, tmp_path, backend, cleanup
):
    # Ensure that after the Job command has completed running
    # the Job's status is updated to STOPPED

    # TODO: Fix this test so it runs using the in-process backend.
    # Currently the job status is never updated to STOPPED at the end of
    # the test

    tmp_file = tmp_path / "foo.py"
    contents = """
import sys, time
print(sys.path)
print(sys.version)
time.sleep(5)
"""
    with open(tmp_file, "w") as f:
        f.write(contents)

    job_name = "my-app"
    await cloud.create_job_configuration(
        name=job_name,
        software=software_env,
        command=["python", "foo.py"],
        files=[str(tmp_file)],
    )
    await cloud.start_job(job_name)
    # Check job has RUNNING status
    jobs = await cloud.list_jobs()
    while jobs == {}:
        await asyncio.sleep(0.1)
        jobs = await cloud.list_jobs()
    # 1
    # while jobs == {}:
    assert jobs

    # Ensure job status is updated to STOPPED after command has been run
    while jobs:
        jobs = await cloud.list_jobs()
        await asyncio.sleep(0.5)


@pytest.mark.asyncio
async def test_job_configuration_update(
    sample_user, cloud, software_env, cleanup, docker_prune
):
    # Create a job configuration
    job_name = "my-app"
    await cloud.create_job_configuration(
        name=job_name,
        command=["python", "--version"],
        cpu=2,
        memory="4 GiB",
        software=software_env,
        ports=[8000],
        description="foo",
    )

    # Ensure output is formatted as expected
    results = await cloud.list_job_configurations()
    assert job_name in results
    assert results[job_name]["software"] == software_env
    assert results[job_name]["cpu"] == 2
    assert results[job_name]["memory"] == 4
    assert results[job_name]["command"] == ["python", "--version"]
    assert results[job_name]["ports"] == [8000]
    assert results[job_name]["description"] == "foo"

    # Update the job configuration
    await cloud.create_software_environment(
        name="my-env-2", container="coiled/notebook:latest"
    )
    await cloud.create_job_configuration(
        name=job_name,
        command=["python", "-m", "http.server"],
        cpu=4,
        memory="16 GiB",
        software="my-env-2",
        ports=[8000, 8787],
        description="bar",
    )

    # Ensure the job configuration has been updated as expected
    results = await cloud.list_job_configurations()
    assert job_name in results
    assert results[job_name]["software"] == "my-env-2"
    assert results[job_name]["cpu"] == 4
    assert results[job_name]["memory"] == 16
    assert results[job_name]["command"] == ["python", "-m", "http.server"]
    assert results[job_name]["ports"] == [8000, 8787]
    assert results[job_name]["description"] == "bar"


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_create_notebook(sample_user, cloud, cleanup):
    name = "mynotebook"
    coiled.create_notebook(
        name=name,
        cpu=2,
        memory="8 GiB",
    )

    envs = await cloud.list_software_environments()
    notebook_env = f"{sample_user.account.name}/{name}-notebook"
    assert notebook_env in envs
    assert envs[notebook_env]["container"] == "coiled/notebook:latest"

    jobs = await cloud.list_job_configurations()
    assert name in jobs
    assert jobs[name]["cpu"] == 2
    assert jobs[name]["memory"] == 8


@pytest.mark.django_db(transaction=True)
def test_jobs_coiled_credits(sample_user, cluster_configuration):
    program = sample_user.account.active_program
    program.update_usage(program.quota + 1)

    with pytest.raises(Exception) as e:
        coiled.start_job(configuration=cluster_configuration)
    assert "You have reached your quota" in e.value.args[0]


@pytest.mark.asyncio
async def test_runtime_environ(sample_user, cloud, software_env, cleanup, docker_prune):
    app_name = "my-app"
    await cloud.create_job_configuration(
        name=app_name,
        command=["env"],
        cpu=2,
        memory="4 GiB",
        software=software_env,
    )
    job_name = await cloud.start_job(
        configuration=app_name, environ={"MY_TESTING_ENV": "VAL"}
    )
    job_id = await cloud.get_job_by_name(job_name)
    start_time = time.time()
    while True:
        try:
            logs = await cloud.job_logs(job_id=job_id)
            if logs["Process"]:
                break
        except Exception:
            pass
        assert time.time() < start_time + 120
        await asyncio.sleep(0.5)
    assert logs
    assert "MY_TESTING_ENV=VAL" in logs["Process"]
    await cloud.stop_job(name=job_name)
