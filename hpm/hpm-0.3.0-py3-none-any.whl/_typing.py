from argparse import Namespace
from typing import Callable, Any, List
from dataclasses import dataclass, field
import abc


@dataclass
class Parameter:
    """Class representing argparse parameter"""

    name: str
    help: str
    action: str = None


@dataclass
class Command:
    __metaclass__ = abc.ABCMeta

    """Class reprensenting argparse subparser"""
    name: str
    help: str
    params: List[Parameter] = field(default_factory=list)

    @abc.abstractmethod
    def execute(self, args: Namespace = None) -> None:
        """Execute the command

        Args:
            args (Namespace, optional): List of args provided by argparse. Defaults to None.
        """
        raise NotImplementedError()


@dataclass
class Group:
    id: int
    name: str
    path: str
    description: str
    visibility: str
    web_url: str
    full_path: str
    parent_id: int


class Project:
    def __init__(
        self,
        _id: int,
        description: str,
        web_url: str,
        name: str,
        path_with_namespace: str,
        star_count: int,
        open_issues_count: int,
        namespace_id: int,
        namespace_name: str,
        ssh_url_to_repo: str,
        http_url_to_repo: str,
    ) -> None:
        self.id = _id
        self.description = description
        self.web_url = web_url
        self.name = name
        self.path_with_namespace = path_with_namespace
        self.star_count = star_count
        self.open_issues_count = open_issues_count
        self.namespace = {"id": namespace_id, "name": namespace_name}
        self.ssh_url_to_repo = ssh_url_to_repo
        self.http_url_to_repo = http_url_to_repo

    def __str__(self) -> str:
        return f'Porject({self.id}, "{self.path_with_namespace}")'

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class ProjectQuestion:
    message: str
    name: str
    default: str
    help: str
    validate: Callable[[str], bool] = None
    transform: Callable[[str], bool] = None
    response: Any = field(init=False)

    def __post_init__(self):
        if self.message == "" or self.name == "":
            raise ValueError("No value provided for message or name")

    def transform_response(self, response: Any) -> None:
        if response is None:
            return

        if self.transform is not None:
            self.response = self.transform(response)

    def set_response(self, response: Any) -> None:
        if response is None:
            self.response = self.default

        self.response = response
