import argparse
import logging
from typing import Text, Union, Optional

from convo.shared.constants import (
    DEFAULT_CONFIGURATION_PATH,
    CONVO_DEFAULT_DOMAIN_PATH,
    DEFAULT_MODEL_PATH ,
    CONVO_DEFAULT_DATA_PATH ,
)


def add_model_parameter(
    parser: argparse.ArgumentParser,
    model_name: Text = "Convo",
    add_positional_arg: bool = True,
    default: Optional[Text] = DEFAULT_MODEL_PATH ,
) -> None:
    help_text = (
        "Path to a trained {} model. If a dir is specified, it will "
        "use the latest model in this dir.".format(model_name)
    )
    parser.add_argument("-m", "--model", type=str, default=default, help=help_text)
    if add_positional_arg:
        parser.add_argument(
            "model-as-positional-argument", nargs="?", type=str, help=help_text
        )


def add_stories_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    stories_name: Text = "training",
) -> None:
    parser.add_argument(
        "-s",
        "--stories",
        type=str,
        default=CONVO_DEFAULT_DATA_PATH ,
        help=f"File or folder containing your {stories_name} stories.",
    )


def add_nlu_data_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    help_text: Text,
    default: Optional[Text] = CONVO_DEFAULT_DATA_PATH ,
) -> None:
    parser.add_argument("-u", "--nlu", type=str, default=default, help=help_text)


def add_domain_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    default: Optional[Text] = CONVO_DEFAULT_DOMAIN_PATH,
) -> None:
    parser.add_argument(
        "-d",
        "--domain",
        type=str,
        default=default,
        help="Domain specification. This can be a single YAML file, or a dir "
        "that contains several files with domain specifications in it. The content "
        "of these files will be read and merged together.",
    )


def add_config_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    default: Optional[Text] = DEFAULT_CONFIGURATION_PATH,
) -> None:
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=default,
        help="The policy and NLU pipeline configuration of your bot.",
    )


def add_out_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    help_text: Text,
    default: Optional[Text] = DEFAULT_MODEL_PATH ,
    required: bool = False,
) -> None:
    parser.add_argument(
        "--out", type=str, default=default, help=help_text, required=required
    )


def add_end_point_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    help_text: Text,
    default: Optional[Text] = None,
) -> None:
    parser.add_argument("--endpoints", type=str, default=default, help=help_text)


def add_data_parameter(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    default: Optional[Text] = CONVO_DEFAULT_DATA_PATH ,
    required: bool = False,
    data_type: Text = "Convo ",
) -> None:
    parser.add_argument(
        "--data",
        type=str,
        default=default,
        help=f"Path to the file or dir containing {data_type} data.",
        required=required,
    )


def add_logging_option(parser: argparse.ArgumentParser) -> None:
    """Add options to an argument parser to configure logging levels."""

    logging_arguments = parser.add_argument_group("Python Logging Options")

    # arguments for logging configuration
    logging_arguments.add_argument(
        "-v",
        "--verbose",
        help="Be verbose. Sets logging level to INFO.",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    logging_arguments.add_argument(
        "-vv",
        "--debug",
        help="Print lots of debugging statements. Sets logging level to DEBUG.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    logging_arguments.add_argument(
        "--quiet",
        help="Be quiet! Sets logging level to WARNING.",
        action="store_const",
        dest="loglevel",
        const=logging.WARNING,
    )
