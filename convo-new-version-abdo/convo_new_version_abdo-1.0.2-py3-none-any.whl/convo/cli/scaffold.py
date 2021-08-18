import argparse
import os
import sys
from typing import List, Text

from convo import telemetry
from convo.cli import SubParsersAction
import convo.train
from convo.cli.shell import get_shell
from convo.cli.utils import generate_output_path
from convo.shared.utils.cli import printing_success, printing_error_exit
from convo.shared.constants import (
    DOCUMENTS_BASE_URL,
    DEFAULT_CONFIGURATION_PATH,
    CONVO_DEFAULT_DOMAIN_PATH,
    CONVO_DEFAULT_DATA_PATH ,
)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all init parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    parser = subparsers.add_parser(
        "init",
        parents=parents,
        help="Creates a new project, with example training data, "
        "actions, and config files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Automatically choose default options for prompts and suppress warnings.",
    )
    parser.add_argument(
        "--init-dir",
        default=None,
        help="Directory where your project should be initialized.",
    )

    parser.set_defaults(func=execute)


def print_train_or_information(args: argparse.Namespace, path: Text) -> None:
    import questionary

    printing_success("Finished creating project structure.")

    compulsory_train = (
        questionary.confirm("Do you want to train an initial model? 💪🏽")
        .skip_if(args.no_prompt, default=True)
        .ask()
    )

    if compulsory_train:
        printing_success("Training an initial model...")
        config = os.path.join(path, DEFAULT_CONFIGURATION_PATH)
        training_files = os.path.join(path, CONVO_DEFAULT_DATA_PATH )
        domain = os.path.join(path, CONVO_DEFAULT_DOMAIN_PATH)
        output = os.path.join(path, generate_output_path())

        args.model = convo.train(domain, config, training_files, output)

        print_run_or_information(args)

    else:
        printing_success(
            "No problem 👍🏼. You can also train a model later by going "
            "to the project dir and running 'convo train'."
        )


def print_run_or_information(args: argparse.Namespace) -> None:
    from convo.core import constants
    import questionary

    compulsory_run = (
        questionary.confirm(
            "Do you want to speak to the trained assistant on the command line? 🤖"
        )
        .skip_if(args.no_prompt, default=False)
        .ask()
    )

    if compulsory_run:
        # provide defaults for command line arguments
        attributes = [
            "endpoints",
            "credentials",
            "cors",
            "auth_token",
            "jwt_secret",
            "jwt_method",
            "enable_api",
            "remote_storage",
        ]
        for a in attributes:
            setattr(args, a, None)

        args.port = constants.BY_DEFAULT_SERVER_PORT

        get_shell(args)
    else:
        if args.no_prompt:
            print(
                "If you want to speak to the assistant, "
                "run 'convo shell' at any time inside "
                "the project dir."
            )
        else:
            printing_success(
                "Ok 👍🏼. "
                "If you want to speak to the assistant, "
                "run 'convo shell' at any time inside "
                "the project dir."
            )


def scaffold_init_project(args: argparse.Namespace, path: Text) -> None:
    generate_initial_project(path)
    print("Created project directory at '{}'.".format(os.path.abspath(path)))
    print_train_or_information(args, path)


def generate_initial_project(path: Text) -> None:
    from distutils.dir_util import copy_tree

    copy_tree(scaffold_path_flow(), path)


def scaffold_path_flow() -> Text:
    import pkg_resources

    return pkg_resources.resource_filename(__name__, "initial_project")


def cancel_print() -> None:
    printing_success("Ok. You can continue setting up by running 'convo init' 🙋🏽‍♀️")
    sys.exit(0)


def _ask_generate_path(path: Text) -> None:
    import questionary

    compulsory_generate = questionary.confirm(
        f"Path '{path}' does not exist 🧐. Create path?"
    ).ask()
    if compulsory_generate:
        os.makedirs(path)
    else:
        printing_success("Ok. You can continue setting up by running " "'convo init' 🙋🏽‍♀️")
        sys.exit(0)


def _query_overwrite(path: Text) -> None:
    import questionary

    override = questionary.confirm(
        "Directory '{}' is not empty. Continue?".format(os.path.abspath(path))
    ).ask()
    if not override:
        cancel_print()


def execute(args: argparse.Namespace) -> None:
    import questionary

    printing_success("Welcome to Convo! 🤖\n")
    if args.no_prompt:
        print(
            f"To get started quickly, an "
            f"initial project will be created.\n"
            f"If you need some help, check out "
            f"the documentation at {DOCUMENTS_BASE_URL}.\n"
        )
    else:
        print(
            f"To get started quickly, an "
            f"initial project will be created.\n"
            f"If you need some help, check out "
            f"the documentation at {DOCUMENTS_BASE_URL}.\n"
            f"Now let's start! 👇🏽\n"
        )

    if args.init_dir is not None:
        path_flow = args.init_dir
    else:
        path_flow = (
            questionary.text(
                "Please enter a path where the project will be "
                "created [default: current dir]",
                default=".",
            )
            .skip_if(args.no_prompt, default=".")
            .ask()
        )

    if args.no_prompt and not os.path.isdir(path_flow):
        printing_error_exit(f"Project init path '{path_flow}' not found.")

    if path_flow and not os.path.isdir(path_flow):
        _ask_generate_path(path_flow)

    if path_flow is None or not os.path.isdir(path_flow):
        cancel_print()

    if not args.no_prompt and len(os.listdir(path_flow)) > 0:
        _query_overwrite(path_flow)

    telemetry.traverse_project_init(path_flow)

    scaffold_init_project(args, path_flow)
