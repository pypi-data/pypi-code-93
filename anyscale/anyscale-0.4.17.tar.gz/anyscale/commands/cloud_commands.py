from typing import Optional

import click

from anyscale.commands.util import OptionPromptNull
from anyscale.controllers.cloud_controller import CloudController


@click.group(
    "cloud",
    short_help="Configure cloud provider authentication for Anyscale.",
    help="""Configure cloud provider authentication and setup
to allow Anyscale to launch instances in your account.""",
)
def cloud_cli() -> None:
    pass


@cloud_cli.command(name="delete", help="Delete a cloud.")
@click.argument("cloud-name", required=False)
@click.option(
    "--cloud-id", help="Cloud id to delete. Alternative to cloud name.", required=False
)
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Don't ask for confirmation."
)
def cloud_delete(cloud_name: str, cloud_id: str, yes: bool) -> None:
    CloudController().delete_cloud(
        cloud_name=cloud_name, cloud_id=cloud_id, skip_confirmation=yes
    )


@cloud_cli.command(
    name="set-default",
    help=(
        "Sets default cloud for your organization. This operation can only be performed "
        "by organization admins, and the default cloud must have organization level "
        "permissions."
    ),
)
@click.argument("cloud-name", required=False)
@click.option(
    "--cloud-id",
    help="Cloud id to set as default. Alternative to cloud name.",
    required=False,
)
def cloud_set_default(cloud_name: str, cloud_id: str) -> None:
    CloudController().set_default_cloud(cloud_name=cloud_name, cloud_id=cloud_id)


@cloud_cli.command(name="setup", help="Set up a cloud provider.")
@click.option(
    "--provider",
    help="The cloud provider type.",
    required=True,
    prompt="Provider",
    type=click.Choice(["aws", "gcp"], case_sensitive=False),
)
@click.option(
    "--region",
    cls=OptionPromptNull,
    help="Region to set up the credentials in.",
    required=True,
    prompt="Region",
    default_option="provider",
    default=lambda p: "us-west-2" if p == "aws" else "us-west1",
    show_default=True,
)
@click.option("--name", help="Name of the cloud.", required=True, prompt="Name")
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Don't ask for confirmation."
)
@click.option(
    "--gcp-folder-id",
    help="Folder ID where the 'Anyscale'  folder will be created.",
    required=False,
    type=int,
)
def setup_cloud(
    provider: str, region: str, name: str, yes: bool, gcp_folder_id: Optional[int]
) -> None:
    CloudController().setup_cloud(
        provider=provider, region=region, name=name, yes=yes, folder_id=gcp_folder_id
    )


@cloud_cli.group("config", help="Manage the configuration for a cloud.", hidden=True)
def cloud_config_group() -> None:
    pass


@cloud_config_group.command("update", help="Update the configuration for a cloud.")
@click.argument("cloud-name", required=False)
@click.option(
    "--cloud-id", help="Cloud id to update. Alternative to cloud name.", required=False
)
@click.option(
    "--max-stopped-instances",
    help="Maximum number of stopped instances permitted in the shared instance pool.",
    required=True,
)
def cloud_config_update(
    cloud_name: str, cloud_id: str, max_stopped_instances: int
) -> None:
    CloudController().update_cloud_config(
        cloud_name=cloud_name,
        cloud_id=cloud_id,
        max_stopped_instances=max_stopped_instances,
    )


@cloud_config_group.command("get", help="Get the current configuration for a cloud.")
@click.argument("cloud-name", required=False)
@click.option(
    "--cloud-id", help="Cloud id to delete. Alternative to cloud name.", required=False
)
def cloud_config_get(cloud_name: str, cloud_id: str) -> None:
    print(CloudController().get_cloud_config(cloud_name=cloud_name, cloud_id=cloud_id,))
