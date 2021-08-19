# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contracts for environment override."""
import os
from pathlib import Path
from azureml.core import Workspace, Environment as V1Environment
from ._util._yaml_utils import YAML
from ._core._environment import Environment as CoreEnvironment, Docker as CoreDocker, \
    CondaDependencies as CoreConda
from ._util._exceptions import UserErrorException


class Environment:
    r"""Configure Python environment for running components.

    An Environment defines Docker, Conda and OS settings. An Environment can be initialized from
    a curated AML environment (For more information about curated environments, see `create and manage
    reusable environments <https://docs.microsoft.com/azure/machine-learning/how-to-use-environments>`_),
    or a YAML file which defines environment setting by following
    `environment specs <https://aka.ms/azure-ml-component-environment>`_.

    .. note::

        The following example shows how to create an environment using
        :class:`azure.ml.component.environment.Environment` class:

        .. code-block:: python

            # Create from a curated environment, suppose we have a workspace as 'ws'
            env = Environment(ws, name="AzureML-Minimal")
            # Or use a curated environment with a specific version
            env = Environment(ws, name="AzureML-Minimal", version="19")

            # Create from a YAML file, see below YAML as an example
            env = Environment(file="<path-to-YAML-file>")

        .. code-block:: yaml

            # Sample environment YAML
            environment:
              docker:
                image:  mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04
              conda:
                conda_dependencies:
                  name: project_environment
                  channels:
                  - defaults
                  dependencies:
                  - python=3.6.8
                  - pip=20.0
                  - pip:
                    - azureml-defaults
                    - azureml-dataprep>=1.6
              os: Linux

        .. note::

            If you both set `name` and `file`, only `name` works as it has higher priority.

        For more samples of working with environments, see
        `environment in runsettings <https://aka.ms/azure-ml-component-runsettings#environment>`_.
    """

    def __init__(self, ws: Workspace=None, name: str=None, version: str=None, file: str=None):
        """Initialize environment by (name & version) or file.

        Note that, when `name` has value, `file` will be ignored.

        :param name: The name of the curated environment.
        :param version: The version of the curated environment.
        :param file: The path to the YAML file.
        """
        if name:
            self._env = self._init_from_curated_env(ws, name, version)
        elif file:
            _check_file_value('file', file)
            yaml_dict = _load_yaml_dict_from_file(file)
            if "name" in yaml_dict:
                name = yaml_dict["name"]
                version = yaml_dict.get("version", None)
                self._env = self._init_from_curated_env(ws, name, version)
            else:
                if "docker" in yaml_dict and "build" in yaml_dict["docker"] and \
                        "dockerfile" in yaml_dict["docker"]["build"]:
                    dockerfile = yaml_dict["docker"]["build"]["dockerfile"]
                    yaml_dict["docker"]["base_dockerfile"] = dockerfile

                try:
                    self._env = CoreEnvironment._from_dict(yaml_dict,
                                                           base_dir=Path(file).parent.resolve().as_posix(),
                                                           raise_on_non_exist_error=True)
                except Exception as e:
                    raise UserErrorException(
                        "Failed to initialize environment settings from file '{}'.".format(file)) from e
        else:
            self._env = CoreEnvironment()

    def _init_from_curated_env(self, ws, name, version):
        _check_str_value('name', name)
        if version:  # Version can be None
            if not isinstance(version, str):
                version = str(version)
        if ws is None:
            raise UserErrorException("Workspace cannot be None when using curated environment.")
        # Get curated environment
        try:
            v1_env = V1Environment.get(ws, name=name, version=version)
        except Exception as e:
            raise UserErrorException("Cannot get curated environment by name '{}'{}.".format(
                name, " and version '{}'".format(version) if version else '')) from e
        yaml_dict = {
            "conda": {
                "conda_dependencies": v1_env.python.conda_dependencies._conda_dependencies
            },
            "docker": {
                "image": v1_env.docker.base_image
            },
            "os": v1_env.docker.platform.os
        }
        return CoreEnvironment._from_dict(yaml_dict)

    def _get_docker(self):
        if self._env.docker:
            docker = Docker()
            docker._docker = self._env.docker
            return docker
        return None

    def _get_conda(self):
        if self._env.conda and self._env.conda.conda_dependencies:
            conda = Conda()
            conda._conda = self._env.conda.conda_dependencies
            return conda
        return None

    def _get_os(self):
        return self._env.os


class Docker:
    r"""Docker environment settings for running a component.

    .. note::

        The following example shows how to create a docker environment settings using
        :class:`azure.ml.component.environment.Docker` class:

        .. code-block:: python

            # Create from image
            docker = Docker(image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04")
            # Create from dockerfile
            docker = Docker(file="<path-to-dockerfile>")

        For more details of working with docker, see
        `environment in runsettings
        <https://componentsdk.azurewebsites.net/concepts/runsettings.html#override-partial-environment>`_.
    """

    def __init__(self, image: str=None, file: str=None):
        """
        Create docker settings from image or a dockerfile.

        :param image: docker image
        :type image: str
        :param file: the path to dockerfile
        :type file: str
        """
        if image and file:
            raise UserErrorException("You can set only one of 'image' and 'file', cannot set them both.")
        self._docker = None
        if image:
            _check_str_value('image', image)
            self._docker = CoreDocker._from_dict({
                "image": image
            })
        elif file:
            _check_file_value('file', file)
            self._docker = CoreDocker._from_dockerfile(file)


class Conda:
    r"""Conda environment settings for running a component.

    .. note::

        The following example shows how to create a conda environment settings using
        :class:`azure.ml.component.environment.Conda` class:

        .. code-block:: python

            # Create from pip requirements file
            conda = Conda(pip_requirements_file="<path-to-pip-requirements-file>")
            # Create from conda yaml file
            conda = Conda(conda_file="<path-to-conda-file>")

        For more details of working with conda, see
        `environment in runsettings
        <https://componentsdk.azurewebsites.net/concepts/runsettings.html#override-partial-environment>`_.
    """

    def __init__(self, pip_requirements_file: str=None, conda_file: str=None):
        """
        Create conda settings from  a pip requirement file or a conda yaml file.

        :param pip_requirements_file: the path to pip requirement file
        :type pip_requirements_file: str
        :param conda_file: the path to conda yaml file
        :type conda_file: str
        """
        if pip_requirements_file and conda_file:
            raise UserErrorException(
                "You can set only one of 'pip_requirements_file' and 'conda_file', cannot set them both.")
        self._conda = None
        if pip_requirements_file:
            _check_file_value('pip_requirements_file', pip_requirements_file)
            self._conda = CoreConda._from_pip_requirements_file(pip_requirements_file)
        elif conda_file:
            _check_file_value('conda_file', conda_file)
            try:
                self._conda = CoreConda._from_file(conda_file)
            except Exception as e:
                raise UserErrorException(
                    "Failed to initialize conda settings from file '{}'.".format(conda_file)) from e


def _load_yaml_dict_from_file(file_path):
    with open(file_path) as fin:
        return YAML.safe_load(fin)


def _check_str_value(param_name, value):
    _check_value_type(param_name, value, str)


def _check_file_value(param_name, value):
    _check_value_type(param_name, value, str)
    if not os.path.exists(value):
        raise UserErrorException("File path '{}' does not exist.".format(value))


def _check_value_type(param_name, value, expected_type):
    if not isinstance(value, expected_type):
        raise UserErrorException(
            "Parameter '{}' type mismatched, expected type: '{}', got '{}'.".format(
                param_name, expected_type.__name__, type(value).__name__))
