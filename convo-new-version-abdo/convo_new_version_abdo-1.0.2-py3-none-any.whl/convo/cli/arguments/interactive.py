import argparse
import uuid

from convo.cli.arguments.default_arguments import (
    add_domain_parameter,
    add_stories_parameter,
    add_model_parameter,
    add_end_point_parameter,
)
from convo.cli.arguments.train import (
    add_force_param,
    add_data_parameter,
    add_config_parameter,
    add_out_parameter,
    add_debug_plots_param,
    add_augmentation_param,
    add_persist_nlu_data_param,
)
from convo.cli.arguments.run import add_new_port_argument


def set_interactive_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--e2e",
        action="store_true",
        help="Save story files in e2e format. In this format user messages "
        "will be included in the stories.",
    )
    add_new_port_argument(parser)

    add_model_parameter(parser, default=None)
    add_data_parameter(parser)

    add_common_parameters(parser)
    train_arguments = add_training_argument(parser)

    add_force_param(train_arguments)
    add_persist_nlu_data_param(train_arguments)


def set_interactive_core_argument(parser: argparse.ArgumentParser) -> None:
    add_model_parameter(parser, model_name="Convo Core", default=None)
    add_stories_parameter(parser)

    add_common_parameters(parser)
    add_training_argument(parser)
    add_new_port_argument(parser)


def add_common_parameters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--skip-visualization",
        default=False,
        action="store_true",
        help="Disable plotting the visualization during interactive learning.",
    )

    parser.add_argument(
        "--conversation-id",
        default=uuid.uuid4().hex,
        help="Specify the id of the conversation the messages are in. Defaults to a "
        "UUID that will be randomly generated.",
    )

    add_end_point_parameter(
        parser,
        help_text="Configuration file for the model server and the connectors as a yml file.",
    )


# noinspection PyProtectedMember
def add_training_argument(parser: argparse.ArgumentParser) -> argparse._ArgumentGroup:
    train_arguments = parser.add_argument_group("Train Arguments")
    add_config_parameter(train_arguments)
    add_domain_parameter(train_arguments)
    add_out_parameter(
        train_arguments, help_text="Directory where your models should be stored."
    )
    add_augmentation_param(train_arguments)
    add_debug_plots_param(train_arguments)

    return train_arguments
