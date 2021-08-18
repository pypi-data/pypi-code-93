import argparse
import logging
import uuid

from typing import List

from convo import telemetry
from convo.cli import SubParsersAction
from convo.cli.arguments import shell as arguments
from convo.shared.utils.cli import printing_error
from convo.exceptions import ModelNotPresent

logger = logging.getLogger(__name__)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all shell parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    parser_shell = subparsers.add_parser(
        "shell",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help=(
            "Loads your trained model and lets you talk to your "
            "assistant on the command line."
        ),
    )
    parser_shell.set_defaults(func=get_shell)

    parser_shell.add_argument(
        "--conversation-id",
        default=uuid.uuid4().hex,
        required=False,
        help="Set the conversation ID.",
    )

    run_sub_parsers = parser_shell.add_subparsers()

    shell_nlu_sub_parser = run_sub_parsers.add_parser(
        "nlu",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Interprets messages on the command line using your NLU model.",
    )

    shell_nlu_sub_parser.set_defaults(func=nlu_shell)

    arguments.set_shell_argument(parser_shell)
    arguments.set_shell_nlu_argument(shell_nlu_sub_parser)


def nlu_shell(args: argparse.Namespace):
    from convo.cli.utils import fetch_validated_path
    from convo.shared.constants import DEFAULT_MODEL_PATH 
    from convo.model import fetch_model, fetch_model_subdirectories
    import convo.nlu.run

    args.connector = "cmdline"

    model_class = fetch_validated_path(args.model, "model", DEFAULT_MODEL_PATH )

    try:
        model_path = fetch_model(model_class)
    except ModelNotPresent:
        printing_error(
            "No model found. Train a model before running the "
            "server using `convo train nlu`."
        )
        return

    _, nlu_model = fetch_model_subdirectories(model_path)

    if not nlu_model:
        printing_error(
            "No NLU model found. Train a model before running the "
            "server using `convo train nlu`."
        )
        return

    telemetry.traverse_shell_started("nlu")
    convo.nlu.execute.run_cmd(nlu_model)


def get_shell(args: argparse.Namespace):
    from convo.cli.utils import fetch_validated_path
    from convo.shared.constants import DEFAULT_MODEL_PATH 
    from convo.model import fetch_model, fetch_model_subdirectories

    args.connector = "cmdline"

    model = fetch_validated_path(args.model, "model", DEFAULT_MODEL_PATH )

    try:
        model_path = fetch_model(model)
    except ModelNotPresent:
        printing_error(
            "No model found. Train a model before running the "
            "server using `convo train`."
        )
        return

    model_core, model_nlu = fetch_model_subdirectories(model_path)

    if not model_core:
        import convo.nlu.run

        telemetry.traverse_shell_started("nlu")

        convo.nlu.execute.run_cmd(model_nlu)
    else:
        import convo.cli.run

        telemetry.traverse_shell_started("convo")

        convo.cli.run.run(args)
