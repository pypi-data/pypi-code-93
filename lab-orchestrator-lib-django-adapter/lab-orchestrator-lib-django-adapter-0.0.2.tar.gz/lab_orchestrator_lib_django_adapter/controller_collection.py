"""
This module contains two methods as shorthands for creating a controller collection that can be used within django
projects.

These controllers can be used in your project to create, read and update resources of the lab orchestrator lib. But
you don't always need to use the methods of the controllers. For example if you want to create or delete a new lab
instance you must use the controller, because the controller has a special implementation of the create and delete
method. In the opposite you don't need to use the controller to retrieve and list a DockerImage or Lab. If you always
use the controller methods you are save, if you don't want to do this you need to read the docs of the controllers.
"""

from django.conf import settings
from lab_orchestrator_lib.controller.controller_collection import create_controller_collection, ControllerCollection
from lab_orchestrator_lib.kubernetes.api import APIRegistry
from lab_orchestrator_lib.kubernetes.config import get_development_config, get_kubernetes_config, get_registry, \
    KubernetesConfig

from lab_orchestrator_lib_django_adapter.adapter import UserDjangoAdapter, LabInstanceDjangoAdapter, LabDjangoAdapter, \
    DockerImageDjangoAdapter


def create_django_controller_collection(registry: APIRegistry, secret_key: str):
    """Creates a controller collection with the django adapters injected.

    :param registry: APIRegistry that is injected into the controllers.
    :param secret_key: The secret key that is used to generate the jwt token.

    :returns: A controller collection that can be used within django projects.
    """
    user_adapter = UserDjangoAdapter()
    docker_image_adapter = DockerImageDjangoAdapter()
    lab_adapter = LabDjangoAdapter()
    lab_instance_adapter = LabInstanceDjangoAdapter()
    return create_controller_collection(
        registry=registry,
        user_adapter=user_adapter,
        docker_image_adapter=docker_image_adapter,
        lab_adapter=lab_adapter,
        lab_instance_adapter=lab_instance_adapter,
        secret_key=secret_key,
    )


def get_default_cc(kubernetes_config: KubernetesConfig = None, registry: APIRegistry = None,
                   controller_collection: ControllerCollection = None, secret_key: str = None):
    """Creates a default controller collection for django projects.

    This method needs to be run in a django project and the settings file should to contain the following variables:
    - `SECRET_KEY`: The secret key that should be used to generate jwt tokens.
    - `DEVELOPMENT`: If this is true, the development mode will be used for kubernetes (no cacert, ignore certs, localhost...)

    This method will create a default KubernetesConfig and APIRegistry and controller collection for django projects,
    but everyone of this default objects can be overwritten by passing in the specific key value pair.

    :param kubernetes_config: Overwrites the default kubernetes config. If None the default is used.
    :param registry: Overwrites the default registry. If None the default is used.
    :param controller_collection: Overwrites the default controller collection. If None the default is used.
    :param secret_key: Overwrites the default secret key. If None the default secret key from settings is used.

    :returns: A controller collection that can be used within django projects.
    """
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    if kubernetes_config is None:
        if settings.DEVELOPMENT:
            kubernetes_config = get_development_config()
        else:
            kubernetes_config = get_kubernetes_config()
    if registry is None:
        registry = get_registry(kubernetes_config)
    if controller_collection is None:
        return create_django_controller_collection(registry, secret_key)
    return controller_collection
