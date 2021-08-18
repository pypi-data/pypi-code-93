import argparse
import logging
import os
import platform
import sys

from convo_sdk import __version__ as convo_sdk_version

from convo import version
from convo.cli import (
    data,
    export,
    interactive,
    run,
    scaffold,
    shell,
    telemetry,
    test,
    train,
    visualize,
    x,
)

from convo.cli.arguments.default_arguments import add_logging_option
from convo.cli.utils import parse_last_positional_args_as_model_path_flow
from convo.shared.exceptions import ConvoExceptions 
from convo.shared.utils.cli import printing_error
import convo.telemetry
from convo.utils.common import setting_logs_and_warnings_filter, setting_logging_level
import convo.utils.io
import convo.utils.tensorflow.environment as tf_env

log = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Parse all the command line arguments for the training script."""

    parser = argparse.ArgumentParser(
        prog="convo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Convo command line interface. Convo allows you to build "
        "your own conversational assistants 🤖. The 'convo' command "
        "allows you to easily run most common commands like "
        "creating a new bot, training or evaluating models.",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Print installed Convo version",
    )

    parent_parser = argparse.ArgumentParser(add_help=False)
    add_logging_option(parent_parser)
    parent_parsers = [parent_parser]

    sub_parsers = parser.add_subparsers(help="Convo commands")

    scaffold.sub_parser_addition(sub_parsers, parents=parent_parsers)
    run.sub_parser_addition(sub_parsers, parents=parent_parsers)
    shell.sub_parser_addition(sub_parsers, parents=parent_parsers)
    train.sub_parser_addition(sub_parsers, parents=parent_parsers)
    interactive.sub_parser_addition(sub_parsers, parents=parent_parsers)
    telemetry.sub_parser_addition(sub_parsers, parents=parent_parsers)
    test.sub_parser_addition(sub_parsers, parents=parent_parsers)
    visualize.sub_parser_addition(sub_parsers, parents=parent_parsers)
    data.sub_parser_addition(sub_parsers, parents=parent_parsers)
    export.sub_parser_addition(sub_parsers, parents=parent_parsers)
    x.sub_parser_addition(sub_parsers, parents=parent_parsers)

    return parser


def print_version() -> None:
    """Prints version information of convo tooling and python."""

    python_ver, os_information = sys.version.split("\n")
    try:
        from convox.community.version import __version__  # pytype: disable=import-error

        x_info = __version__
    except ModuleNotFoundError:
        x_info = None

    print(f"Convo Version     : {version.__version__}")
    print(f"Convo SDK Version : {convo_sdk_version}")
    print(f"Convo X Version   : {x_info}")
    print(f"Python Version   : {python_ver}")
    print(f"Operating System : {platform.platform()}")
    print(f"Python Path      : {sys.executable}")


def main() -> None:
    # Running as standalone python application

    parse_last_positional_args_as_model_path_flow()
    arg_parser = create_argument_parser()
    cmdline_arguments = arg_parser.parse_args()

    log_level = (
        cmdline_arguments.loglevel if hasattr(cmdline_arguments, "loglevel") else None
    )
    setting_logging_level(log_level)

    tf_env.setup_tf_env()

    # insert current path in syspath so custom modules are found
    sys.path.insert(1, os.getcwd())

    try:
        if hasattr(cmdline_arguments, "func"):
            convo.utils.io.config_color_logging(log_level)
            setting_logs_and_warnings_filter()
            convo.telemetry.start_error_reporting()
            cmdline_arguments.func(cmdline_arguments)
        elif hasattr(cmdline_arguments, "version"):
            print_version()
        else:
            # user has not provided a subcommand, let's print the help
            log.error("No command specified.")
            arg_parser.print_help()
            sys.exit(1)
    except ConvoExceptions  as e:
        # these are exceptions we expect to happen (e.g. invalid training data format)
        # it doesn't make sense to print a stacktrace for these if we are not in
        # debug mode
        log.debug("Failed to run CLI command due to an exception.", exc_info=e)
        printing_error(f"{e.__class__.__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
