#!/usr/bin/env python
"""GitLab Client
"""
from typing import Optional
from typing import Dict
from typing import List
from typing import cast

from .endpoints import IEndpoint

from .crud import APICreate
from .crud import APIRead
from .crud import APIUpdate

# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring
# the following creats problems when inheriting from more than 3 gitlab.crud.API* Mixins
# pylint: disable=too-many-ancestors


class Runners(APIRead):
    path = "/projects"

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))


class Projects(APIRead):
    path = "/projects"

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))


class Groups(APIRead):
    path = "/groups"

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))


class Users(APIRead, APICreate):
    path = '/users'


class Group(APIRead, APIUpdate):
    def __init__(self, endpoint: IEndpoint,
            group_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/groups/{group_id}"


class User(APIRead, APIUpdate):
    def __init__(self, endpoint: IEndpoint,
            user_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/users/{user_id}"


class UserProjects(APIRead, APIUpdate):
    def __init__(self, endpoint: IEndpoint,
            user_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/users/{user_id}/projects"


class Project(APIRead, APIUpdate):
    def __init__(self, endpoint: IEndpoint,
            project_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/projects/{project_id}"


class Pipeline(APIRead):
    def __init__(self, endpoint: IEndpoint,
            project_id: int, pipeline_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/projects/{project_id}/pipelines/{pipeline_id}"


class GroupBadges(APIRead):
    def __init__(self, endpoint: IEndpoint,
            group_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/groups/{group_id}/badges"

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))


class ProjectBadges(APIRead):
    def __init__(self, endpoint: IEndpoint,
            project_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/projects/{project_id}/badges"

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))


class ProjectBadge(APIRead):
    def __init__(self, endpoint: IEndpoint,
            project_id: int, badge_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/projects/{project_id}/badges/{badge_id}"

class Releases(APIRead, APICreate):
    def __init__(self, endpoint: IEndpoint,
            project_id: int) -> None:
        super().__init__(endpoint)

        self.path = f"/projects/{project_id}/releases"

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))



class Release(APIRead):
    def __init__(self, endpoint: IEndpoint,
            project_id: int, tag_name: str) -> None:
        super().__init__(endpoint)

        self.path = f"/projects/{project_id}/releases/{tag_name}"


class GroupWikis(APIRead, APICreate):
    def __init__(self, endpoint: IEndpoint,
            group_id: int):
        super().__init__(endpoint)

        self.path = f'/groups/{group_id}/wikis'

    def read(self, attributes: Optional[Dict] = None) -> List:
        # method overloading only necessary to change the return type to a more specific List.
        return cast(List, super().read(attributes))


class GroupWiki(APIRead, APIUpdate):
    def __init__(self, endpoint: IEndpoint,
            group_id: int, slug: str):
        super().__init__(endpoint)

        self.path = f'/groups/{group_id}/wikis/{slug}'
