import argparse
from typing import Text

from convo.cli.arguments.default_arguments import (
    add_nlu_data_parameter,
    add_out_parameter,
    add_data_parameter,
    add_domain_parameter,
)
from convo.shared.constants import DEFAULT_CHANGED_DATA_PATH


def set_convert_argument(parser: argparse.ArgumentParser, data_type: Text):
    parser.add_argument(
        "-f",
        "--format",
        required=True,
        default="yaml",
        choices=["json", "md", "yaml"],
        help="Output format the training data should be converted into. "
        "Note: currently training data can be converted to 'yaml' format "
        "only from 'md' format",
    )

    add_data_parameter(parser, required=True, data_type=data_type)

    add_out_parameter(
        parser,
        required=True,
        default=DEFAULT_CHANGED_DATA_PATH,
        help_text="File (for `json` and `md`) or existing path (for `yaml`) "
        "where to save training data in Convo format.",
    )

    parser.add_argument("-l", "--language", default="en", help="Language of data.")


def set_split_argument(parser: argparse.ArgumentParser):
    add_nlu_data_parameter(parser, help_text="File or folder containing your NLU data.")

    parser.add_argument(
        "--training-fraction",
        type=float,
        default=0.8,
        help="Percentage of the data which should be in the training data.",
    )

    parser.add_argument(
        "--random-seed",
        type=int,
        default=None,
        help="Seed to generate the same train/test split.",
    )

    add_out_parameter(
        parser,
        default="train_test_split",
        help_text="Directory where the split files should be stored.",
    )


def set_validator_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--fail-on-warnings",
        default=False,
        action="store_true",
        help="Fail validation on warnings and errors. "
        "If omitted only errors will result in a non zero exit code.",
    )
    add_domain_parameter(parser)
    add_data_parameter(parser)
