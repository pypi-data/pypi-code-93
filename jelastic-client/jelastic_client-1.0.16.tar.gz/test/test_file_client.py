from jelastic_client import FileClient


def test_file_client_read_file_from_environment(
        file_client: FileClient,
        alpine_with_file: tuple[str, str],
        expected_file_content_in_alpine_with_file: str):
    # Arrange
    env_name = alpine_with_file[0]
    path_to_file = alpine_with_file[1]

    # Act
    actual_content = file_client.read(
        env_name, path_to_file, node_type="docker")

    # Assert
    assert expected_file_content_in_alpine_with_file.replace(
        "\r", "") == actual_content.replace("\r", "")
