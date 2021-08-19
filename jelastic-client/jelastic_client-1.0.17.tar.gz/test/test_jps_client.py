import os

import pytest

from jelastic_client import ControlClient, JpsClient
from jelastic_client.core.exceptions import JelasticClientException


def test_jps_client_install_valid_manifest_creates_environment(
        control_client: ControlClient,
        jps_client: JpsClient,
        test_data_dir: str,
        new_env_name: str):
    # Arrange
    filename = os.path.join(test_data_dir, "valid_manifest.jps")

    # Act
    jps_client.install(filename, new_env_name)

    # Assert
    assert control_client.env_exists(new_env_name)


def test_jps_client_install_valid_manifest_makes_environment_run(
        control_client: ControlClient,
        jps_client: JpsClient,
        test_data_dir: str,
        new_env_name: str):
    # Arrange
    filename = os.path.join(test_data_dir, "valid_manifest.jps")

    # Act
    jps_client.install(filename, new_env_name)

    # Assert
    assert control_client.env_is_running(new_env_name)


def test_jps_client_install_invalid_manifest_raises_exception(
        jps_client: JpsClient,
        test_data_dir: str,
        new_env_name: str):
    # Arrange
    filename = os.path.join(test_data_dir, "invalid_manifest.jps")

    # Act / Assert
    with pytest.raises(JelasticClientException):
        jps_client.install(filename, new_env_name)


def test_jps_client_get_engine_version_returns_supported_engine_version(
        jps_client: JpsClient,
        supported_jelastic_version: str):
    # Arrange

    # Act
    actual_version = jps_client.get_engine_version()

    # Assert
    assert supported_jelastic_version == actual_version
