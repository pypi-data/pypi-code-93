import pytest

from jelastic_client import ControlClient, EnvNode, EnvSettings, DockerSettings
from jelastic_client.core import JelasticClientException


def test_control_client_delete_non_existent_environment_raises_exception(
        control_client: ControlClient,
        non_existent_env_name: str):
    # Arrange

    # Act / Assert
    with pytest.raises(JelasticClientException):
        control_client.delete_env(non_existent_env_name)


def test_control_client_create_environment_with_single_vps_node_runs_environment(
        control_client: ControlClient,
        new_env_name: str):
    # Arrange
    env = EnvSettings(shortdomain=new_env_name)
    node = EnvNode(flexibleCloudlets=4, nodeType="ubuntu-vps")

    # Act
    actual_env_name = control_client.create_environment(env, [node])

    # Assert
    assert new_env_name == actual_env_name
    assert control_client.env_is_running(new_env_name)


def test_control_client_create_environment_with_single_sql_node_runs_environment(
        control_client: ControlClient,
        new_env_name: str):
    # Arrange
    env = EnvSettings(shortdomain=new_env_name)
    # postgres needs at least 3 cloudlets
    node = EnvNode(fixedCloudlets=3, flexibleCloudlets=4,
                   nodeType="postgresql")

    # Act
    actual_env_name = control_client.create_environment(env, [node])

    # Assert
    assert new_env_name == actual_env_name
    assert control_client.env_is_running(new_env_name)


def test_control_client_create_environment_with_single_docker_node_runs_environment(
        control_client: ControlClient,
        new_env_name: str):
    # Arrange
    env = EnvSettings(shortdomain=new_env_name)
    docker_settings = DockerSettings(image="alpine")
    node = EnvNode(docker=docker_settings,
                   flexibleCloudlets=4, nodeType="docker")

    # Act
    actual_env_name = control_client.create_environment(env, [node])

    # Assert
    assert new_env_name == actual_env_name
    assert control_client.env_is_running(new_env_name)


def test_control_client_create_environment_with_multiple_nodes_runs_environment(
        control_client: ControlClient,
        new_env_name: str):
    # Arrange
    env = EnvSettings(shortdomain=new_env_name)
    # postgres needs at least 3 cloudlets
    sql_node = EnvNode(fixedCloudlets=3, flexibleCloudlets=4,
                       nodeType="postgresql")
    docker_settings = DockerSettings(image="alpine")
    docker_node = EnvNode(docker=docker_settings,
                          flexibleCloudlets=4, nodeType="docker")

    # Act
    actual_env_name = control_client.create_environment(
        env, [sql_node, docker_node])

    # Assert
    assert new_env_name == actual_env_name
    assert control_client.env_is_running(new_env_name)
