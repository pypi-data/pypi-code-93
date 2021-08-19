import os
from typing import Optional
from unittest.mock import ANY, Mock, mock_open as mock_open_factory, patch

import pytest

from anyscale.client.openapi_client import Project, UserInfo
from anyscale.client.openapi_client.models.project_list_response import (
    ProjectListResponse,
)
from anyscale.controllers.project_controller import (
    COMPUTE_CONFIG_FILENAME,
    ProjectController,
)
from anyscale.project import ProjectDefinition


@pytest.fixture()
def mock_api_client(project_test_data: Project) -> Mock:
    mock_api_client = Mock()

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.return_value = ProjectListResponse(
        results=[project_test_data]
    )
    mock_api_client.list_sessions_api_v2_sessions_get.return_value.results = []
    mock_api_client.get_project_latest_cluster_config_api_v2_projects_project_id_latest_cluster_config_get.return_value.result.config = (
        ""
    )

    return mock_api_client


@pytest.mark.parametrize("owner", [None, "owner"])
def test_clone_project(
    project_test_data: Project, mock_api_client: Mock, owner: Optional[str]
) -> None:
    project_controller = ProjectController(
        api_client=mock_api_client, anyscale_client=Mock()
    )
    project_controller._write_sample_compute_config = Mock()  # type: ignore

    os_makedirs_mock = Mock(return_value=None)
    mock_write_project_file_to_disk = Mock(return_value=None)
    with patch.multiple("os", makedirs=os_makedirs_mock), patch(
        "anyscale.controllers.project_controller._write_project_file_to_disk"
    ) as mock_write_project_file_to_disk:
        project_controller.clone(project_name=project_test_data.name, owner=owner)

    mock_api_client.find_project_by_project_name_api_v2_projects_find_by_name_get.assert_called_once_with(
        name=project_test_data.name, _request_timeout=ANY, owner=owner
    )
    os_makedirs_mock.assert_called_once_with(project_test_data.name)
    mock_write_project_file_to_disk.assert_called_once_with(
        project_test_data.id, project_test_data.name
    )

    project_controller._write_sample_compute_config.assert_called_once_with(
        filepath=os.path.join(project_test_data.name, COMPUTE_CONFIG_FILENAME),
        project_id=project_test_data.id,
    )


def test_init_project(project_test_data: Project, mock_api_client: Mock) -> None:
    project_controller = ProjectController(
        api_client=mock_api_client, anyscale_client=Mock()
    )
    project_controller._write_sample_compute_config = Mock()  # type: ignore
    project_definition = ProjectDefinition(os.getcwd())
    project_definition.config["name"] = project_test_data.name
    mock_create_new_proj_def = Mock(
        return_value=(project_test_data.name, project_definition)
    )
    mock_register_project = Mock()
    os_path_exists_mock = Mock(return_value=False)

    with patch.multiple(
        "anyscale.controllers.project_controller",
        create_new_proj_def=mock_create_new_proj_def,
        register_project=mock_register_project,
    ), patch.multiple("os.path", exists=os_path_exists_mock):
        project_controller.init(name=project_test_data.name)

    mock_create_new_proj_def.assert_called_once_with(
        project_test_data.name, api_client=mock_api_client,
    )
    mock_register_project.assert_called_once_with(project_definition, mock_api_client)

    project_controller._write_sample_compute_config.assert_called_once_with(
        COMPUTE_CONFIG_FILENAME,
    )


@pytest.mark.parametrize("project_id", [None, "mock-project-id"])
@pytest.mark.parametrize("project_last_cloud_id", [None, "mock-project-cloud-id"])
@pytest.mark.parametrize("org_default_cloud", [None, "mock-default-cloud-id"])
def test_write_sample_compute_config(
    mock_api_client: Mock,
    project_id: Optional[str],
    project_last_cloud_id: Optional[str],
    org_default_cloud: Optional[str],
    userinfo_test_data: UserInfo,
) -> None:

    # Set up mocks.
    mock_anyscale_client = Mock()
    mock_anyscale_client.get_project.return_value.result.last_used_cloud_id = (
        project_last_cloud_id
    )
    first_mock_cloud_record = Mock()
    first_mock_cloud_record.id = "first-mock-cloud-id"
    last_mock_cloud_record = Mock()
    last_mock_cloud_record.id = "last-mock-cloud-id"
    mock_api_client.list_clouds_api_v2_clouds_get.return_value.results = [
        first_mock_cloud_record,
        last_mock_cloud_record,
    ]
    mock_config = Mock()
    mock_config.to_dict = Mock(return_value={"mock-config-key": "mock-config-value"})
    mock_api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.return_value.result = (
        mock_config
    )

    userinfo_test_data.organizations[0].default_cloud_id = org_default_cloud
    mock_api_client.get_user_info_api_v2_userinfo_get.return_value.result = (
        userinfo_test_data
    )

    project_controller = ProjectController(
        api_client=mock_api_client, anyscale_client=mock_anyscale_client
    )

    # Run the test.
    with patch("builtins.open", mock_open_factory()) as mock_open, patch(
        "anyscale.controllers.project_controller.get_cloud_id_and_name", Mock()
    ) as mock_get_cloud_id:

        # write_sample_compute_config with default cloud.
        if org_default_cloud:
            project_controller._write_sample_compute_config(filepath="mock-fp")
            mock_api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=org_default_cloud
            )
            mock_get_cloud_id.assert_called_once_with(
                mock_api_client, cloud_id=org_default_cloud
            )
            mock_open.assert_called_once_with("mock-fp", "w")
        # write_sample_compute_config with no project ID.
        elif not project_id:
            project_controller._write_sample_compute_config(filepath="mock-fp")

            mock_anyscale_client.get_project.assert_not_called()
            mock_api_client.list_clouds_api_v2_clouds_get.assert_called_once_with()
            mock_api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=last_mock_cloud_record.id
            )
            mock_open.assert_called_once_with("mock-fp", "w")

        # write_sample_compute_config
        # with project ID, but no default cloud there.
        elif not project_last_cloud_id:
            project_controller._write_sample_compute_config(
                filepath="mock-fp", project_id=project_id
            )

            mock_anyscale_client.get_project.assert_called_once_with(project_id)
            mock_api_client.list_clouds_api_v2_clouds_get.assert_called_once_with()
            mock_api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=last_mock_cloud_record.id
            )
            mock_open.assert_called_once_with("mock-fp", "w")

        # write_sample_compute_config
        # with project ID, and with a default cloud there.
        else:
            project_controller._write_sample_compute_config(
                filepath="mock-fp", project_id=project_id
            )

            mock_anyscale_client.get_project.assert_called_once_with(project_id)
            mock_api_client.list_clouds_api_v2_clouds_get.assert_not_called()
            mock_api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get.assert_called_once_with(
                cloud_id=project_last_cloud_id
            )
            mock_open.assert_called_once_with("mock-fp", "w")
