from lab_orchestrator_lib.controller.controller_collection import create_controller_collection
from lab_orchestrator_lib.kubernetes.api import APIRegistry
from lab_orchestrator_lib_django_adapter.adapter import UserDjangoAdapter, LabInstanceDjangoAdapter, LabDjangoAdapter, \
    DockerImageDjangoAdapter


def create_django_controller_collection(registry: APIRegistry):
    user_adapter = UserDjangoAdapter()
    docker_image_adapter = DockerImageDjangoAdapter()
    lab_adapter = LabDjangoAdapter()
    lab_instance_adapter = LabInstanceDjangoAdapter()
    return create_controller_collection(
        registry=registry,
        user_adapter=user_adapter,
        docker_image_adapter=docker_image_adapter,
        lab_adapter=lab_adapter,
        lab_instance_adapter=lab_instance_adapter
    )
