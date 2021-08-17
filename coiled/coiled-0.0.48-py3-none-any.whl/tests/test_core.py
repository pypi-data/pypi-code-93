import asyncio
import time
import uuid
from decimal import Decimal
from os import environ
from typing import Dict, cast
from unittest import mock

import coiled
import dask
import pytest
import structlog
from coiled.core import Async, Cloud, _parse_gcp_creds
from coiled.exceptions import (
    AWSCredentialsParameterError,
    AzureCredentialsParameterError,
    GCPCredentialsError,
    GCPCredentialsParameterError,
    RegistryParameterError,
    UnsupportedBackendError,
)
from dask.distributed import Client
from django.conf import settings

from backends import ecs, types
from backends.utils import parse_gcp_location
from common.exceptions import CoiledException
from software_environments.type_defs import ContainerRegistryType

from ..errors import ServerError
from ..utils import ParseIdentifierError

pytestmark = [
    pytest.mark.django_db(transaction=True),
]

logger = structlog.get_logger(__name__)

DASKDEV_IMAGE = environ.get("DASKDEV_IMAGE", "daskdev/dask:latest")
DASKDEV_IMAGE = "daskdev/dask:latest"


@pytest.mark.asyncio
async def test_version_error(base_user, remote_access_url, monkeypatch):
    with dask.config.set(
        {
            "coiled": {
                "user": base_user.user.username,
                "token": base_user.user.auth_token.key,
                "server": remote_access_url,
                "account": base_user.account.name,
                "no-minimum-version-check": False,
            }
        }
    ):
        monkeypatch.setattr(coiled.core, "COILED_VERSION", "0.0.14")
        with pytest.raises(ServerError, match="Coiled now requires"):
            async with coiled.Cloud(asynchronous=True):
                pass


@pytest.mark.asyncio
async def test_basic(sample_user):
    async with coiled.Cloud(
        asynchronous=True,
    ) as cloud:

        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts
        assert cloud.default_account == sample_user.user.username


@pytest.mark.asyncio
async def test_trailing_slash(remote_access_url, sample_user):
    async with coiled.Cloud(
        server=remote_access_url + "/",
        asynchronous=True,
    ):
        pass


@pytest.mark.asyncio
async def test_server_input(remote_access_url, sample_user):
    async with coiled.Cloud(
        server=remote_access_url.split("://")[-1],
        asynchronous=True,
    ) as cloud:
        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts
        assert cloud.default_account == sample_user.user.username


@pytest.mark.asyncio
async def test_informative_error_org(remote_access_url, sample_user):
    with pytest.raises(PermissionError) as info:
        async with coiled.Cloud(
            server=remote_access_url.split("://")[-1],
            account="does-not-exist",
            asynchronous=True,
        ):
            pass

    assert sample_user.account.slug in str(info.value)
    assert "does-not-exist" in str(info.value)


@pytest.mark.asyncio
async def test_config(remote_access_url, sample_user):
    async with coiled.Cloud(
        user=sample_user.user.username,
        token=sample_user.user.auth_token.key,
        server=remote_access_url,
        asynchronous=True,
    ) as cloud:
        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts
        assert cloud.default_account == sample_user.user.username


def test_config_attribute():
    assert coiled.config == dask.config.get("coiled")


@pytest.mark.asyncio
async def test_repr(remote_access_url, sample_user):
    async with coiled.Cloud(asynchronous=True) as cloud:
        for func in [str, repr]:
            assert sample_user.user.username in func(cloud)
            assert remote_access_url in func(cloud)


@pytest.mark.asyncio
async def test_normalize_name(cloud, cleanup):
    assert cloud._normalize_name(name="foo/bar") == ("foo", "bar")
    assert cloud._normalize_name(name="bar") == (cloud.default_account, "bar")
    assert cloud._normalize_name(name="bar", context_account="baz") == ("baz", "bar")

    # Invalid name raises
    with pytest.raises(ParseIdentifierError):
        cloud._normalize_name(name="foo/bar/baz")


@pytest.mark.test_group("core-slow-group-1")
def test_sync(sample_user, cluster_configuration):
    with coiled.Cloud() as cloud:
        assert cloud.user == sample_user.user.username
        assert sample_user.user.username in cloud.accounts

        with coiled.Cluster(
            n_workers=0, configuration=cluster_configuration, cloud=cloud
        ) as cluster:
            assert cluster.scale(1) is None


@pytest.mark.parametrize(
    "backend_options",
    [
        {},
        pytest.param(
            {"fargate_spot": True},
            marks=pytest.mark.xfail(reason="capacity provider error"),
        ),
    ],
)
@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-1")
async def test_cluster_management(
    cloud,
    sample_user,
    cluster_configuration,
    cleanup,
    backend_options,
):
    name = f"myname-{uuid.uuid4().hex}"
    result = await cloud.list_clusters()

    cluster_id = None
    try:
        cluster_id = await cloud.create_cluster(
            configuration=cluster_configuration,
            name=name,
            backend_options=backend_options,
        )

        result = await cloud.list_clusters()
        assert name in result
        await cloud.scale_up(cluster_id, n=1)

        async with coiled.Cluster(name=name, asynchronous=True) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)

                result = await cloud.list_clusters()
                # Check output is formatted properly
                # NOTE that if we're on AWS the scheduler doesn't really knows its
                # own public address, so we get it from the dashboard link
                if environ.get("TEST_BACKEND", "in_process") != "in_process":
                    address = (
                        client.dashboard_link.replace("/status", "")
                        .replace("8787", "8786")
                        .replace("http", "tls")
                    )
                else:
                    address = client.scheduler_info()["address"]
                r = result[name]
                assert r["address"] == address
                # TODO this is returning the id of the configuration.
                # We probably don't want that
                assert isinstance(r["configuration"], int)
                assert r["dashboard_address"] == client.dashboard_link
                assert r["account"] == sample_user.user.username
                assert r["status"] == "running"

    finally:
        if cluster_id is not None:
            await cloud.delete_cluster(cluster_id=cluster_id)

    # wait for the cluster to shut down
    clusters = await cloud.list_clusters()
    for i in range(5):
        if name not in clusters:
            break
        await asyncio.sleep(1)
        clusters = await cloud.list_clusters()

    assert name not in clusters


@pytest.mark.skipif(
    not environ.get("TEST_BACKEND", "in_process") == "aws",
    reason="We need AWS",
)
@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-1")
async def test_backend_option_validity(cloud_with_gpu, cluster_configuration, cleanup):
    with pytest.raises(ServerError, match="Select either fargate_spot or GPUs"):
        cluster = await cloud_with_gpu.create_cluster(
            name="gpu-cluster",
            configuration=cluster_configuration,
            worker_gpu=1,
            backend_options={"fargate_spot": True},
        )
        assert cluster


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-2")
async def test_cluster_proxied_dashboard_link(
    cloud,
    cluster_configuration,
    cleanup,
):
    # Make sure we are initially not using proxied dashboard addresses
    with dask.config.set({"coiled.dashboard.proxy": False}):
        async with coiled.Cluster(
            n_workers=1, configuration=cluster_configuration, asynchronous=True
        ) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)

                # Non-proxied dashboard address
                dashboard_address_expected = cluster._dashboard_address
                assert cluster.dashboard_link == dashboard_address_expected
                result = await cloud.list_clusters()
                dashboard_address = result[cluster.name]["dashboard_address"]
                assert dashboard_address == dashboard_address_expected

                # Switch to using proxied dashboard addresses
                with dask.config.set({"coiled.dashboard.proxy": True}):
                    cluster_id = result[cluster.name]["id"]
                    dashboard_address_expected = (
                        f"{cloud.server}/dashboard/{cluster_id}/status"
                    )
                    assert cluster.dashboard_link == dashboard_address_expected
                    result = await cloud.list_clusters()
                    dashboard_address = result[cluster.name]["dashboard_address"]
                    assert dashboard_address == dashboard_address_expected


@pytest.mark.skip(
    reason="Not working right now, and not critical at the moment. Should not block merging PRs."
)
@pytest.mark.asyncio
async def test_no_aws_credentials_warning(cloud, cluster_configuration, cleanup):
    name = "myname"
    environ["AWS_SHARED_CREDENTIALS_FILE"] = "/tmp/nocreds"
    AWS_ACCESS_KEY_ID = environ.pop("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = environ.pop("AWS_SECRET_ACCESS_KEY", "")
    await cloud.create_cluster(
        configuration=cluster_configuration,
        name=name,
    )

    with pytest.warns(UserWarning) as records:
        async with coiled.Cluster(name=name, asynchronous=True):
            pass

    warning = records[-1].message
    message = warning if isinstance(warning, str) else warning.args[0]
    assert message == "No AWS credentials found -- none will be sent to the cluster."
    del environ["AWS_SHARED_CREDENTIALS_FILE"]
    if any((AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)):
        environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
        environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID


@pytest.mark.asyncio
async def test_default_account(sample_user):
    async with coiled.Cloud(
        asynchronous=True,
    ) as cloud:
        assert cloud.accounts
        assert cloud.default_account == sample_user.user.username


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-2")
async def test_cluster_class(cloud, cluster_configuration, cleanup):
    print(f"Coiled config is: {coiled.config}")
    async with coiled.Cluster(
        n_workers=2, asynchronous=True, cloud=cloud, configuration=cluster_configuration
    ) as cluster:
        async with Client(cluster, asynchronous=True, timeout="120 seconds") as client:
            await client.wait_for_workers(2)

            clusters = await cloud.list_clusters()
            assert cluster.name in clusters

    # wait for the cluster to shut down
    clusters = await cloud.list_clusters()
    for i in range(5):
        if cluster.name not in clusters:
            break
        await asyncio.sleep(1)
        clusters = await cloud.list_clusters()

    assert cluster.name not in clusters


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-2")
async def test_cluster_class_overwrite(cloud, cluster_configuration, cleanup):
    await cloud.create_software_environment(
        name="new-env",
        container=DASKDEV_IMAGE,
    )
    worker_options = {"lifetime": "6001s"}
    scheduler_options = {"synchronize_worker_interval": "59s"}
    worker_cpu = 2
    # Create a cluster where we overwrite parameters in the cluster configuration
    async with coiled.Cluster(
        n_workers=1,
        configuration=cluster_configuration,
        software="new-env",  # Override software environment
        worker_cpu=worker_cpu,  # Override worker CPU
        worker_memory="8 GiB",
        worker_options=worker_options,  # Specify worker options
        scheduler_options=scheduler_options,  # Specify scheduler options
        asynchronous=True,
        cloud=cloud,
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            # Check that worker_options were propagated
            result = await client.run(lambda dask_worker: dask_worker.lifetime == 6001)
            assert all(result.values())
            assert all(
                w["nthreads"] == worker_cpu
                for w in client.scheduler_info()["workers"].values()
            )

            # Check that scheduler_options were propagated
            result = await client.run_on_scheduler(
                lambda dask_scheduler: dask_scheduler.synchronize_worker_interval
            )
            assert result == 59


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-3")
async def test_worker_options_scheduler_options(cloud, software_env, cleanup):
    # Create cluster configuration with worker and scheduler options
    worker_options = {"lifetime": "6001s", "nthreads": 2}
    scheduler_options = {"synchronize_worker_interval": "59s"}
    await cloud.create_cluster_configuration(
        name="my-config",
        software=software_env,
        worker_options=worker_options,
        scheduler_options=scheduler_options,
    )

    async with coiled.Cluster(
        n_workers=1, asynchronous=True, cloud=cloud, configuration="my-config"
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            # Check that worker_options were propagated
            result = await client.run(lambda dask_worker: dask_worker.lifetime == 6001)
            assert all(result.values())
            assert all(
                w["nthreads"] == 2 for w in client.scheduler_info()["workers"].values()
            )

            # Check that scheduler_options were propagated
            result = await client.run_on_scheduler(
                lambda dask_scheduler: dask_scheduler.synchronize_worker_interval
            )
            assert result == 59


@pytest.mark.skipif(
    not all(
        (
            environ.get("TEST_BACKEND", "in_process") == "aws",
            environ.get("TEST_AWS_SECRET_ACCESS_KEY", None),
            environ.get("TEST_AWS_ACCESS_KEY_ID", None),
        )
    ),
    reason="We need external AWS account credentials",
)
@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-3")
async def test_worker_class(cloud, software_env, cleanup):
    # Create cluster configuration with non-standard worker class
    await cloud.create_cluster_configuration(
        name="my-config",
        software=software_env,
        worker_class="dask.distributed.Worker",  # different than the default, nanny
    )

    async with coiled.Cluster(
        n_workers=1, asynchronous=True, cloud=cloud, configuration="my-config"
    ) as cluster:

        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            # Check that worker_class was used
            result = await client.run(
                lambda dask_worker: type(dask_worker).__name__ == "Worker"
            )
            assert all(result.values())


@pytest.mark.skip(reason="https://github.com/coiled/cloud/issues/2538")
@pytest.mark.asyncio
@pytest.mark.timeout(400)
@pytest.mark.test_group("core-slow-group-4")
async def test_scaling_limits(
    cloud: Cloud[Async], cleanup, cluster_configuration, sample_user
):
    async with coiled.Cluster(
        n_workers=sample_user.membership.limit // 2 - 1,
        name="first",
        configuration=cluster_configuration,
        asynchronous=True,
        cloud=cloud,
    ) as first:
        with pytest.raises(Exception) as info:
            await first.scale(sample_user.membership.limit * 2)

        assert "limit" in str(info.value)
        assert str(sample_user.membership.limit) in str(info.value)
        assert str(sample_user.membership.limit * 2) in str(info.value)

        async with coiled.Cluster(
            n_workers=sample_user.membership.limit // 2 - 1,
            name="second",
            configuration=cluster_configuration,
            asynchronous=True,
            cloud=cloud,
        ) as second:

            # At this point with both clusters we are maxed out at 10
            # (2 schedulers, 8 workers) all with 1 cpu each.
            # There's a 10 % buffer though

            with pytest.raises(Exception) as info:
                await second.scale(sample_user.membership.limit)

            assert "limit" in str(info.value)
            assert str(sample_user.membership.limit) in str(info.value)

            # We also shouldn't be able to create a cluster at this point
            with pytest.raises(ValueError) as create_info:
                await coiled.Cluster(
                    n_workers=sample_user.membership.limit * 2,
                    name="third",
                    configuration=cluster_configuration,
                    asynchronous=True,
                    cloud=cloud,
                )
            assert "Unable to create cluster" in str(create_info)
            # This would be nice, but currently our logic is duplicated
            # in the scale and the create methods
            # assert str(sample_user.membership.limit) in str(create_info.value)
            await second.scale(1)
            await second.scale(4)


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-4")
async def test_configuration_overrides_limits(
    cloud: Cloud[Async], cleanup, cluster_configuration, sample_user
):
    # Limits is 10
    with pytest.raises(Exception) as info:
        await coiled.Cluster(
            n_workers=2,
            name="first",
            configuration=cluster_configuration,
            worker_cpu=4,
            worker_memory="8 GiB",
            scheduler_cpu=4,
            scheduler_memory="8 GiB",
            cloud=cloud,
        )
    assert "limit" in str(info.value)


@pytest.mark.asyncio
@pytest.mark.xfail(reason="https://github.com/coiled/cloud/issues/2342")
@pytest.mark.test_group("core-slow-group-5")
async def test_cluster_logs(cloud, cleanup, cluster_configuration, sample_user):
    async with coiled.Cluster(
        name="first",
        configuration=cluster_configuration,
        asynchronous=True,
        backend_options={"region": "us-west-1"},
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

        logs = await cluster.get_logs()
        assert "Scheduler" in logs
        assert len(logs.keys()) == 5  # Scheduler and 4 workers
        scheduler_logs = await cluster.get_logs(workers=False)
        assert len(scheduler_logs) == 1
        worker_logs = await cluster.get_logs(scheduler=False)
        assert "Scheduler" not in worker_logs


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-5")
async def test_default_cloud(sample_user, software_env):
    """
    Raises ValueError since cluster configuration does not exist;
    subsequently create the cluster_config in default backend and successfully
    create
    """
    cluster_config = "foo"
    with pytest.raises(ValueError) as info:
        await coiled.Cluster(configuration=cluster_config, asynchronous=True)

    # Expected ValueError:
    #   ValueError("Cluster configuration 'test-t5s3nrzj/foo' not found.")
    assert "foo" in str(info.value)

    async with coiled.Cloud(
        asynchronous=True,
    ):
        async with coiled.Cloud(
            asynchronous=True,
        ) as cloud_2:
            await cloud_2.create_cluster_configuration(
                name=cluster_config,
                worker_cpu=1,
                worker_memory="2 GiB",
                software=software_env,
            )
            try:
                cluster = coiled.Cluster(
                    configuration=cluster_config, asynchronous=True
                )
                assert cluster.cloud is cloud_2
            finally:
                await cloud_2.delete_cluster_configuration(name=cluster_config)


@pytest.mark.asyncio
async def test_cloud_repr_html(cloud, cleanup):
    text = cloud._repr_html_()
    assert cloud.user in text
    assert cloud.server in text
    assert cloud.default_account in text


@pytest.mark.asyncio
async def test_create_and_list_cluster_configuration(
    cloud, cleanup, sample_user, software_env
):
    # TODO decide on defaults and who should own them (defaults in the REST API
    # or maybe just the sdk client)

    # Create basic cluster configuration
    # await cloud.create_cluster_configuration(name="config-1")

    # Create a more customized cluster configuration
    await cloud.create_cluster_configuration(
        name="config-2",
        software=software_env,
        worker_cpu=4,
        worker_memory="8 GiB",
        scheduler_cpu=2,
        scheduler_memory="4 GiB",
        private=True,
    )

    result = await cloud.list_cluster_configurations()
    cfg_name = f"{sample_user.account.name}/config-2"
    assert cfg_name in result
    cfg = result[cfg_name]
    assert cfg["account"] == sample_user.user.username
    assert software_env in str(cfg["scheduler"])
    assert software_env in str(cfg["worker"])

    assert "2" in str(cfg["scheduler"])
    assert "4" in str(cfg["worker"])
    assert cfg["private"] is True


@pytest.mark.asyncio
async def test_create_and_update_cluster_configuration(
    cloud, cleanup, sample_user, software_env
):
    await cloud.create_cluster_configuration(
        name="config-3",
        software=software_env,
        worker_cpu=4,
        worker_memory="8 GiB",
        scheduler_cpu=2,
        scheduler_memory="4 GiB",
    )
    expected_cfg_name = f"{sample_user.account.name}/config-3"
    result = await cloud.list_cluster_configurations()
    assert len(result) == 1
    cfg = result[expected_cfg_name]
    assert cfg["scheduler"]["cpu"] == 2
    assert cfg["worker"]["cpu"] == 4
    assert cfg["scheduler"]["memory"] == 4
    assert cfg["private"] is False
    assert cfg["worker"]["software"] == software_env
    assert cfg["scheduler"]["software"] == software_env

    await cloud.create_cluster_configuration(
        name="config-3",
        software=software_env,
        worker_cpu=4,
        worker_memory="8 GiB",
        scheduler_cpu=4,
        scheduler_memory="8 GiB",
        private=True,
    )
    result = await cloud.list_cluster_configurations()
    assert len(result) == 1
    cfg = result[expected_cfg_name]
    assert cfg["scheduler"]["cpu"] == 4
    assert cfg["worker"]["cpu"] == 4
    assert cfg["scheduler"]["memory"] == 8
    assert cfg["private"] is True


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-6")
async def test_update_cluster_configuration_updates_software(
    cloud, cleanup, sample_user, software_env
):
    await cloud.create_cluster_configuration(
        name="test-software", software=software_env
    )

    result = await cloud.list_cluster_configurations()
    expected_cfg_name = f"{sample_user.account.name}/test-software"
    cfg = result[expected_cfg_name]

    assert cfg["scheduler"]["software"] == f"{sample_user.account.name}/myenv"
    assert cfg["worker"]["software"] == f"{sample_user.account.name}/myenv"

    await cloud.create_software_environment(
        name="updated_env",
        container=DASKDEV_IMAGE,
    )

    await cloud.create_cluster_configuration(
        name="test-software", software="updated_env"
    )

    result = await cloud.list_cluster_configurations()
    expected_cfg_name = f"{sample_user.account.name}/test-software"
    cfg = result[expected_cfg_name]
    assert cfg["scheduler"]["software"] == "updated_env"
    assert cfg["worker"]["software"] == "updated_env"


@pytest.mark.skipif(
    not environ.get("TEST_BACKEND", "in_process") == "aws",
    reason="This needs the ECS backend",
)
@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-6")
async def test_create_and_update_cluster_configuration_validates(
    cloud_with_gpu, cleanup, sample_gpu_user, software_env
):
    with pytest.raises(Exception) as exc_info:
        await cloud_with_gpu.create_cluster_configuration(
            name="config-4",
            software=software_env,
            worker_cpu=1,
            worker_memory="111 GiB",
            scheduler_cpu=2,
            scheduler_memory="4 GiB",
        )
    result = str(exc_info)
    assert "Invalid CPU and memory" in result

    await cloud_with_gpu.create_cluster_configuration(
        name="config-4",
        software=software_env,
        worker_cpu=4,
        worker_memory="17 GiB",
        scheduler_cpu=2,
        scheduler_memory="4 GiB",
    )

    with pytest.raises(Exception) as exc_info:
        await cloud_with_gpu.create_cluster_configuration(
            name="config-4",
            software=software_env,
            worker_cpu=4,
            worker_gpu=1,
            worker_memory="21 GiB",
            scheduler_cpu=2,
            scheduler_memory="4 GiB",
        )
    result = str(exc_info)
    assert "Coiled currently does not support" in result


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-6")
async def test_cluster_configuration_with_gpu(
    cloud_with_gpu, cleanup, sample_gpu_user, software_env
):
    await cloud_with_gpu.create_cluster_configuration(
        name="config-4",
        software=software_env,
        worker_cpu=2,
        worker_gpu=1,
        worker_memory="4 GiB",
        scheduler_cpu=1,
        scheduler_memory="2 GiB",
    )
    result = await cloud_with_gpu.list_cluster_configurations()
    assert len(result) == 1
    assert result["mygpuuser/config-4"]["worker"]["gpu"] == 1


@pytest.mark.asyncio
async def test_cluster_configuration_update_gpu(
    cloud_with_gpu, cleanup, sample_gpu_user, software_env
):
    await cloud_with_gpu.create_cluster_configuration(
        name="x",
        software=software_env,
    )
    result = await cloud_with_gpu.list_cluster_configurations()
    assert not result["mygpuuser/x"]["worker"]["gpu"]

    await cloud_with_gpu.create_cluster_configuration(
        name="x",
        software=software_env,
        worker_gpu=1,
    )
    result = await cloud_with_gpu.list_cluster_configurations()
    assert result["mygpuuser/x"]["worker"]["gpu"]


@pytest.mark.asyncio
async def test_delete_cluster_configuration(cloud, cleanup, sample_user, software_env):
    # Initially no configurations
    result = await cloud.list_cluster_configurations()
    assert not result

    # Create two configurations
    await cloud.create_cluster_configuration(
        name="config-1",
        software=software_env,
        worker_cpu=1,
        worker_memory="2 GiB",
        # environment={"foo": "bar"},
    )
    await cloud.create_cluster_configuration(
        name="config-2",
        software=software_env,
        worker_cpu=2,
        worker_memory="4 GiB",
        # environment={"foo": "bar"},
    )

    result = await cloud.list_cluster_configurations()
    assert len(result) == 2

    # Delete one of the configurations
    await cloud.delete_cluster_configuration(name="config-1")
    result = await cloud.list_cluster_configurations()
    assert len(result) == 1
    assert f"{sample_user.account.name}/config-2" in result


@pytest.mark.asyncio
async def test_invalid_fargate_resources_raises(
    cloud: Cloud[Async],
    cleanup,
    cluster_configuration,
    backend,
):
    if not isinstance(backend, ecs.ClusterManager):
        pytest.skip()

    with pytest.raises(ValueError, match="Invalid CPU and memory combination"):
        await coiled.Cluster(
            configuration=cluster_configuration,
            worker_cpu=1,
            worker_memory="64 GiB",
            cloud=cloud,
        )


@pytest.mark.skip(reason="infinite loop error")
@pytest.mark.asyncio
async def test_current_click(sample_user, clean_configuration):
    with mock.patch("coiled.utils.input") as mock_input:
        with mock.patch("click.prompt") as mock_prompt:
            mock_input.side_effect = [sample_user.user.username, "n"]
            mock_prompt.return_value = "foo"
            with pytest.raises(Exception):
                await coiled.Cloud.current(asynchronous=True)


@pytest.mark.skip(reason="infinite loop error")
@pytest.mark.asyncio
async def test_current_click_2(sample_user, clean_configuration):
    with mock.patch("coiled.utils.input") as mock_input:
        with mock.patch("click.prompt") as mock_prompt:
            mock_input.side_effect = [sample_user.user.username, "n"]
            mock_prompt.return_value = "foo"
            with pytest.raises(Exception):
                await coiled.Cluster(configuration="default", asynchronous=True)


@pytest.mark.asyncio
async def test_current(sample_user, clean_configuration):
    with dask.config.set(
        {
            "coiled.user": sample_user.user.username,
            "coiled.token": str(sample_user.user.auth_token),
        }
    ):
        await coiled.Cloud.current(asynchronous=True)
        # await coiled.Cluster(configuration="default", asynchronous=True)  # no cluster config


@pytest.mark.asyncio
async def test_default_org_username(second_user):
    async with coiled.Cloud(asynchronous=True) as cloud:
        assert cloud.default_account == second_user.user.username


@pytest.mark.asyncio
async def test_account_config(sample_user, second_account):
    with dask.config.set({"coiled.account": second_account.account.slug}):
        async with coiled.Cloud(
            asynchronous=True,
        ) as cloud:
            assert cloud.default_account == second_account.account.slug


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-8")
async def test_list_clusters_account(
    second_account, cloud, cluster_configuration, cleanup
):
    # Create cluster in first account
    await cloud.create_cluster(
        name="cluster-1",
        configuration=cluster_configuration,
    )

    # Create cluster in second account
    await cloud.create_software_environment(
        name=f"{second_account.account.slug}/env-2",
        container=DASKDEV_IMAGE,
    )
    await cloud.create_cluster_configuration(
        name=f"{second_account.account.slug}/config-2",
        software="env-2",
    )
    await cloud.create_cluster(
        name="cluster-2",
        configuration=f"{second_account.account.slug}/config-2",
        account=second_account.account.slug,
    )

    # Ensure account= in list_clusters filters by the specified account
    result = await cloud.list_clusters(account=second_account.account.slug)
    assert len(result) == 1
    assert "cluster-2" in result

    # Cleanup second_account since regular cleanup uses the default account
    await asyncio.sleep(
        1
    )  # Allow the scheduler time to phone home. TODO: find a better way!
    await asyncio.gather(
        *[
            cloud.delete_cluster(
                cluster_id=c["id"],
                account=second_account.account.slug,
            )
            for c in result.values()
        ]
    )


# TODO generalize this for more than just the ECS backend
@pytest.mark.skipif(
    not environ.get("TEST_BACKEND", "in_process") == "aws",
    reason="The options in this test are ECS-specific",
)
@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-8")
async def test_account_options_and_overrides(
    account_with_options, cloud, cluster_configuration
):
    await cloud.create_cluster(
        name="cluster",
        configuration=cluster_configuration,
        account=account_with_options.account.slug,
    )

    result = await cloud.list_clusters(account=account_with_options.account.slug)
    assert result["cluster"]["options"]["region"] == "us-east-2"
    await cloud.create_cluster(
        name="cluster-2",
        configuration=cluster_configuration,
        account=account_with_options.account.slug,
        backend_options={"region": "us-west-1"},
    )
    result = await cloud.list_clusters(account=account_with_options.account.slug)
    assert result["cluster-2"]["options"]["region"] == "us-west-1"

    # Don't use the regular cleanup since it uses the default account
    await asyncio.sleep(
        1
    )  # Allow the scheduler time to phone home. TODO: find a better way!
    await asyncio.gather(
        *[
            cloud.delete_cluster(
                cluster_id=c["id"],
                account=account_with_options.account.slug,
            )
            for c in result.values()
        ]
    )


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-8")
async def test_connect_to_existing_cluster(cloud, cluster_configuration, cleanup):
    async with coiled.Cluster(
        n_workers=0, asynchronous=True, configuration=cluster_configuration
    ) as a:
        async with Client(a, asynchronous=True):
            pass  # make sure that the cluster is up

        async with coiled.Cluster(n_workers=0, asynchronous=True, name=a.name) as b:
            assert a.scheduler_address == b.scheduler_address

        async with Client(a, asynchronous=True):
            pass  # make sure that a is still up


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-9")
async def test_connect_same_name(cloud, cluster_configuration, cleanup, capsys):
    # Ensure we can connect to an existing, running cluster with the same name
    async with coiled.Cluster(
        name="foo-123",
        n_workers=0,
        asynchronous=True,
        configuration=cluster_configuration,
    ) as cluster1:
        async with coiled.Cluster(
            name="foo-123",
            asynchronous=True,
            configuration=cluster_configuration,
        ) as cluster2:
            assert cluster1.name == cluster2.name
            captured = capsys.readouterr()
            assert "using existing cluster" in captured.out.lower()
            assert cluster1.name in captured.out


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-9")
@pytest.mark.xfail(reason="Flaky: https://github.com/coiled/cloud/issues/2934")
async def test_create_cluster_with_account_in_config(cleanup, cloud_with_account):
    # If user sets 'account' in their coiled.yml we want to be
    # # able to create clusters without <account>/<name>
    # If jess sets 'account' to fedex list_cluster_configurations
    # should return the fedex configs.
    result = await cloud_with_account.list_cluster_configurations()
    assert "fedex/fedex-config" in result

    try:
        async with coiled.Cluster(
            configuration="fedex-config",
            cloud=cloud_with_account,
        ):
            pass  # cluster created without any issue
    except ValueError as e:
        pytest.fail(f"Unable to find {e}")


@pytest.mark.test_group("core-slow-group-9")
def test_public_api_software_environments(sample_user):
    results = coiled.list_software_environments()
    assert not results

    name = "foo"
    coiled.create_software_environment(name=name, container=DASKDEV_IMAGE)
    results = coiled.list_software_environments()
    assert len(results) == 1
    expected_env_name = f"{sample_user.account.name}/foo"
    assert expected_env_name in results
    assert results[expected_env_name]["container"] == DASKDEV_IMAGE

    coiled.delete_software_environment(name)
    results = coiled.list_software_environments()
    assert not results


def test_public_api_cluster_configurations(sample_user, software_env):
    results = coiled.list_cluster_configurations()
    assert not results

    name = "foo"
    coiled.create_cluster_configuration(name=name, software=software_env)
    expected_cfg_name = f"{sample_user.account.name}/foo"
    results = coiled.list_cluster_configurations()
    assert len(results) == 1
    assert expected_cfg_name in results
    assert results[expected_cfg_name]["scheduler"]["software"] == software_env

    coiled.delete_cluster_configuration(name)
    results = coiled.list_cluster_configurations()
    assert not results


@pytest.mark.django_db
def test_public_api_cluster_configurations_with_gpu(sample_user, software_env):
    # should not be able to use GPUs
    program = sample_user.account.active_program
    program.gpus_limit = 0
    program.save()

    name = "foo"
    with pytest.raises(Exception) as e:
        coiled.create_cluster_configuration(
            name=name, software=software_env, worker_gpu=1
        )
        assert "cannot configure clusters with GPUs" in e.value.args[0]

    # Allow GPUs
    program.gpus_limit = 1
    program.save()

    coiled.create_cluster_configuration(name=name, software=software_env, worker_gpu=1)
    results = coiled.list_cluster_configurations()
    expected_cfg_name = f"{sample_user.account.name}/foo"
    assert len(results) == 1
    assert expected_cfg_name in results

    coiled.delete_cluster_configuration(name)


@pytest.mark.test_group("core-slow-group-10")
def test_public_api_clusters(sample_user, cluster_configuration):
    results = coiled.list_clusters()
    assert not results

    name = "foo"
    coiled.create_cluster(name=name, configuration=cluster_configuration)
    results = coiled.list_clusters()
    results = cast(Dict[str, Dict], results)
    assert len(results) == 1
    assert name in results

    coiled.delete_cluster(name=name)
    results = coiled.list_clusters()
    assert not results


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-10")
async def test_multi_region(cloud, cluster_configuration, cleanup):
    async with coiled.Cluster(
        n_workers=1,
        name="uswest1",
        asynchronous=True,
        configuration=cluster_configuration,
        backend_options={"region": "us-west-1"},
    ) as cluster:
        async with Client(cluster, asynchronous=True):
            clusters = await cloud.list_clusters()
            assert cluster.name in clusters


@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-10")
async def test_backend_options(cloud, cluster_configuration, cleanup):
    """Region is supported for now"""
    async with coiled.Cluster(
        n_workers=1,
        name="uswest2",
        asynchronous=True,
        configuration=cluster_configuration,
        backend_options={"region": "us-west-1"},
    ) as cluster:
        async with Client(cluster, asynchronous=True):
            clusters = await cloud.list_clusters()
            assert cluster.name in clusters


@pytest.mark.django_db(transaction=True)  # implied by `live_server`, but explicit
@pytest.mark.test_group("core-slow-group-10")
def test_public_api_clusters_wanting_gpu_but_not_having_access(
    sample_user, software_env
):
    CONFIGURATION_NAME = "foo"
    program = sample_user.account.active_program
    program.gpus_limit = 1
    program.save()
    coiled.create_cluster_configuration(
        name=CONFIGURATION_NAME, software=software_env, worker_gpu=1
    )

    # Now restore to normal disabled state
    program.gpus_limit = 0
    program.save()
    # Assert we get an error trying to launch a cluster when we can't use GPUs
    with pytest.raises(Exception) as e:
        coiled.create_cluster(name="baz", configuration=CONFIGURATION_NAME)
    assert "cannot launch clusters with GPUs" in e.value.args[0]


@pytest.mark.test_group("core-slow-group-10")
def test_create_cluster_eats_unknown_exception_from_backend(
    settings, monkeypatch, backend, cluster_configuration
):
    settings.FF_SUPPRESS_UNKNOWN_EXCEPTIONS = True

    def fake_create_dask_cluster(*args, **kwargs):
        raise AssertionError("test assertion")

    for name, backend_manager in backend.items():
        monkeypatch.setattr(
            backend_manager, "create_dask_cluster", fake_create_dask_cluster
        )
    with pytest.raises(ServerError) as e:
        coiled.create_cluster(name="foo", configuration=cluster_configuration)

    assert (
        "Coiled cloud encountered an unknown issue handling your request, contact customer service and quote ID"
        in e.value.args[0]
    )


@pytest.mark.test_group("core-slow-group-10")
def test_create_cluster_raises_coiled_exception_from_backend(
    monkeypatch, backend, cluster_configuration
):
    def fake_create_dask_cluster2(*args, **kwargs):
        raise CoiledException("test assertion")

    for name, backend_manager in backend.items():
        monkeypatch.setattr(
            backend_manager, "create_dask_cluster", fake_create_dask_cluster2
        )
    with pytest.raises(ServerError) as e:
        coiled.create_cluster(name="foo", configuration=cluster_configuration)

    assert "test assertion" in e.value.args[0]


@pytest.mark.skip(reason="don't have s3fs on default testing configuration")
@pytest.mark.asyncio
@pytest.mark.test_group("core-slow-group-10")
async def test_aws_credentials(cloud, cluster_configuration, cleanup):
    s3fs = pytest.importorskip("s3fs")
    anon = s3fs.S3FileSystem(anon=True)
    try:
        anon.ls("coiled-data")
    except Exception:
        pass
    else:
        raise ValueError("Need to test against private bucket")

    s3 = s3fs.S3FileSystem()
    try:
        s3.ls("coiled-data")
    except Exception:
        # no local credentials for private bucket coiled-data
        pytest.skip()

    async with coiled.Cluster(
        n_workers=1,
        asynchronous=True,
        configuration=cluster_configuration,
    ) as a:
        async with Client(a, asynchronous=True) as client:

            def f():
                import s3fs

                s3 = s3fs.S3FileSystem()
                return s3.ls("coiled-data")

            await client.submit(f)  # ensure that this doesn't raise


@pytest.mark.asyncio
async def test_fully_qualified_names(cloud, cleanup, sample_user):
    # Ensure that fully qualified <account>/<name> can be used

    account = sample_user.user.username
    name = "foo"
    full_name = f"{account}/{name}"
    await cloud.create_software_environment(full_name, container=DASKDEV_IMAGE)
    result = await cloud.list_software_environments(account)
    assert f"{sample_user.account.name}/{name}" in result

    await cloud.create_cluster_configuration(full_name, software=full_name)
    result = await cloud.list_cluster_configurations(account)
    assert f"{sample_user.account.name}/{name}" in result

    await cloud.delete_cluster_configuration(full_name)
    assert not await cloud.list_cluster_configurations(account)

    await cloud.delete_software_environment(full_name)
    assert not await cloud.list_software_environments(account)


@pytest.mark.asyncio
async def test_create_cluster_warns(cluster_configuration):
    with pytest.warns(UserWarning, match="use coiled.Cluster()"):
        coiled.create_cluster(name="foo", configuration=cluster_configuration)
    coiled.delete_cluster("foo")


@pytest.mark.skipif(
    not all(
        (
            environ.get("TEST_BACKEND", "in_process") == "aws",
            environ.get("TEST_AWS_SECRET_ACCESS_KEY", None),
            environ.get("TEST_AWS_ACCESS_KEY_ID", None),
        )
    ),
    reason="We need external AWS account credentials",
)
@pytest.mark.asyncio
async def test_aws_external_account(external_aws_account_user):
    user = external_aws_account_user
    name = "aws"
    async with coiled.Cloud(account=user.username, asynchronous=True) as cloud:
        await cloud.create_software_environment(name=name, container=DASKDEV_IMAGE)
        result = await cloud.list_software_environments()
        assert name in result
        await cloud.create_cluster_configuration(
            name=name,
            software=name,
            worker_cpu=1,
            worker_memory="2 GiB",
            scheduler_cpu=1,
            scheduler_memory="2 GiB",
        )
        result = await cloud.list_cluster_configurations()
        assert name in result
        async with coiled.Cluster(
            name=name, n_workers=1, asynchronous=True, configuration=name, cloud=cloud
        ) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)
                clusters = await cloud.list_clusters()
                assert cluster.name in clusters


@pytest.mark.skipif(
    not environ.get("TEST_BACKEND", "in_process") == "aws",
    reason="We only have AWS tracking cost for now",
)
def test_public_cluster_cost_estimate(sample_user, cluster_configuration):
    costs = coiled.cluster_cost_estimate(configuration=cluster_configuration)
    assert "$" in costs
    assert "/hr" in costs
    cost = Decimal(costs[1:-3])
    assert cost > Decimal(0)


@pytest.mark.skipif(
    not environ.get("TEST_BACKEND", "in_process") == "aws",
    reason="We only have AWS tracking cost for now",
)
def test_public_cluster_cost_estimate_overrides(sample_user, cluster_configuration):
    costs = coiled.cluster_cost_estimate(
        n_workers=10,
        configuration=cluster_configuration,
        worker_cpu=4,
        worker_memory=16,
        scheduler_cpu=2,
        scheduler_memory=4,
        backend_options={"region": "us-west-1"},
    )
    assert "$" in costs
    assert "/hr" in costs
    cost = Decimal(costs[1:-3])
    assert cost > Decimal(1)


def test_public_api_list_core_usage_table(sample_user, capfd):
    coiled.list_core_usage()
    capture = capfd.readouterr()

    assert "Account_limit" not in capture.out
    assert "10" in capture.out
    assert "Core usage" in capture.out


def test_public_api_list_core_usage_json(sample_user):
    result = coiled.list_core_usage(json=True)

    assert result["tier_limit"] == 10
    assert result["user_total"] == 0
    assert result["account_total"] == 0
    assert result["jobs_total"] == 0
    assert result["clusters_total"] == 0


def test_public_api_list_local_versions(sample_user, capfd):
    coiled.list_local_versions()
    capture = capfd.readouterr()

    assert "Versions" in capture.out


def test_public_api_diagnostics(sample_user):
    result = coiled.diagnostics()

    assert result["health_check"]
    assert result["local_versions"]
    assert result["coiled_configuration"]


@pytest.mark.asyncio
@pytest.mark.test_group("slow_group_25")
async def test_wss_protocol_proxy_cluster(
    cloud,
    sample_user,
    cluster_configuration,
    cleanup,
):
    name = f"myname-{uuid.uuid4().hex}"
    result = await cloud.list_clusters()
    assert name not in result

    async with coiled.Cluster(
        name=name,
        configuration=cluster_configuration,
        asynchronous=True,
        protocol="wss",
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            result = await cloud.list_clusters()
            address = (
                client.dashboard_link.replace("status", "")
                .replace("dashboard", "cluster")
                .replace("http", "ws")
            )
            r = result[name]
            assert r["address"] == address
            # TODO this is returning the id of the configuration.
            # We probably don't want that
            assert isinstance(r["configuration"], int)
            assert r["dashboard_address"] == client.dashboard_link
            assert r["account"] == sample_user.user.username
            assert r["status"] == "running"

    # wait for the cluster to shut down
    clusters = await cloud.list_clusters()
    for i in range(5):
        if name not in clusters:
            break
        await asyncio.sleep(1)
        clusters = await cloud.list_clusters()

    assert name not in clusters


@pytest.mark.asyncio
@pytest.mark.test_group("slow_group_25")
async def test_tls_protocol_no_proxy_cluster(
    cloud,
    sample_user,
    cluster_configuration,
    cleanup,
):
    name = f"myname-{uuid.uuid4().hex}"
    result = await cloud.list_clusters()
    assert name not in result

    async with coiled.Cluster(
        name=name,
        configuration=cluster_configuration,
        asynchronous=True,
        protocol="tls",
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            result = await cloud.list_clusters()
            address = (
                client.dashboard_link.replace("/status", "")
                .replace("8787", "8786")
                .replace("http", "tls")
            )
            r = result[name]
            assert r["address"] == address
            # TODO this is returning the id of the configuration.
            # We probably don't want that
            assert isinstance(r["configuration"], int)
            assert r["dashboard_address"] == client.dashboard_link
            assert r["account"] == sample_user.user.username
            assert r["status"] == "running"

    # wait for the cluster to shut down
    clusters = await cloud.list_clusters()
    for i in range(5):
        if name not in clusters:
            break
        await asyncio.sleep(1)
        clusters = await cloud.list_clusters()

    assert name not in clusters


@pytest.mark.asyncio
async def test_multi_protocol_cluster(
    cloud,
    sample_user,
    cluster_configuration,
    cleanup,
):
    name = f"myname-{uuid.uuid4().hex}"
    result = await cloud.list_clusters()
    assert name not in result

    async with coiled.Cluster(
        name=name,
        configuration=cluster_configuration,
        asynchronous=True,
        scheduler_options={"protocol": ["wss", "tls"], "port": [8786, 8789]},
        worker_options={"protocol": "tls"},
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            result = await cloud.list_clusters()
            address = (
                client.dashboard_link.replace("status", "")
                .replace("dashboard", "cluster")
                .replace("http", "ws")
            )
            r = result[name]
            assert r["address"] == address
            # TODO this is returning the id of the configuration.
            # We probably don't want that
            assert isinstance(r["configuration"], int)
            assert r["dashboard_address"] == client.dashboard_link
            assert r["account"] == sample_user.user.username
            assert r["status"] == "running"
            # TODO: How to check that the worker protocol is in fact
            # using tls and contacting the scheduler on the priv ip

    # wait for the cluster to shut down
    clusters = await cloud.list_clusters()
    for i in range(5):
        if name not in clusters:
            break
        await asyncio.sleep(1)
        clusters = await cloud.list_clusters()

    assert name not in clusters


@pytest.mark.asyncio
async def test_multi_protocol_auto_assign_ports(
    cloud,
    sample_user,
    cluster_configuration,
    cleanup,
):
    name = f"myname-{uuid.uuid4().hex}"
    result = await cloud.list_clusters()
    assert name not in result

    async with coiled.Cluster(
        name=name,
        configuration=cluster_configuration,
        asynchronous=True,
        scheduler_options={"protocol": ["wss", "tls"]},
        worker_options={"protocol": "tls"},
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)

            result = await cloud.list_clusters()
            address = (
                client.dashboard_link.replace("status", "")
                .replace("dashboard", "cluster")
                .replace("http", "ws")
            )
            r = result[name]
            assert r["address"] == address
            # TODO this is returning the id of the configuration.
            # We probably don't want that
            assert isinstance(r["configuration"], int)
            assert r["dashboard_address"] == client.dashboard_link
            assert r["account"] == sample_user.user.username
            assert r["status"] == "running"
            # TODO: How to check that the worker protocol is in fact
            # using tls and contacting the scheduler on the priv ip

    # wait for the cluster to shut down
    clusters = await cloud.list_clusters()
    for i in range(5):
        if name not in clusters:
            break
        await asyncio.sleep(1)
        clusters = await cloud.list_clusters()

    assert name not in clusters


@pytest.mark.asyncio
async def test_toplevel_protocol_and_scheduler_options_protocol_collide():
    with pytest.raises(RuntimeError):
        coiled.Cluster(
            name="test",
            asynchronous=True,
            protocol="tls",
            scheduler_options={"protocol": "wss"},
        )


@pytest.mark.asyncio
async def test_toplevel_protocol_and_worker_options_protocol_collide():
    with pytest.raises(RuntimeError):
        coiled.Cluster(
            name="test",
            asynchronous=True,
            protocol="tls",
            worker_options={"protocol": "wss"},
        )


@pytest.mark.django_db(transaction=True)  # implied by `live_server`, but explicit
def test_cluster_coiled_credits(sample_user, cluster_configuration):
    program = sample_user.account.active_program
    program.update_usage(program.quota + 1)

    with pytest.raises(Exception) as e:
        coiled.create_cluster(name="baz", configuration=cluster_configuration)
    assert "You have reached your quota" in e.value.args[0]


@pytest.mark.xfail(reason="Failing in CI: https://github.com/coiled/cloud/issues/2858")
@pytest.mark.test_group("slow_group_25")
@pytest.mark.asyncio
async def test_account_environment_variables(
    account_with_env_variables,
    backend,
):
    user, account, membership = account_with_env_variables
    async with coiled.Cloud(account=account.slug, asynchronous=True) as cloud:
        await cloud.create_software_environment(
            name="soft_env",
            container=DASKDEV_IMAGE,
        )
        await cloud.create_cluster_configuration(
            account=account.slug,
            name="env",
            software="soft_env",
            worker_cpu=1,
            worker_memory="2 GiB",
            scheduler_cpu=1,
            scheduler_memory="2 GiB",
        )
        async with coiled.Cluster(
            n_workers=1,
            configuration=f"{account.slug}/env",
            asynchronous=True,
            cloud=cloud,
            account=account.slug,
        ) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)

                def test_env():
                    import os

                    return os.getenv("MY_TESTING_ENV")

                result = await client.run_on_scheduler(test_env)
                assert result == "env_variable"
                cluster_result = await client.submit(test_env)
                assert cluster_result == "env_variable"


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_default_coiled(
    cloud,
    sample_user,
):
    account = sample_user.account
    assert account.options == {}

    if environ.get("TEST_BACKEND") == "in_process":
        assert account.container_registry == {
            "type": ContainerRegistryType.CONDA,
        }
    else:
        assert account.container_registry == {
            "type": ContainerRegistryType.ECR,
            "credentials": {},
            "public_ecr": False,
            "region": settings.AWS_DEFAULT_USER_REGION,
        }
    assert account.backend == settings.DEFAULT_CLUSTER_BACKEND

    coiled.set_backend_options(use_coiled_defaults=True)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_invalid_args(
    cloud,
    sample_user,
):
    with pytest.raises(UnsupportedBackendError) as e_info:
        coiled.set_backend_options(backend="vm_geocities")  # type: ignore
    assert "Supplied backend: vm_geocities not in supported types: " in str(e_info)
    assert "aws" in str(e_info)
    assert "azure" in str(e_info)
    assert "gcp" in str(e_info)
    assert "ecs" in str(e_info)


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_aws_vm(
    cloud,
    sample_user,
):
    account = sample_user.account

    # set region
    coiled.set_backend_options(backend="aws", region=settings.AWS_DEFAULT_USER_REGION)
    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS

    # set no region
    coiled.set_backend_options(backend="aws")

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_aws_vm_customer_hosted(cloud, sample_user, mocker):

    mocker.patch("coiled.utils.boto3")
    account = sample_user.account

    # mock this _configure_backend method as we don't want to test this here
    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )

    # create VPC requires have aws_* creds
    with pytest.raises(AWSCredentialsParameterError) as e_info:
        coiled.set_backend_options(backend="aws", create_vpc=True)
    assert (
        "Creating an AWS VPC requires params: aws_access_key_id and aws_secret_access_key."
        in str(e_info)
    )

    credentials = {
        "aws_access_key_id": "test-aws_access_key_id",
        "aws_secret_access_key": "test-aws_secret_access_key",
    }

    # set region
    coiled.set_backend_options(
        backend="aws",
        aws_region=settings.AWS_DEFAULT_USER_REGION,
        create_vpc=True,
        **credentials,
    )
    account.refresh_from_db()

    options = {
        "aws_region_name": settings.AWS_DEFAULT_USER_REGION,
        "credentials": {
            "aws_access_key": "test-aws_access_key_id",
            "aws_secret_key": "test-aws_secret_access_key",
        },
        "provider_name": "aws",
        "type": "aws_cloudbridge_backend_options",
    }

    assert account.options == options

    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {
            "aws_access_key_id": "test-aws_access_key_id",
            "aws_secret_access_key": "test-aws_secret_access_key",
        },
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]
    assert kwargs_options.aws_region_name == options["aws_region_name"]


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_aws_ecs(
    cloud,
    sample_user,
):
    account = sample_user.account

    # set region
    coiled.set_backend_options(
        backend="ecs", aws_region=settings.AWS_DEFAULT_USER_REGION
    )
    account.refresh_from_db()

    assert account.options == {"region": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.ECS

    # set no region
    coiled.set_backend_options(backend="ecs")

    account.refresh_from_db()

    assert account.options == {"region": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.ECS

    with pytest.raises(UnsupportedBackendError) as e_info:
        coiled.set_backend_options(backend="ecs", create_vpc=True)

    assert "VPC for AWS ECS is no longer supported." in str(e_info.value)


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gcp_vm_coiled_hosted(cloud, sample_user):

    account = sample_user.account

    # set region
    coiled.set_backend_options(
        backend="gcp",
        zone=settings.GCP_DEFAULT_USER_ZONE,
    )
    account.refresh_from_db()

    default_region, default_zone = parse_gcp_location(settings.GCP_DEFAULT_USER_ZONE)
    assert account.options == {
        "gcp_region_name": default_region,
        "gcp_zone_name": default_zone,
    }
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_GCP

    # set no region or zone
    coiled.set_backend_options(backend="gcp")

    account.refresh_from_db()

    assert account.options == {
        "gcp_region_name": default_region,
        "gcp_zone_name": default_zone,
    }
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_GCP

    # make sure region makes it through
    coiled.set_backend_options(
        backend="gcp",
        gcp_region="us-central1",
    )
    account.refresh_from_db()
    assert account.options == {
        "gcp_region_name": "us-central1",
        # For now we add zone "c" to the end
        "gcp_zone_name": "us-central1-c",
    }


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gcp_vm_customer_hosted(cloud, sample_user, mocker):

    account = sample_user.account

    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )

    reqed_keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    coiled.set_backend_options(
        backend="gcp",
        create_vpc=True,
        gcp_service_creds_dict=gcp_service_creds_dict,
        gcp_project_id="test-project-name",
        gcp_region="gcp_region_name",
    )
    account.refresh_from_db()

    options = {
        "provider_name": "gcp",
        "type": "gcp_cloudbridge_backend_options",
        "gcp_project_name": "test-project-name",
        "gcp_region_name": "gcp_region_name",
        "gcp_zone_name": "gcp_region_name-c",
        "gcp_service_creds_dict": gcp_service_creds_dict,
    }
    assert account.options == options
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]
    assert kwargs_options.gcp_region_name == options["gcp_region_name"]


@pytest.mark.test_group("core-slow-group-12")
def test__parse_gcp_creds_missing_project_id(cloud, sample_user, mocker):
    reqed_keys = [
        "type",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    with pytest.raises(GCPCredentialsError) as e:
        _parse_gcp_creds(
            gcp_service_creds_file=None, gcp_service_creds_dict=gcp_service_creds_dict
        )
    error_message = e.value.args[0]
    assert error_message.startswith(
        "Unable to find 'project_id' in 'gcp_service_creds_dict'"
    )


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gcp_vm_customer_hosted_gar_registry(
    cloud, sample_user, mocker
):

    account = sample_user.account

    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )
    mocker.patch(
        "software_environments.registry.gcp",
        mock.AsyncMock(),
    )

    reqed_keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    coiled.set_backend_options(
        backend="gcp",
        create_vpc=True,
        gcp_service_creds_dict=gcp_service_creds_dict,
        gcp_project_name="test-project-name",
        gcp_region="gcp_region_name",
        gcp_zone="gcp_zone_name",
        registry_type="gar",
    )
    account.refresh_from_db()

    options = {
        "provider_name": "gcp",
        "type": "gcp_cloudbridge_backend_options",
        "gcp_project_name": "test-project-name",
        "gcp_region_name": "gcp_region_name",
        "gcp_zone_name": "gcp_zone_name",
        "gcp_service_creds_dict": gcp_service_creds_dict,
    }
    assert account.options == options
    assert account.container_registry == {
        "type": ContainerRegistryType.GAR,
        "credentials": gcp_service_creds_dict,
        "project_id": "test-project-name",
        "location": "gcp_region_name",
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]
    assert kwargs_options.gcp_region_name == options["gcp_region_name"]


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_gar_registry_validation(cloud, mocker):
    mocker.patch("coiled.utils.boto3")
    mocker.patch("backends.cloudbridge.cloudbridge.ClusterManager._configure_backend")
    credentials = {
        "aws_access_key_id": "test-aws_access_key_id",
        "aws_secret_access_key": "test-aws_secret_access_key",
    }
    reqed_keys = [
        "type",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    with pytest.raises(GCPCredentialsError) as e:
        coiled.set_backend_options(
            gcp_service_creds_dict=gcp_service_creds_dict,
            # These are required for GAR
            # gcp_project_name="test-project-name",
            # gcp_region_name="gcp_region_name",
            registry_type="gar",
            **credentials,
        )
    error_message = e.value.args[0]
    assert error_message.startswith(
        "Unable to find 'project_id' in 'gcp_service_creds_dict'"
    )

    with pytest.raises(GCPCredentialsParameterError) as e:
        coiled.set_backend_options(
            backend="gcp",
            create_vpc=True,
            # Required for GAR, but error is different because
            # it happens earlier.
            # gcp_service_creds_dict=gcp_service_creds_dict,
            gcp_project_name="test-project-name",
            gcp_region="gcp_region_name",
            registry_type="gar",
            **credentials,
        )
    error_message = e.value.args[0]
    assert (
        "Parameter 'gcp_service_creds_file' or 'gcp_service_creds_dict' must be supplied"
        in error_message
    )


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_handle_exception_in_configure_backend(
    cloud, sample_user, mocker
):

    account = sample_user.account

    assert account.options == {}

    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == settings.DEFAULT_CLUSTER_BACKEND

    configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )
    configure_backend_mock.side_effect = Exception("boom something broke")

    rollback_failed_configure_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager.rollback_failed_configure"
    )

    reqed_keys = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]

    gcp_service_creds_dict = {k: "token" for k in reqed_keys}

    with pytest.raises(ServerError):
        coiled.set_backend_options(
            backend="gcp",
            create_vpc=True,
            gcp_service_creds_dict=gcp_service_creds_dict,
            gcp_project_name="test-project-name",
            gcp_region="gcp_region_name",
        )
    account.refresh_from_db()
    assert account.options == {}

    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == settings.DEFAULT_CLUSTER_BACKEND
    assert rollback_failed_configure_mock.called


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_azure_vm_missing_params(
    cloud,
    sample_user,
):
    account = sample_user.account

    # region selection not yet set up in BE
    coiled.set_backend_options(backend="azure")
    account.refresh_from_db()

    assert account.options == {"azure_region_name": settings.AZURE_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AZURE

    with pytest.raises(AzureCredentialsParameterError) as e_info:
        coiled.set_backend_options(backend="azure", create_vpc=True)
    assert "Missing Azure parameters" in str(e_info)


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_azure_vm_customer_hosted(cloud, sample_user, mocker):

    account = sample_user.account

    _configure_backend_mock = mocker.patch(
        "backends.cloudbridge.cloudbridge.ClusterManager._configure_backend"
    )

    azure_backend_options = {
        "azure_resource_group": "nathan_test_01_resource_group",
        "azure_client_id": "86*******",
        "azure_secret": "XL_*****",
        "azure_subscription_id": "0223*****",
        "azure_tenant": "285*****",
    }

    coiled.set_backend_options(
        backend="azure",
        create_vpc=True,
        **azure_backend_options,
    )
    account.refresh_from_db()

    options = {
        "provider_name": "azure",
        "type": "azure_cloudbridge_backend_options",
        "azure_region_name": settings.AZURE_DEFAULT_USER_REGION,
        "credentials": {
            "aws_access_key_id": "",
            "aws_secret_access_key": "",
            "azure_secret": "XL_*****",
            "azure_subscription_id": "0223*****",
            "azure_tenant": "285*****",
        },
        "azure_client_id": "86*******",
        "azure_resource_group": "nathan_test_01_resource_group",
    }

    assert account.options == options
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM
    assert _configure_backend_mock.called

    kwargs = _configure_backend_mock.call_args.kwargs

    kwargs_user_info = kwargs["user_info"]
    kwargs_options = kwargs["options"]

    assert kwargs_user_info.user_id == sample_user.user.id
    assert kwargs_user_info.account_slug == account.slug
    assert kwargs_options.type == options["type"]


### TEST backend_options_registries


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_ecr_no_credentials(
    cloud,
    sample_user,
):
    # TODO What am I missing for set up?
    account = sample_user.account

    credentials = {}

    coiled.set_backend_options(registry_type="ecr", **credentials)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": credentials,
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_ecr(cloud, sample_user, mocker):
    # pytest installs the coiled client
    mocker.patch("coiled.utils.boto3")
    account = sample_user.account

    coiled.set_backend_options(registry_type="ecr")

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}
    assert account.container_registry == {
        "type": ContainerRegistryType.ECR,
        "credentials": {},
        "public_ecr": False,
        "region": settings.AWS_DEFAULT_USER_REGION,
    }
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_dockerhub(
    cloud,
    sample_user,
):
    account = sample_user.account

    registry = {
        "type": ContainerRegistryType.DOCKER_HUB,
        "namespace": "registry_namespace",
        "access_token": "registry_access_token",
        "uri": "registry_uri",
        "username": "registry_username",
    }
    kwargs = {f"registry_{k}": v for k, v in registry.items()}

    coiled.set_backend_options(**kwargs)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}

    registry["account"] = registry["namespace"]
    registry["password"] = registry["access_token"]
    del registry["namespace"]
    del registry["access_token"]

    assert account.container_registry == registry
    assert account.backend == types.BackendChoices.VM_AWS

    ## test use register_username if not registry_namespace
    registry = {
        "type": ContainerRegistryType.DOCKER_HUB,
        "access_token": "registry_access_token",
        "uri": "registry_uri",
        "username": "registry_username",
    }
    kwargs = {f"registry_{k}": v for k, v in registry.items()}

    coiled.set_backend_options(**kwargs)

    account.refresh_from_db()

    assert account.options == {"aws_region_name": settings.AWS_DEFAULT_USER_REGION}

    registry["account"] = registry["username"]
    registry["password"] = registry["access_token"]
    del registry["access_token"]
    assert account.container_registry == registry
    assert account.backend == types.BackendChoices.VM_AWS


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_dockerhub_required_fields(
    cloud,
    sample_user,
):

    registry = {
        "type": ContainerRegistryType.DOCKER_HUB,
        "namespace": "registry_namespace",
        "access_token": "registry_access_token",
        "uri": "registry_uri",
    }
    kwargs = {f"registry_{k}": v for k, v in registry.items()}

    with pytest.raises(RegistryParameterError) as e_info:
        coiled.set_backend_options(**kwargs, registry_username="UpperCasedUserName")
    assert "Your dockerhub [registry_username] must be lowercase" in str(e_info)

    with pytest.raises(RegistryParameterError) as e_info:
        coiled.set_backend_options(**kwargs)
    assert (
        "For setting your registry credentials, these fields cannot be empty: ['registry_username']"
        in str(e_info)
    )


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_acr(cloud, sample_user, mocker):
    account = sample_user.account
    assert account.options == {}
    mocker.patch("backends.cloudbridge.cloudbridge.ClusterManager._configure_backend")
    credentials = {
        "azure_resource_group": "my-resource-group",
        "azure_client_id": "client-id",
        "azure_secret": "client-secret",
        "azure_subscription_id": "subscription-id",
        "azure_tenant": "tenant-id",
    }
    location = "eastus"

    coiled.set_backend_options(
        backend="azure",
        create_vpc=True,
        azure_region=location,
        registry_type="acr",
        **credentials,
    )
    account.refresh_from_db()

    options = {
        "provider_name": "azure",
        "type": "azure_cloudbridge_backend_options",
        "azure_region_name": location,
        "credentials": {
            "aws_access_key_id": "",
            "aws_secret_access_key": "",
            "azure_secret": credentials["azure_secret"],
            "azure_subscription_id": credentials["azure_subscription_id"],
            "azure_tenant": credentials["azure_tenant"],
        },
        "azure_client_id": credentials["azure_client_id"],
        "azure_resource_group": credentials["azure_resource_group"],
    }
    registry = {
        "type": ContainerRegistryType.ACR,
        "credentials": credentials,
        "location": location,
    }
    assert account.options == options
    assert account.container_registry == registry


@pytest.mark.test_group("core-slow-group-12")
def test_set_backend_options_registry_acr_validation(cloud, sample_user, mocker):
    account = sample_user.account
    assert account.options == {}
    mocker.patch("backends.cloudbridge.cloudbridge.ClusterManager._configure_backend")
    credentials = {
        "azure_resource_group": "my-resource-group",
        "azure_client_id": "client-id",
        "azure_secret": "client-secret",
        "azure_subscription_id": "subscription-id",
        "azure_tenant": "tenant-id",
    }
    location = "eastus"

    with pytest.raises(AzureCredentialsParameterError) as e:
        coiled.set_backend_options(
            backend="azure",
            create_vpc=True,
            azure_region=location,
            registry_type="acr",
            # Required
            # **credentials,
        )
    error_message = e.value.args[0]
    for k in credentials.keys():
        assert k in error_message

    with pytest.raises(Exception) as e:
        coiled.set_backend_options(
            backend="azure",
            create_vpc=True,
            azure_region="im_an_invalid_region",
            registry_type="acr",
            **credentials,
        )
    error_message = e.value.args[0]
    assert "not a supported Azure region" in error_message


@pytest.mark.asyncio
@pytest.mark.timeout(600)
@pytest.mark.test_group("test_env_from_software_env")
async def test_env_from_software_env(sample_user, backend, cleanup):
    account = sample_user.user.username
    name = "foo"
    full_name = f"{account}/{name}"
    conda_env = {
        "channels": ["defaults", "conda-forge"],
        "dependencies": ["python=3.8", "dask=2021.5.0", "distributed=2021.5.0"],
    }
    environ = {"MY_TESTING_ENV": "VAL"}
    async with coiled.Cloud(account=account, asynchronous=True) as cloud:
        await cloud.create_software_environment(
            full_name, conda=conda_env, environ=environ
        )
        while True:
            if await cloud.list_software_environments():
                break
            await asyncio.sleep(0.5)

        await cloud.create_cluster_configuration(
            name=full_name,
            software=full_name,
            worker_cpu=1,
            worker_memory="2 GiB",
            scheduler_cpu=1,
            scheduler_memory="2 GiB",
        )
        async with coiled.Cluster(
            n_workers=1,
            configuration=full_name,
            asynchronous=True,
            cloud=cloud,
        ) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)

                def test_env():
                    import os

                    return os.getenv("MY_TESTING_ENV")

                result = await client.run_on_scheduler(test_env)
                assert result == "VAL"
                cluster_result = await client.submit(test_env)
                assert cluster_result == "VAL"
        await cloud.delete_software_environment(full_name)


@pytest.mark.asyncio
@pytest.mark.timeout(600)
@pytest.mark.test_group("test_env_from_softwre_env_override_from_account")
async def test_env_from_softwre_env_override_from_account(
    account_with_env_variables,
    backend,
    cleanup,
):
    user, account, membership = account_with_env_variables
    async with coiled.Cloud(account=account.slug, asynchronous=True) as cloud:
        conda_env = {
            "channels": ["defaults", "conda-forge"],
            "dependencies": ["python=3.8", "dask=2021.5.0", "distributed=2021.5.0"],
        }
        environ = {"MY_TESTING_ENV": "VAL"}

        await cloud.create_software_environment(
            name="soft_env", conda=conda_env, environ=environ
        )
        while True:
            if await cloud.list_software_environments():
                break
            await asyncio.sleep(0.5)

        await cloud.create_cluster_configuration(
            account=account.slug,
            name="env",
            software="soft_env",
            worker_cpu=1,
            worker_memory="2 GiB",
            scheduler_cpu=1,
            scheduler_memory="2 GiB",
        )
        async with coiled.Cluster(
            n_workers=1,
            configuration=f"{account.slug}/env",
            asynchronous=True,
            cloud=cloud,
            account=account.slug,
        ) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)

                def test_env():
                    import os

                    return os.getenv("MY_TESTING_ENV")

                cluster_result = await client.submit(test_env)
                assert cluster_result == "env_variable"
                result = await client.run_on_scheduler(test_env)
                assert result == "env_variable"

        await cloud.delete_software_environment("soft_env")


@pytest.mark.asyncio
@pytest.mark.timeout(600)
@pytest.mark.test_group("core-slow-group-11")
async def test_env_from_account_override_from_runtime(
    account_with_env_variables,
    backend,
    cleanup,
):
    user, account, membership = account_with_env_variables
    async with coiled.Cloud(account=account.slug, asynchronous=True) as cloud:
        await cloud.create_software_environment(
            name="soft_env",
            container=DASKDEV_IMAGE,
        )
        await cloud.create_cluster_configuration(
            account=account.slug,
            name="env",
            software="soft_env",
            worker_cpu=1,
            worker_memory="2 GiB",
            scheduler_cpu=1,
            scheduler_memory="2 GiB",
        )
        environ = {"MY_TESTING_ENV": "VAL"}
        async with coiled.Cluster(
            n_workers=1,
            asynchronous=True,
            configuration="env",
            cloud=cloud,
            account=account.slug,
            environ=environ,
        ) as cluster:
            async with Client(cluster, asynchronous=True) as client:
                await client.wait_for_workers(1)

                def test_env():
                    import os

                    return os.getenv("MY_TESTING_ENV")

                cluster_result = await client.submit(test_env)
                assert cluster_result == "VAL"
                result = await client.run_on_scheduler(test_env)
                assert result == "VAL"


@pytest.mark.skip(reason="Under development")
@pytest.mark.test_group("slow")
@pytest.mark.asyncio
async def test_adaptive_vanilla(cloud, cleanup, cluster_configuration):
    """
    This test verifies that the adaptive scaling works in principle. Once load
    is put on the scheudler, the adaptive_target should increase and the control
    loop shoud initiate upscaling on the backend.

    Note about flakyness: This test might observe some flakyness since it is a
    timing sensitive issue and depends on request roundtrips and various
    """
    # TODO: Adaptive currently raises a lot of errors if the requested resources
    # is beyond the user limit. This should be captured in a dedicated test and
    # treated gracefully without spamming logs, especially not exceptions

    timeout = 120
    num_tasks = 500
    async with coiled.Cluster(
        n_workers=1,
        cloud=cloud,
        configuration=cluster_configuration,
        asynchronous=True,
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:

            num_workers_start = len(cluster.scheduler_info["workers"])

            def sleep(x):
                import time

                time.sleep(0.1)
                return x

            futs = client.map(sleep, range(num_tasks))
            # This starts a PC which _should_ adapt the workers dynamically

            start = time.time()
            cluster.adapt(maximum=5, target_duration="1s")

            while len(cluster.scheduler_info["workers"]) <= num_workers_start:

                if time.time() - start > timeout:
                    raise AssertionError(
                        f"Adaptive cluster didn't scale up after {timeout}s. "
                        "Known workers {cluster.scheduler_info['workers']}"
                    )

                await asyncio.sleep(0.1)

            res = await client.gather(futs)
            assert sum(res) == sum(range(num_tasks))
            del futs
            num_workers_after = len(cluster.scheduler_info["workers"])
            await asyncio.sleep(2)

            start = time.time()
            while len(cluster.scheduler_info["workers"]) >= num_workers_after:

                if time.time() - start > timeout:
                    raise AssertionError(
                        f"Adaptive cluster didn't scale down after {timeout}s. "
                        f"Known workers {cluster.scheduler_info['workers']}"
                    )

                await asyncio.sleep(0.1)


@pytest.mark.test_group("slow")
@pytest.mark.asyncio
async def test_recommendations_scale_up_and_down(cloud, cleanup, cluster_configuration):
    async with coiled.Cluster(
        n_workers=1,
        cloud=cloud,
        configuration=cluster_configuration,
        asynchronous=True,
    ) as cluster:
        timeout = 60
        async with Client(cluster, asynchronous=True) as client:
            await client.wait_for_workers(1)
            await cluster.scale_up(5)
            assert len(cluster.requested) > len(cluster.observed)
            assert len(cluster.requested) == 5
            await client.wait_for_workers(5, timeout=5 * 60)
            assert len(cluster.requested) == len(cluster.observed)
            recommendations = await cluster.recommendations(1)
            status = recommendations.pop("status")
            assert status == "down"
            await cluster.scale_down(**recommendations)
            start = time.time()
            assert len(cluster.requested) <= len(cluster.observed)
            while len(cluster.observed) > 1:
                if time.time() - start > timeout:
                    raise AssertionError("Couldn't scale down")
                await asyncio.sleep(0.5)


def test_parse_gcp_creds_parameter_missing():
    with pytest.raises(GCPCredentialsParameterError):
        _parse_gcp_creds(gcp_service_creds_dict=None, gcp_service_creds_file="")


def test_parse_gcp_creds_not_file():
    with pytest.raises(GCPCredentialsError):
        _parse_gcp_creds(
            gcp_service_creds_dict=None, gcp_service_creds_file="non_existent"
        )


def test_parse_gcp_creds_bad_file(mocker, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")
    mocker.mock_open(read_data="test").return_value = ""
    with pytest.raises(GCPCredentialsError):
        result = _parse_gcp_creds(
            gcp_service_creds_dict=None, gcp_service_creds_file=test_file
        )
        assert "not a valid JSON file" in result


def test_parse_gcp_creds_missing_all_keys(mocker, tmp_path):
    test_file = tmp_path / "test.json"
    test_file.write_text("test")
    mocker.patch("json.load").return_value = {}

    with pytest.raises(GCPCredentialsError) as error:
        _parse_gcp_creds(gcp_service_creds_dict=None, gcp_service_creds_file=test_file)

    assert "is missing the keys" in str(error.value)


def test_parse_gcp_creds_missing_project_id(mocker, tmp_path):
    test_file = tmp_path / "test.json"
    test_file.write_text("test")
    mocker.patch("json.load").return_value = {
        "type": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_x509_cert_url": "",
    }

    with pytest.raises(GCPCredentialsError) as error:
        _parse_gcp_creds(gcp_service_creds_dict=None, gcp_service_creds_file=test_file)

    assert "is missing the keys" in str(error.value)
    assert "project_id" in str(error.value)
