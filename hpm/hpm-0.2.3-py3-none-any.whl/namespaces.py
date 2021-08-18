from typing import List
from ._typing import Group, Project
from .api import get_owned_groups


def insert_subnamspace(parent: dict, subnamespace: Group):
    """Insert a new subnamespace in the parent

    Args:
        parent (dict): Parent namespace
        subnamespace (Group): Child namespace

    Returns:
        dict: Updated parent
    """
    if parent["id"] == subnamespace.parent_id:
        parent["children"].append(
            {
                "id": subnamespace.id,
                "name": subnamespace.name,
                "full_path": subnamespace.full_path,
                "url": subnamespace.web_url,
                "children": [],
                "projects": [],
            }
        )
        return parent

    for _next_namespace in parent["children"]:
        if isinstance(_next_namespace, dict):
            item = insert_subnamspace(_next_namespace, subnamespace)
            if item is not None:
                return item


def insert_project_in_namespace(namespaces: dict, project: Project):
    """Insert a project in the corresponding namespace

    Args:
        namespaces (dict): Root namespaces
        project (Project): Project to be inserted

    Returns:
        dict: Updated namespaces dict
    """
    if namespaces["id"] == project.namespace["id"]:
        namespaces["projects"].append(project)
        return namespaces

    for _next_namespace in namespaces["children"]:
        _next = insert_project_in_namespace(_next_namespace, project)
        if _next is not None:
            return _next


def create_namespace_tree(groups: List[Group], projects: List[Project]) -> list:
    """Create a namespace array containing every projects

    Args:
        groups (List[Group]): Group list
        projects (List[Project]): Project list

    Returns:
        list: List of all namespaces.\ne.g.:\n[\n{\n\t'id': 1234,\n\t'name': 'my-group',\n\t'children': [{...}],\n\t'projects': [<Project>,...]\n\n}, {...}\n]
    """
    parent = []
    for group in groups:
        if group.parent_id is not None:
            for p in parent:
                p = insert_subnamspace(p, group)
        else:
            parent.append(
                {
                    "id": group.id,
                    "name": group.name,
                    "full_path": group.full_path,
                    "url": group.web_url,
                    "children": [],
                    "projects": [],
                }
            )

    tmp = projects.copy()
    for project in projects:
        for par in parent:
            if insert_project_in_namespace(par, project) is not None:
                tmp.remove(project)
                break

    # Now projects holds only personal projects (not the ones in groups)
    projects = tmp
    if len(projects) > 0:
        parent.append(
            {
                "id": projects[0].namespace["id"],
                "name": "Personal",
                "url": f'https://gitedu.hesge.ch/users/{projects[0].namespace["name"]}/projects',
                "children": [],
                "projects": [],
            }
        )
    for project in projects:
        insert_project_in_namespace(parent[-1], project)

    return parent


def get_namespace_id(namespace_name: str) -> int:
    """Get the namespace id to privide to the api

    Args:
        namespace_name (str): Namespace name

    Returns:
        int: Namespace id
    """
    GROUPS = get_owned_groups()

    if GROUPS is None:
        return -1

    _id = [group.id for group in GROUPS if group.full_path == namespace_name]

    if len(_id) > 0:
        return _id[0]
    else:
        return -1
