import argparse
from typing import Union

from convo.cli.arguments.default_arguments import (
    add_config_parameter,
    add_stories_parameter,
    add_nlu_data_parameter,
    add_out_parameter,
    add_domain_parameter,
)
from convo.shared.constants import DEFAULT_CONFIGURATION_PATH, CONVO_DEFAULT_DATA_PATH 


def set_train_arguments(parser: argparse.ArgumentParser):
    add_data_parameter(parser)
    add_config_parameter(parser)
    add_domain_parameter(parser)
    add_out_parameter(parser, help_text="Directory where your models should be stored.")

    add_augmentation_param(parser)
    add_debug_plots_param(parser)

    add_num_threads_param(parser)

    add_model_name_param(parser)
    add_persist_nlu_data_param(parser)
    add_force_param(parser)


def set_train_core_arguments(parser: argparse.ArgumentParser):
    add_stories_parameter(parser)
    add_domain_parameter(parser)
    add_core_config_param(parser)
    add_out_parameter(parser, help_text="Directory where your models should be stored.")

    add_augmentation_param(parser)
    add_debug_plots_param(parser)

    add_force_param(parser)

    add_model_name_param(parser)

    compare_arguments = parser.add_argument_group("Comparison Arguments")
    add_compare_params(compare_arguments)


def set_train_nlu_arguments(parser: argparse.ArgumentParser):
    add_config_parameter(parser)
    add_domain_parameter(parser, default=None)
    add_out_parameter(parser, help_text="Directory where your models should be stored.")

    add_nlu_data_parameter(parser, help_text="File or folder containing your NLU data.")

    add_num_threads_param(parser)

    add_model_name_param(parser)
    add_persist_nlu_data_param(parser)


def add_force_param(parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]):
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a model training even if the data has not changed.",
    )


def add_data_parameter(parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]):
    parser.add_argument(
        "--data",
        default=[CONVO_DEFAULT_DATA_PATH ],
        nargs="+",
        help="Paths to the Core and NLU data files.",
    )


def add_core_config_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-c",
        "--config",
        nargs="+",
        default=[DEFAULT_CONFIGURATION_PATH],
        help="The policy and NLU pipeline configuration of your bot. "
        "If multiple configuration files are provided, multiple Convo Core "
        "models are trained to compare policies.",
    )


def add_compare_params(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]
):
    parser.add_argument(
        "--percentages",
        nargs="*",
        type=int,
        default=[0, 25, 50, 75],
        help="Range of exclusion percentages.",
    )
    parser.add_argument(
        "--runs", type=int, default=3, help="Number of runs for experiments."
    )


def add_augmentation_param(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]
):
    parser.add_argument(
        "--augmentation",
        type=int,
        default=50,
        help="How much data augmentation to use during training.",
    )


def add_debug_plots_param(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]
):
    parser.add_argument(
        "--debug-plots",
        default=False,
        action="store_true",
        help="If enabled, will create plots showing checkpoints "
        "and their connections between story blocks in a  "
        "file called `story_blocks_connections.html`.",
    )


def add_num_threads_param(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]
):
    parser.add_argument(
        "--num-threads",
        type=int,
        default=1,
        help="Maximum amount of threads to use when training.",
    )


def add_model_name_param(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--fixed-model-name",
        type=str,
        help="If set, the name of the model file/dir will be set to the given "
        "name.",
    )


def add_persist_nlu_data_param(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]
):
    parser.add_argument(
        "--persist-nlu-data",
        action="store_true",
        help="Persist the nlu training data in the saved model.",
    )
