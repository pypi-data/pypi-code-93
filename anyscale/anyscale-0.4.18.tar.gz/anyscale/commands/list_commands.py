"""
Defines and implements `anyscale list {resource}` commands.
Supported resources: clouds, projects, sessions, ips
"""

from typing import Any, Optional

import click

from anyscale.controllers.list_controller import ListController


@click.group("list", help="List resources (projects, sessions) within Anyscale.")
def list_cli() -> None:
    pass


@list_cli.command(
    name="clouds", help="List the clouds currently available in your account."
)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
def list_clouds(show_json: bool) -> None:
    list_controller = ListController()
    output = list_controller.list_clouds(json_format=show_json)
    print(output)


@list_cli.command(name="projects", help="List all accessible projects.")
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
@click.pass_context
def project_list(ctx: Any, show_json: bool) -> None:
    list_controller = ListController()
    output = list_controller.list_projects(json_format=show_json)
    print(output)


@list_cli.command(name="sessions", help="List all sessions within the current project.")
@click.option(
    "--name",
    help="Name of the session. If provided, this prints the snapshots that "
    "were applied and commands that ran for all sessions that match "
    "this name.",
    default=None,
)
@click.option("--all", help="List all sessions, including inactive ones.", is_flag=True)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
def session_list(name: Optional[str], all: bool, show_json: bool) -> None:
    list_controller = ListController()
    output = list_controller.list_sessions(
        name=name, show_all=all, json_format=show_json
    )
    print(output)


@list_cli.command(name="ips", help="List IP addresses of head and worker nodes.")
@click.argument("session-name", required=False, type=str)
@click.option("--json", "show_json", help="Return the results in json", is_flag=True)
@click.option(
    "--all", "all_sessions", help="List IPs of all active sessions.", is_flag=True
)
def list_ips(session_name: Optional[str], show_json: bool, all_sessions: bool) -> None:
    """List IP addresses of head and worker nodes."""
    list_controller = ListController()
    output = list_controller.list_ips(
        session_name=session_name, json_format=show_json, all_sessions=all_sessions
    )
    print(output)
