import os
from typing import Dict

from docker.errors import APIError  # type: ignore
from pydantic import ValidationError

from tktl.core.exceptions.exceptions import (
    MissingDocker,
    NoContentsFoundException,
    UserRepoValidationException,
)
from tktl.core.loggers import LOG
from tktl.core.managers.docker import DockerManager
from tktl.core.managers.project import ProjectManager
from tktl.core.schemas.project import ProjectValidationOutput
from tktl.core.validation.outputs import (
    ConfigFileValidationFailure,
    ProjectValidationFailure,
)


def validate_project_config(path: str):
    try:
        ProjectManager.validate_project_config(path)
    except ValidationError as e:
        validation_output = ProjectValidationOutput(
            title=ConfigFileValidationFailure.title,
            summary=ConfigFileValidationFailure.summary,
            text=ConfigFileValidationFailure.format_step_results(validation_errors=e),
        )
        log_failure(validation_output)
        return
    except (NoContentsFoundException, UserRepoValidationException) as e:
        validation_output = ProjectValidationOutput(
            title=ProjectValidationFailure.title,
            summary=ProjectValidationFailure.summary,
            text=ProjectValidationFailure.format_step_results(validation_errors=e),
        )
        log_failure(validation_output)
        return
    LOG.log("Project scaffolding is valid!", color="green")


def log_failure(validation_output: ProjectValidationOutput):
    LOG.log(f"Project scaffolding is invalid: {validation_output.title}", color="red")
    LOG.log(validation_output.summary, color="red", err=True)
    LOG.log(validation_output.text, color="red", err=True)


def build_image(path: str, nocache: bool = False, secrets: Dict[str, str] = None):
    dm = DockerManager(path)
    LOG.log("Building docker image...")
    abs_path = os.path.abspath(os.path.join(path, ".buildfile"))
    image = dm.build_image(dockerfile=abs_path, nocache=nocache, buildargs=secrets)

    return dm, image


def status_output(status):
    if status["StatusCode"] == 0:
        LOG.log("Success", color="green")
    else:
        LOG.log("Error", color="red")
        exit(1)


def validate_import(path: str, nocache: bool, secrets: Dict[str, str] = None):
    try:
        dm, image = build_image(path, nocache=nocache, secrets=secrets)
        LOG.log("Testing import of tktl...")
        status, _ = dm.test_import(image)
        status_output(status)
        if nocache:
            dm.remove_image(image=image)

    except MissingDocker:
        LOG.log(
            "Couldn't locate docker, please make sure it is installed, or use the DOCKER_HOST environment variable",
            color="red",
        )


def validate_unittest(path: str, nocache: bool, secrets: Dict[str, str] = None):
    try:
        dm, image = build_image(path=path, nocache=nocache, secrets=secrets)
        LOG.log("Running unittests...")
        status, _ = dm.test_unittest(image)
        status_output(status)
        if nocache:
            dm.remove_image(image=image)

    except MissingDocker:
        LOG.log(
            "Couldn't locate docker, please make sure it is installed, or use the DOCKER_HOST environment variable",
            color="red",
        )


def validate_integration(
    path: str, nocache: bool, timeout: int, retries: int, secrets: Dict[str, str] = None
):
    try:
        dm, image = build_image(path, nocache=nocache, secrets=secrets)
        LOG.log("Waiting for service to start...")
        (
            rest_response,
            grpc_response,
            arrow_container,
            rest_container,
        ) = dm.run_and_check_health(
            image,
            kill_on_success=True,
            auth_enabled=False,
            timeout=timeout,
            retries=retries,
        )
        if _validate_container_response(
            rest_response=rest_response, grpc_response=grpc_response
        ):
            LOG.log("Success", color="green")
        else:
            LOG.log(
                "Unable to run container. See stack trace for more info", color="red"
            )
            exit(1)
        if nocache:
            dm.remove_image(image=image)

    except MissingDocker:
        LOG.log(
            "Couldn't locate docker, please make sure it is installed, or use the DOCKER_HOST environment variable",
            color="red",
        )


def validate_profiling(
    path: str, nocache: bool, timeout: int, retries: int, secrets: Dict[str, str] = None
):
    try:
        dm, image = build_image(path, nocache=nocache, secrets=secrets)
        LOG.log("Testing profiling...")
        LOG.log("Initiating service...")
        (
            rest_response,
            grpc_response,
            arrow_container,
            rest_container,
        ) = dm.run_and_check_health(
            image,
            kill_on_success=False,
            auth_enabled=False,
            timeout=timeout,
            retries=retries,
        )
        success = _validate_container_response(
            rest_response=rest_response, grpc_response=grpc_response
        )
        if not success:
            LOG.log(
                "Failed to run service container, ensure service can run with `tktl validate integration`",
                color="red",
            )
            exit(1)
        try:
            LOG.log("Initiating remote profiling...")
            status, container = dm.run_profiling_container()
            status_output(status)
            if nocache:
                dm.remove_image(image=container.image.id)
        finally:
            try:
                arrow_container.kill()
                rest_container.kill()
                if nocache:
                    dm.remove_image(image=rest_container.image.id)
                    dm.remove_image(image=arrow_container.image.id)
            except APIError:
                pass

    except MissingDocker:
        LOG.log(
            "Couldn't locate docker, please make sure it is installed, or use the DOCKER_HOST environment variable",
            color="red",
        )


def _validate_rest_response(rest_response):
    if rest_response is None:
        LOG.log("Could not access REST endpoint", color="red")
    elif rest_response.status_code != 204:
        LOG.log(f"Response status code {rest_response.status_code}", color="red")
    else:
        return True
    return False


def _validate_grpc_response(grpc_response):
    if grpc_response is None:
        LOG.log("Could not access gRPC endpoint", color="red")
    else:
        return True
    return False


def _validate_container_response(rest_response, grpc_response):
    return _validate_rest_response(
        rest_response=rest_response
    ) and _validate_grpc_response(grpc_response=grpc_response)


def validate_all(
    path: str, nocache: bool, timeout: int, retries: int, secrets: Dict[str, str] = None
):
    validate_project_config(path)
    validate_import(path, nocache=nocache, secrets=secrets)
    validate_unittest(path, nocache=False, secrets=secrets)
    validate_integration(
        path, nocache=False, timeout=timeout, retries=retries, secrets=secrets
    )
    validate_profiling(
        path, nocache=False, timeout=timeout, retries=retries, secrets=secrets
    )
