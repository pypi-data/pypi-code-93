import sys
from argparse import ArgumentParser
from typing import List, Union

from loguru import logger

from . import BaseELGCommand


def docker_create_command_factory(args):
    return DockerCreateCommand(
        classname=args.classname,
        path=args.path,
        requirements=args.requirements,
        requirements_file=args.requirements_file,
        required_files=args.required_files,
        required_folders=args.required_folders,
        commands=args.commands,
        base_image=args.base_image,
        service_type=args.service_type,
    )


class DockerCreateCommand(BaseELGCommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        info_parser = parser.add_parser("create", description="Create requirements.txt and Docker files.")
        info_parser.add_argument(
            "-n", "--classname", type=str, default=None, required=True, help="Name of the Service Class"
        )
        info_parser.add_argument(
            "-p",
            "--path",
            type=str,
            default="",
            required=None,
            help="Path the python script containing the Service Class definition from the current location",
        )
        info_parser.add_argument(
            "-i",
            "--base_image",
            type=str,
            default="python:slim",
            required=None,
            help="Name of the base Docker image used in the Dockerfile",
        )
        info_parser.add_argument(
            "-r",
            "--requirements",
            type=str,
            action="append",
            default=None,
            required=False,
            help="Pypi requirements for the Service Class, e.g. `nltk==3.5`",
        )
        info_parser.add_argument(
            "--requirements_file",
            type=str,
            default=None,
            required=False,
            help="Pypi requirements file, e.g. `requirements.txt`",
        )
        info_parser.add_argument(
            "-f",
            "--required_files",
            type=str,
            action="append",
            default=None,
            required=False,
            help="Name of the files from the directory of the Service Class",
        )
        info_parser.add_argument(
            "--required_folders",
            type=str,
            action="append",
            default=None,
            required=False,
            help="Name of the folders from the directory of the Service Class",
        )
        info_parser.add_argument(
            "--commands",
            type=str,
            action="append",
            default=None,
            required=False,
            help="Command to run in the Dockerfile",
        )
        info_parser.add_argument(
            "-t",
            "--service_type",
            type=str,
            default="flask",
            required=None,
            help="Type of service used. Can be 'flask' or 'quart'.",
            choices=["flask", "quart"],
        )

        info_parser.set_defaults(func=docker_create_command_factory)

    def __init__(
        self,
        classname: str = None,
        path: str = "",
        requirements: Union[str, List[str]] = None,
        requirements_file: str = None,
        required_files: Union[str, List[str]] = None,
        required_folders: Union[str, List[str]] = None,
        commands: Union[str, List[str]] = None,
        base_image: str = None,
        service_type: str = "flask",
    ):
        self._classname = classname
        self._path = path
        self._requirements = requirements
        self._requirements_file = requirements_file
        self._required_files = required_files
        self._required_folders = required_folders
        self._commands = commands
        self._base_image = base_image
        self._service_type = service_type

    def run(self):
        if self._service_type == "flask":
            from ..flask_service import FlaskService
        elif self._service_type == "quart":
            from ..quart_service import QuartService

        try:
            logger.info(f"Creation of `requirements.txt`")
            if self._requirements is None:
                requirements = []
            elif isinstance(self._requirements, str):
                requirements = [self._requirements]
            else:
                requirements = self._requirements
            if self._requirements_file is None:
                pass
            else:
                with open(self._requirements_file) as f:
                    requirements += f.read().split("\n")
            if self._service_type == "flask":
                FlaskService.create_requirements(requirements=requirements, path=self._path)
            elif self._service_type == "quart":
                QuartService.create_requirements(requirements=requirements, path=self._path)
            logger.info(f"Creation of `Dockerfile` and `docker-entrypoint.sh`")
            if self._required_files is None:
                required_files = []
            elif isinstance(self._required_files, str):
                required_files = [self._required_files]
            else:
                required_files = self._required_files
            if self._required_folders is None:
                required_folders = []
            elif isinstance(self._required_folders, str):
                required_folders = [self._required_folders]
            else:
                required_folders = self._required_folders
            if self._commands is None:
                commands = []
            elif isinstance(self._commands, str):
                commands = [self._commands]
            else:
                commands = self._commands
            if self._service_type == "flask":
                FlaskService.create_docker_files(
                    required_files=required_files,
                    required_folders=required_folders,
                    commands=commands,
                    base_image=self._base_image,
                    path=self._path,
                )
            elif self._service_type == "quart":
                QuartService.create_docker_files(
                    required_files=required_files,
                    required_folders=required_folders,
                    commands=commands,
                    base_image=self._base_image,
                    path=self._path,
                )
        except Exception as e:
            logger.error(f"Error during the creation of docker files - {e}")
            sys.exit(1)
