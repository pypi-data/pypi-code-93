import os
import time
from typing import Dict

import docker  # type: ignore

from tktl.commands.health import GetGrpcHealthCommand, GetRestHealthCommand
from tktl.core.config import settings
from tktl.core.exceptions.exceptions import APIClientException, MissingDocker
from tktl.core.loggers import LOG, MUTE_LOG

TESTING_DOCKERFILE = "Dockerfile.taktile-cli-testing"
MULTI_STAGE_BUILD_STEP_NAME = "build_step"


class DockerManager:
    def __init__(self, path):
        try:
            self._client = docker.from_env()
            self._path = path
        except docker.errors.DockerException as err:
            raise MissingDocker from err

    def get_docker_file(self) -> str:
        with open(os.path.join(self._path, ".buildfile")) as fp:
            return fp.read()

    def stream_logs(self, container) -> None:
        for line in container.logs(stream=True):
            LOG.log(f"> {line.decode()}".strip())

    def _patch_docker_file(
        self, input_docker_file: str = ".buildfile", output: str = TESTING_DOCKERFILE
    ):
        """patch_docker_file

        Remove kaniko related config
        """
        with open(os.path.join(self._path, input_docker_file)) as fp:
            lines = fp.readlines()
            desired_contents = []
            for line in lines:
                if line.startswith("ARG RESOURCE_NAME"):
                    break
                desired_contents.append(line)

        with open(os.path.join(self._path, output), "w") as fp:
            fp.writelines(desired_contents)

    @staticmethod
    def _is_multi_stage(file_path: str) -> bool:
        with open(file_path) as fp:
            lines = fp.readlines()
            return any(
                x.startswith(f"FROM {MULTI_STAGE_BUILD_STEP_NAME}") for x in lines
            )

    def _remove_patched_docker_file(self, file_path: str = TESTING_DOCKERFILE):
        os.remove(os.path.join(self._path, file_path))

    def remove_image(self, image):
        self._client.images.remove(image, force=True)

    def build_image(
        self, dockerfile: str, nocache: bool = False, buildargs: Dict = None
    ) -> str:

        if nocache:
            try:
                image = self._client.images.get("taktile-cli-test:latest")
                self._client.images.remove(image.id)
            except docker.errors.ImageNotFound:
                pass

        # TODO: After phasing out support for non multistage docker files, remove this.
        if DockerManager._is_multi_stage(dockerfile):
            LOG.log(
                f"Multistage dockerfile, building target {MULTI_STAGE_BUILD_STEP_NAME}..."
            )
            image, stream = self._client.images.build(
                path=self._path,
                dockerfile=dockerfile,
                tag="taktile-cli-test",
                nocache=nocache,
                target=MULTI_STAGE_BUILD_STEP_NAME,
                buildargs=buildargs,
                forcerm=True,
            )
        else:
            LOG.log("Patching dockerfile...")
            self._patch_docker_file(
                input_docker_file=dockerfile, output=TESTING_DOCKERFILE
            )
            image, stream = self._client.images.build(
                path=self._path,
                dockerfile=TESTING_DOCKERFILE,
                tag="taktile-cli-test",
                nocache=nocache,
                forcerm=True,
            )
            self._remove_patched_docker_file()

        for chunk in stream:
            if "stream" in chunk:
                for line in chunk["stream"].splitlines():
                    LOG.trace("> " + line)

        return image.id

    def test_import(self, image_id: str):
        client_name = "tktl" if not settings.FUTURE_ENDPOINTS else "client"
        command = f"python -c 'from src.endpoints import {client_name}'"
        try:
            container = self._client.containers.run(image_id, command, detach=True,)
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def test_unittest(self, image_id: str):
        try:
            container = self._client.containers.run(
                image_id, "python -m pytest ./user_tests/", detach=True
            )
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def run_rest_container(
        self, image_id: str, detach: bool = True, auth_enabled: bool = True
    ):
        return self._client.containers.run(
            image_id,
            detach=detach,
            entrypoint="/start-rest.sh",
            environment={"AUTH_ENABLED": auth_enabled},
            ports={"80/tcp": 8080},
            remove=True,
            stderr=True,
            stdout=True,
        )

    def run_arrow_container(
        self, image_id: str, detach: bool = True, auth_enabled: bool = True
    ):
        return self._client.containers.run(
            image_id,
            detach=detach,
            entrypoint="/start-flight.sh",
            environment={"AUTH_ENABLED": auth_enabled},
            ports={"5005/tcp": 5005},
            remove=True,
            stderr=True,
            stdout=True,
        )

    def run_containers(
        self, image_id: str, detach: bool = True, auth_enabled: bool = True
    ):
        arrow_container = self.run_arrow_container(
            image_id=image_id, detach=detach, auth_enabled=auth_enabled
        )
        rest_container = self.run_rest_container(
            image_id=image_id, detach=detach, auth_enabled=auth_enabled
        )
        return arrow_container, rest_container

    def run_profiling_container(self):
        try:
            container = self._client.containers.run(
                "taktile/taktile-profiler:latest",
                entrypoint="profiler profile -l",
                network_mode="host",
                detach=True,
            )
            self.stream_logs(container)
            status = container.wait()
            return status, container
        finally:
            container.remove()

    def run_and_check_health(
        self,
        image_id: str,
        kill_on_success: bool = False,
        auth_enabled: bool = True,
        timeout: int = 7,
        retries: int = 7,
    ):
        arrow_container, rest_container = self.run_containers(
            image_id=image_id, detach=True, auth_enabled=auth_enabled
        )
        grpc_health_cmd = GetGrpcHealthCommand(
            branch_name="",
            repository="",
            local=True,
            logger=MUTE_LOG if not LOG.VERBOSE else LOG,
            skip_auth=True,
        )
        rest_health_cmd = GetRestHealthCommand(
            branch_name="",
            repository="",
            local=True,
            logger=MUTE_LOG if not LOG.VERBOSE else LOG,
            skip_auth=True,
        )

        try:
            for _ in range(retries):
                try:
                    time.sleep(timeout)
                    rest_response = rest_health_cmd.execute()
                    grpc_response = grpc_health_cmd.execute()
                    return rest_response, grpc_response, arrow_container, rest_container
                except (APIClientException, Exception):
                    pass

            return None, None, arrow_container, rest_container
        finally:
            if kill_on_success:
                arrow_container.kill()
                rest_container.kill()
