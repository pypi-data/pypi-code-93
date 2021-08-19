import requests
import json
import pathlib
import yaml
from urllib.parse import urlencode
from typing import List, Union
from requests.models import Response
from rich import print
from rich.console import Console
from yaml.loader import SafeLoader
from ._typing import Group, Project
from .errors import APIError


token: str
base_uri: str
console = Console()

# =============
# Decorator
# =============
def need_api_token(func):
    """Decorator for call with needed token

    Args:
        func (Callable): Function to call
    """

    def wrapper_func(*args, **kwargs):
        global token, base_uri

        # =============
        # Retrieve config
        # =============
        try:
            with open(
                pathlib.Path(__file__).resolve().parent.absolute() / "config.yaml", "r"
            ) as f:
                config = dict(yaml.load(f, Loader=SafeLoader))

                if not config["token"]:
                    raise Exception("No token found")

                token = config["token"]
                base_uri = config["target"]  # Always have a default value
        except (FileNotFoundError, Exception) as e:
            if isinstance(e, FileNotFoundError):
                print(
                    "Before making any calls, you need to setup at least your token by doing : hpm setup --token <TOKEN_VALUE>"
                )
                print(
                    "You can also setup a custom target uri by adding the parameter `--target <TARGET_URI>`"
                )
                exit()

            token = None

        if not token:
            print(
                "No token as been register. Please do so using `hpm setup --token <TOKEN_VALUE>.`"
            )
            exit()  # Force program exit because nothing will run correctly if no token as been provided
        return func(*args, **kwargs)

    return wrapper_func


# =============
# Utility function
# =============
def _create_group_from_json(json_response: dict) -> Group:
    """Create a group from a json response

    Args:
        json_response (dict): Response from api

    Returns:
        Group: Newly created group
    """
    return Group(
        json_response["id"],
        json_response["name"],
        json_response["path"],
        json_response["description"],
        json_response["visibility"],
        json_response["web_url"],
        json_response["full_path"],
        json_response["parent_id"],
    )


def _create_project_from_json(json_response: dict) -> Project:
    """Create a project from a json response

    Args:
        json_response (dict): Response from api

    Returns:
        Project: Newly created project
    """
    return Project(
        json_response["id"],
        json_response["description"],
        json_response["web_url"],
        json_response["name"],
        json_response["path_with_namespace"],
        json_response["star_count"],
        json_response["open_issues_count"],
        json_response["namespace"]["id"],
        json_response["namespace"]["name"],
        json_response["ssh_url_to_repo"],
        json_response["http_url_to_repo"],
    )


def _validate_api_response(response: Response) -> bool:
    """Validate an api call response

    Args:
        response (Response): Provided response

    Returns:
        bool: Response validation status
    """
    if not response.ok:
        # Custom message for most known error status codes
        if response.status_code == 404:
            print("Cannot reach API endpoint", response.status_code)
        elif response.status_code == 500:
            print("Server-side error", response.status_code)
        else:
            print("Error during API call", response.status_code)

        return False

    return True


# =============
# API calls
# =============
@need_api_token
def get_owned_groups() -> List[Group]:
    """Get user owned groups

    Returns:
        Group[]: List of owned groups
    """
    url = f"{base_uri}/groups?owned=true&per_page=100"

    payload = {}
    headers = {"Private-Token": token}

    with console.status("[bold green]💾 Getting groups..."):
        response = requests.request("GET", url, headers=headers, data=payload)

    if not _validate_api_response(response):
        return None

    response = json.loads(response.text)

    groups: List[Group] = []
    # @see: https://gitedu.hesge.ch/help/api/groups.md#list-groups
    for json_group in response:
        groups.append(_create_group_from_json(json_group))

    return groups


@need_api_token
def get_owned_projects(page=1):
    """Get user owned projects

    Args:
        page (int): Pagination number

    Return:
        Project[]: List of owned projects
    """
    url = f"{base_uri}/projects?membership=true&page={page}"

    payload = {}
    headers = {"Private-Token": token}

    with console.status("[bold green]💾 Getting projects..."):
        response = requests.request("GET", url, headers=headers, data=payload)

    if not _validate_api_response(response):
        return None

    response_json = json.loads(response.text)

    p_list: List[Project] = []
    # @see: https://gitedu.hesge.ch/help/api/projects.md#list-all-projects
    for json_project in response_json:
        p_list.append(_create_project_from_json(json_project))

    return {
        # @see: https://stackoverflow.com/a/45087988 for informations on headers
        "headers": {
            "X-Next-Page": response.headers.get("X-Next-Page"),
            "X-Prev-Page": response.headers.get("X-Prev-Page"),
            "X-Total-Pages": response.headers.get("X-Total-Pages"),
        },
        # Sort the project by full namespace for easier print later
        "list": sorted(p_list, key=lambda k: k.path_with_namespace),
    }


@need_api_token
def create_project(params: list) -> Union[Project, APIError]:
    """Create a new project

    Args:
        params (list): Param list

    Returns:
        Project: Newly created project
    """
    url = f"{base_uri}/projects?"

    # Build url parameters
    url_params = {}
    for param in params:
        if param["value"] is not None and param["value"] != "":
            url_params[param["key"]] = param["value"]

        # Special case for namespace check
        if param["key"] == "namespace_id" and param["value"] == -1:
            return APIError(message="Namespace not found")

    url += urlencode(url_params)

    payload = {}
    headers = {"Private-Token": token}

    with console.status("[bold green]🚀 Creating project..."):
        response = requests.request("POST", url, headers=headers, data=payload)

    if not _validate_api_response(response):
        return None

    response = json.loads(response.text)

    return _create_project_from_json(response)


@need_api_token
def get_subgroups(parent: Group) -> List[Group]:
    """Get the parent subgroups list

    Args:
        parent (Group): Parent group

    Returns:
        List[Group]: List of subgroups
    """
    url = f"{base_uri}/groups/{parent.id}/subgroups"

    payload = {}
    headers = {"Private-Token": token}

    with console.status("[bold green]💾 Getting subgroups...") as status:
        response = requests.request("GET", url, headers=headers, data=payload)

    if not _validate_api_response(response):
        return None

    response = json.loads(response.text)

    groups: List[Group] = []
    for json_group in response:
        groups.append(_create_group_from_json(json_group))

    return groups


@need_api_token
def get_group_projects(group: Group) -> List[Project]:
    """Get the provided group's project list

    Args:
        group (Group): Group to fetch from

    Returns:
        List[Project]: List of projects
    """
    url = f"{base_uri}/groups/{group.id}/projects"

    payload = {}
    headers = {"Private-Token": token}

    with console.status("[bold green]💾 Getting group's projects..."):
        response = requests.request("GET", url, headers=headers, data=payload)

    if not _validate_api_response(response):
        return None

    response_json = json.loads(response.text)

    p_list: List[Project] = []
    for json_project in response_json:
        p_list.append(_create_project_from_json(json_project))

    return p_list


@need_api_token
def get_group(group_id: int) -> Group:
    """Get group details

    Args:
        group_id (int): Wanted group

    Returns:
        Group: Found group
    """
    url = f"{base_uri}/groups/{group_id}"

    payload = {}
    headers = {"Private-Token": token}

    with console.status("[bold green]💾 Getting group..."):
        response = requests.request("GET", url, headers=headers, data=payload)

    if not _validate_api_response(response):
        return None

    response = json.loads(response)

    return _create_group_from_json(response)
