import json
import os
from typing import Optional

import click

import anyscale
from anyscale.api import get_anyscale_api_client, get_api_client
from anyscale.cli_logger import _CliLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.cloud import get_cloud_id_and_name
from anyscale.project import (
    _write_project_file_to_disk,
    create_new_proj_def,
    get_proj_id_from_name,
    load_project_or_throw,
    register_project,
)
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as AnyscaleApi
from anyscale.util import get_endpoint


COMPUTE_CONFIG_FILENAME = "example_compute_config.json"


class ProjectController:
    def __init__(
        self,
        api_client: Optional[DefaultApi] = None,
        anyscale_client: Optional[AnyscaleApi] = None,
        log: _CliLogger = _CliLogger(),
    ):
        if api_client is None:
            api_client = get_api_client()
        self.api_client = api_client

        if anyscale_client is None:
            anyscale_client = get_anyscale_api_client()
        self.anyscale_api_client = anyscale_client
        self.log = log

    def clone(self, project_name: str, owner: Optional[str] = None) -> None:
        project_id = get_proj_id_from_name(project_name, self.api_client, owner)

        os.makedirs(project_name)
        _write_project_file_to_disk(project_id, project_name)

        self._write_sample_compute_config(
            filepath=os.path.join(project_name, COMPUTE_CONFIG_FILENAME),
            project_id=project_id,
        )

    def init(
        self,
        name: Optional[str] = None,
        config: Optional[str] = None,
        requirements: Optional[str] = None,
    ) -> None:
        if config:
            message = (
                "Warning: `anyscale init` is no longer accepting a cluster yaml in "
                "the --config argument. All sessions should be started with cluster envs "
                "and cluster computes."
            )
            self.log.warning(message)
        project_id_path = anyscale.project.ANYSCALE_PROJECT_FILE

        if os.path.exists(project_id_path):
            # Project id exists.
            project_definition = load_project_or_throw()
            project_id = project_definition.config["project_id"]

            # Checking if the project is already registered.
            # TODO: Fetch project by id rather than listing all projects
            resp = self.api_client.list_projects_api_v2_projects_get()
            for project in resp.results:
                if project.id == project_id:
                    raise click.ClickException(
                        "This project is already created at {url}".format(
                            url=get_endpoint(f"/projects/{project.id}")
                        )
                    )
            # Project id exists locally but not registered in the db.
            if click.confirm(
                "The Anyscale project associated with this doesn't "
                "seem to exist anymore or is not valid. Do you want "
                "to re-create it?",
                abort=True,
            ):
                os.remove(project_id_path)
                _, project_definition = create_new_proj_def(
                    name, api_client=self.api_client,
                )
        else:
            # Project id doesn't exist and not enough info to create project.
            _, project_definition = create_new_proj_def(
                name, api_client=self.api_client,
            )

        register_project(project_definition, self.api_client)
        self._write_sample_compute_config(COMPUTE_CONFIG_FILENAME)

    def _write_sample_compute_config(
        self, filepath: str, project_id: Optional[str] = None,
    ) -> None:
        """Writes a sample compute config JSON file to be used with anyscale up.
        If no default cloud is available from the organization and the user
        has never used a cloud before, don't write the sample compute config.
        """

        # Compute configs need a real cloud ID.
        cloud_id = None
        user = self.api_client.get_user_info_api_v2_userinfo_get().result
        organization = user.organizations[0]  # Each user only has one org
        if organization.default_cloud_id:
            # Use default cloud id if organization has one and if user has correct
            # permissions for it.
            try:
                get_cloud_id_and_name(
                    self.api_client, cloud_id=organization.default_cloud_id
                )
                cloud_id = organization.default_cloud_id
            except Exception:
                # Fallback to other options for getting cloud id.
                pass
        if not cloud_id and project_id:
            # See if the project has a cloud ID for us to use.
            project = self.anyscale_api_client.get_project(project_id).result
            cloud_id = project.last_used_cloud_id

        # If no cloud ID in the project, fall back to the oldest cloud.
        # (For full compatibility with other frontends, we should be getting
        # the last used cloud from the user, but our users APIs
        # are far from in good shape for that...)
        if not cloud_id:
            cloud_list = self.api_client.list_clouds_api_v2_clouds_get().results
            if len(cloud_list) == 0:
                # If there is no cloud ID from the user,
                # let them create their project and set up a
                # compute config JSON file later.
                return
            cloud_id = cloud_list[-1].id

        default_config = self.api_client.get_default_compute_config_api_v2_compute_templates_default_cloud_id_get(
            cloud_id=cloud_id
        ).result

        with open(filepath, "w") as f:
            json.dump(default_config.to_dict(), f, indent=2)
