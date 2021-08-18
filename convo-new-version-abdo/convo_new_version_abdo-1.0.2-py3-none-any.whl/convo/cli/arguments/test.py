import argparse
from typing import Union

from convo.shared.constants import DEFAULT_MODEL_PATH , DEFAULT_RESULT_PATH 

from convo.cli.arguments.default_arguments import (
    add_stories_parameter,
    add_model_parameter,
    add_nlu_data_parameter,
    add_end_point_parameter,
    add_out_parameter,
)
from convo.model import fetch_latest_model


def set_testing_arguments(parser: argparse.ArgumentParser):
    add_model_parameter(parser, add_positional_arg=False)

    core_arguments = parser.add_argument_group("Core Test Arguments")
    add_test_core_argument_group(core_arguments)

    nlu_arguments = parser.add_argument_group("NLU Test Arguments")
    add_test_nlu_argument_group(nlu_arguments)

    add_no_plot_parameters(parser)
    add_errors_success_parameters(parser)
    add_out_parameter(
        parser,
        default=DEFAULT_RESULT_PATH ,
        help_text="Output path for any files created during the evaluation.",
    )


def set_testing_core_arguments(parser: argparse.ArgumentParser):
    add_test_core_model_parameters(parser)
    add_test_core_argument_group(parser, include_e2e_argument=True)


def set_testing_nlu_arguments(parser: argparse.ArgumentParser):
    add_model_parameter(parser, add_positional_arg=False)
    add_test_nlu_argument_group(parser)


def add_test_core_argument_group(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer],
    include_e2e_argument: bool = False,
):
    add_stories_parameter(parser, "test")
    parser.add_argument(
        "--max-stories", type=int, help="Maximum number of stories to test on."
    )
    add_out_parameter(
        parser,
        default=DEFAULT_RESULT_PATH ,
        help_text="Output path for any files created during the evaluation.",
    )
    if include_e2e_argument:
        parser.add_argument(
            "--e2e",
            "--end-to-end",
            action="store_true",
            help="Run an end-to-end evaluation for combined action and "
            "intent prediction. Requires a story file in end-to-end "
            "format.",
        )
    add_end_point_parameter(
        parser, help_text="Configuration file for the connectors as a yml file."
    )
    parser.add_argument(
        "--fail-on-prediction-errors",
        action="store_true",
        help="If a prediction error is encountered, an exception "
        "is thrown. This can be used to validate stories during "
        "tests, e.g. on travis.",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="If supplied, downloads a story file from a URL and "
        "trains on it. Fetches the data by sending a GET request "
        "to the supplied URL.",
    )
    parser.add_argument(
        "--evaluate-model-directory",
        default=False,
        action="store_true",
        help="Should be set to evaluate models trained via "
        "'convo train core --config <config-1> <config-2>'. "
        "All models in the provided dir are evaluated "
        "and compared against each others.",
    )
    add_no_plot_parameters(parser)
    add_errors_success_parameters(parser)


def add_test_nlu_argument_group(
    parser: Union[argparse.ArgumentParser, argparse._ActionsContainer]
):
    add_nlu_data_parameter(parser, help_text="File or folder containing your NLU data.")

    add_out_parameter(
        parser,
        default=DEFAULT_RESULT_PATH ,
        help_text="Output path for any files created during the evaluation.",
    )
    parser.add_argument(
        "-c",
        "--config",
        nargs="+",
        default=None,
        help="Model configuration file. If a single file is passed and cross "
        "validation mode is chosen, cross-validation is performed, if "
        "multiple configs or a folder of configs are passed, models "
        "will be trained and compared directly.",
    )

    cross_validation_arguments = parser.add_argument_group("Cross Validation")
    cross_validation_arguments.add_argument(
        "--cross-validation",
        action="store_true",
        default=False,
        help="Switch on cross validation mode. Any provided model will be ignored.",
    )
    cross_validation_arguments.add_argument(
        "-f",
        "--folds",
        required=False,
        default=5,
        help="Number of cross validation folds (cross validation only).",
    )
    comparison_arguments = parser.add_argument_group("Comparison Mode")
    comparison_arguments.add_argument(
        "-r",
        "--runs",
        required=False,
        default=3,
        type=int,
        help="Number of comparison runs to make.",
    )
    comparison_arguments.add_argument(
        "-p",
        "--percentages",
        required=False,
        nargs="+",
        type=int,
        default=[0, 25, 50, 75],
        help="Percentages of training data to exclude during comparison.",
    )

    add_no_plot_parameters(parser)
    add_errors_success_parameters(parser)


def add_test_core_model_parameters(parser: argparse.ArgumentParser):
    default_path = fetch_latest_model(DEFAULT_MODEL_PATH )
    parser.add_argument(
        "-m",
        "--model",
        nargs="+",
        default=[default_path],
        help="Path to a pre-trained model. If it is a 'tar.gz' file that model file "
        "will be used. If it is a dir, the latest model in that dir "
        "will be used (exception: '--evaluate-model-directory' flag is set). If multiple "
        "'tar.gz' files are provided, all those models will be compared.",
    )


def add_no_plot_parameters(
    parser: argparse.ArgumentParser, default: bool = False, required: bool = False
) -> None:
    parser.add_argument(
        "--no-plot",
        dest="disable_plotting",
        action="store_true",
        default=default,
        help="Don't render evaluation plots.",
        required=required,
    )


def add_errors_success_parameters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--successes",
        action="store_true",
        default=False,
        help="If set successful predictions will be written to a file.",
    )
    parser.add_argument(
        "--no-errors",
        action="store_true",
        default=False,
        help="If set incorrect predictions will NOT be written to a file.",
    )
