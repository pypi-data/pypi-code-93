import os
import sys
import uuid
from typing import List

import docker
from dagster import Array, Field, check
from dagster.core.events import DagsterEvent
from dagster.core.executor.step_delegating.step_handler.base import StepHandler, StepHandlerContext
from dagster.core.host_representation.grpc_server_registry import GrpcServerEndpoint
from dagster.core.launcher import DefaultRunLauncher
from dagster.daemon.daemon import get_default_daemon_logger
from dagster.serdes import ConfigurableClass, serialize_dagster_namedtuple
from dagster.serdes.utils import create_snapshot_id
from dagster.utils import find_free_port, merge_dicts

from .user_code_launcher import ReconcileUserCodeLauncher

GRPC_SERVER_LABEL = "dagster_grpc_server"


class DockerUserCodeLauncher(ReconcileUserCodeLauncher, ConfigurableClass):
    def __init__(
        self,
        inst_data=None,
        networks=None,
        env_vars=None,
    ):
        self._inst_data = inst_data
        self._logger = get_default_daemon_logger("DockerUserCodeLauncher")
        self._networks = check.opt_list_param(networks, "networks", of_type=str)
        self._env_vars = env_vars

        super(DockerUserCodeLauncher, self).__init__()

    def start(self):
        super().start()
        self._cleanup_containers()

    @property
    def inst_data(self):
        return self._inst_data

    @classmethod
    def config_type(cls):
        return {
            "networks": Field(Array(str), is_required=False),
            "env_vars": Field(
                [str],
                is_required=False,
                description="The list of environment variables names to forward to the docker container",
            ),
        }

    @staticmethod
    def from_config_value(inst_data, config_value):
        return DockerUserCodeLauncher(inst_data=inst_data, **config_value)

    def _create_container(self, client, location_name, metadata, container_name, hostname, port):

        python_env = (
            {"DAGSTER_CLI_API_GRPC_PYTHON_FILE": metadata.python_file}
            if metadata.python_file
            else {"DAGSTER_CLI_API_GRPC_PACKAGE_NAME": metadata.package_name}
        )
        return client.containers.create(
            metadata.image,
            detach=True,
            hostname=hostname,
            name=container_name,
            network=self._networks[0] if len(self._networks) else None,
            environment=merge_dicts(
                (
                    {env_name: os.getenv(env_name) for env_name in self._env_vars}
                    if self._env_vars
                    else {}
                ),
                {
                    "DAGSTER_CURRENT_IMAGE": metadata.image,
                    "PYTHONUNBUFFERED": "1",
                    "DAGSTER_CLI_API_GRPC_PORT": str(port),
                    "DAGSTER_CLI_API_GRPC_HOST": "0.0.0.0",
                    "DAGSTER_CLI_API_GRPC_LAZY_LOAD_USER_CODE": "1",
                },
                python_env,
            ),
            labels=[GRPC_SERVER_LABEL, self._get_label_for_metadata(location_name, metadata)],
            command=["dagster", "api", "grpc"],
            ports={port: port} if hostname == "localhost" else None,
        )

    def _get_containers(self, client, location_name, metadata):
        return client.containers.list(
            all=True, filters={"label": self._get_label_for_metadata(location_name, metadata)}
        )

    def _add_server(self, location_name, metadata):
        client = docker.client.from_env()

        # check if the container already exists, remove it if so (could happen
        # if a previous attempt to add the container failed)
        existing_containers = self._get_containers(client, location_name, metadata)
        for existing_container in existing_containers:
            self._logger.info(
                "Removing existing container for location {location_name} with image {image}: {container_name}".format(
                    location_name=location_name,
                    image=metadata.image,
                    container_name=existing_container.name,
                )
            )
            self._remove_container(existing_container)

        return self._start_new_server(location_name, metadata)

    def _start_new_server(self, location_name, metadata):
        client = docker.client.from_env()

        container_name = f"{location_name}_{str(uuid.uuid4().hex)[0:6]}"

        self._logger.info(
            "Starting a new container for location {location_name} with image {image}: {container_name}".format(
                location_name=location_name, image=metadata.image, container_name=container_name
            )
        )

        has_network = len(self._networks) > 0
        if has_network:
            port = 4000
            hostname = container_name
        else:
            port = find_free_port()
            hostname = "localhost"

        try:
            container = self._create_container(
                client, location_name, metadata, container_name, hostname, port
            )
        except docker.errors.ImageNotFound:
            client.images.pull(metadata.image)
            container = self._create_container(
                client, location_name, metadata, container_name, hostname, port
            )

        if len(self._networks) > 1:
            for network_name in self._networks[1:]:
                network = client.networks.get(network_name)
                network.connect(container)

        container.start()

        self._logger.info("Started container {container_id}".format(container_id=container.id))

        server_id = self._wait_for_server(host=hostname, port=port)

        endpoint = GrpcServerEndpoint(
            server_id=server_id,
            host=hostname,
            port=port,
            socket=None,
        )

        return endpoint

    def _gen_update_server(self, location_name, old_metadata, new_metadata):
        client = docker.client.from_env()
        existing_containers = self._get_containers(client, location_name, old_metadata)
        updated_server = self._start_new_server(location_name, new_metadata)
        yield updated_server

        # Now cleanup the old containers
        for existing_container in existing_containers:
            self._logger.info(
                "Removing old container for location {location_name}: {container_name}".format(
                    location_name=location_name,
                    container_name=existing_container.name,
                )
            )
            self._remove_container(existing_container)

    def _get_label_for_metadata(self, location_name, metadata):
        return f"{location_name}_{create_snapshot_id(metadata)[0:6]}"

    def _remove_server(self, location_name, metadata):
        client = docker.client.from_env()
        containers = self._get_containers(client, location_name, metadata)
        for container in containers:
            self._logger.info(
                "Removing a container for location {location_name} with image {image}: {container_name}".format(
                    location_name=location_name,
                    image=container.image,
                    container_name=container.name,
                )
            )

            self._remove_container(container)

    def _remove_container(self, container):
        try:
            container.stop()
        except Exception:  # pylint: disable=broad-except
            self._logger.error(
                "Failure stopping container {container_id}: {exc_info}".format(
                    container_id=container.id,
                    exc_info=sys.exc_info(),
                )
            )
        container.remove(force=True)
        self._logger.info("Removed container {container_id}".format(container_id=container.id))

    def _cleanup_containers(self):
        client = docker.client.from_env()
        # Shut down any dangling containers with the gRPC label
        existing_containers = client.containers.list(all=True, filters={"label": GRPC_SERVER_LABEL})

        for container in existing_containers:
            self._logger.info(
                "Stopping and removing existing gRPC container {container_name}".format(
                    container_name=container.name
                )
            )
            self._remove_container(container)

    def __exit__(self, exception_type, exception_value, traceback):
        self._cleanup_containers()

    def step_handler(self):
        return DockerStepHandler(self._networks, self._env_vars)

    def run_launcher(self):
        launcher = DefaultRunLauncher()
        launcher.register_instance(self._instance)

        return launcher


class DockerStepHandler(StepHandler):
    def __init__(self, networks, env_vars):
        super().__init__()
        self._networks = check.opt_list_param(networks, "networks", of_type=str)
        self._env_vars = check.opt_list_param(env_vars, "env_vars", of_type=str)

    @property
    def name(self) -> str:
        return "DockerStepHandler"

    def _create_step_container(self, client, step_image, execute_step_args):

        return client.containers.create(
            step_image,
            detach=True,
            network=self._networks[0] if len(self._networks) else None,
            command=[
                "dagster",
                "api",
                "execute_step",
                serialize_dagster_namedtuple(execute_step_args),
            ],
            environment=(
                {env_name: os.getenv(env_name) for env_name in self._env_vars}
                if self._env_vars
                else {}
            ),
        )

    def launch_step(self, step_handler_context: StepHandlerContext) -> List[DagsterEvent]:
        client = docker.client.from_env()

        step_image = (
            step_handler_context.execute_step_args.pipeline_origin.repository_origin.container_image
        )

        if not step_image:
            raise Exception("No image included to launch steps: " + str(step_image))

        try:
            step_container = self._create_step_container(
                client, step_image, step_handler_context.execute_step_args
            )
        except docker.errors.ImageNotFound:
            client.images.pull(step_image)
            step_container = self._create_step_container(
                client, step_image, step_handler_context.execute_step_args
            )

        if len(self._networks) > 1:
            for network_name in self._networks[1:]:
                network = client.networks.get(network_name)
                network.connect(step_container)

        step_container.start()
        return []

    def check_step_health(self, step_handler_context: StepHandlerContext) -> List[DagsterEvent]:
        # TODO not implemented
        return []

    def terminate_step(self, step_handler_context: StepHandlerContext) -> List[DagsterEvent]:
        # TODO not implemented
        return []
