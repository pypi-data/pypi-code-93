import argparse
import logging
import os
from typing import List, Text

from convo.cli import SubParsersAction
from convo.cli.arguments import run as arguments
import convo.cli.utils
import convo.shared.utils.cli
from convo.shared.constants import (
    DOCUMENTS_BASE_URL,
    DEFAULT_END_POINTS_PATH,
    DEFAULT_CRED_PATH,
    DEFAULT_ACTION_PATH,
    DEFAULT_MODEL_PATH ,
)
from convo.exceptions import ModelNotPresent

logger = logging.getLogger(__name__)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all run parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    execute_parser = subparsers.add_parser(
        "run",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts a Convo server with your trained model.",
    )
    execute_parser.set_defaults(func=run)

    run_sub_parser = execute_parser.add_subparsers()
    sdk_sub_parsers = run_sub_parser.add_parser(
        "actions",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Runs the action server.",
    )
    sdk_sub_parsers.set_defaults(func=run_activities)

    arguments.set_run_argument(execute_parser)
    arguments.set_run_action_argument(sdk_sub_parsers)


def run_activities(args: argparse.Namespace):
    import convo_sdk.__main__ as sdk

    args.actions = args.actions or DEFAULT_ACTION_PATH

    sdk.main_from_args(args)


def verify_model_path(model_path: Text, parameter: Text, default: Text):

    if model_path is not None and not os.path.exists(model_path):
        reason_string = f"'{model_path}' not found."
        if model_path is None:
            reason_string = f"Parameter '{parameter}' not set."

        logger.debug(f"{reason_string} Using default location '{default}' instead.")

        os.makedirs(default, exist_ok=True)
        model_path = default

    return model_path


def run(args: argparse.Namespace):
    import convo.run

    args.endpoints = convo.cli.utils.fetch_validated_path(
        args.endpoints, "endpoints", DEFAULT_END_POINTS_PATH, True
    )
    args.credentials = convo.cli.utils.fetch_validated_path(
        args.credentials, "credentials", DEFAULT_CRED_PATH, True
    )

    if args.enable_api:
        if not args.remote_storage:
            args.model = verify_model_path(args.model, "model", DEFAULT_MODEL_PATH )
        convo.run(**vars(args))
        return

    # if the API is not enable you cannot start without a model
    # make sure either a model server, a remote storage, or a local model is
    # configured

    from convo.model import fetch_model
    from convo.core.utils import AvailableEndpoints

    # start server if remote storage is configured
    if args.remote_storage is not None:
        convo.run(**vars(args))
        return

    # start server if model server is configured
    terminals = AvailableEndpoints.read_last_points(args.endpoints)
    local_model = terminals.model if terminals and terminals.model else None
    if local_model is not None:
        convo.run(**vars(args))
        return

    # start server if local model found
    args.model = verify_model_path(args.model, "model", DEFAULT_MODEL_PATH )
    local_model_set = True
    try:
        fetch_model(args.model)
    except ModelNotPresent:
        local_model_set = False

    if local_model_set:
        convo.run(**vars(args))
        return

    convo.shared.utils.cli.printing_error(
        f"No model found. You have three options to provide a model:\n"
        f"1. Configure a model server in the endpoint configuration and provide "
        f"the configuration via '--endpoints'.\n"
        f"2. Specify a remote storage via '--remote-storage' to load the model "
        f"from.\n"
        f"3. Train a model before running the server using `convo train` and "
        f"use '--model' to provide the model path.\n"
        f"For more information check {DOCUMENTS_BASE_URL}/model-storage."
    )
