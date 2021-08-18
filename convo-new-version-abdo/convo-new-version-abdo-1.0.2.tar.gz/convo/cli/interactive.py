import argparse
import logging
import os
from typing import List, Optional, Text

from convo import model
from convo.cli import SubParsersAction
from convo.cli.arguments import interactive as arguments
import convo.cli.train as train
import convo.cli.utils
from convo.shared.constants import DEFAULT_END_POINTS_PATH, DEFAULT_MODEL_PATH 
from convo.shared.importers.importer import TrainingDataImporter
import convo.shared.utils.cli
import convo.utils.common

log = logging.getLogger(__name__)


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all interactive cli parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    collaborative_parser = subparsers.add_parser(
        "interactive",
        conflict_handler="resolve",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts an interactive learning session to create new training data for a "
        "Convo model by chatting.",
    )
    collaborative_parser.set_defaults(func=interactive, core_only=False)

    collaborative_subparsers = collaborative_parser.add_subparsers()
    collaborative_core_parser = collaborative_subparsers.add_parser(
        "core",
        conflict_handler="resolve",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Starts an interactive learning session model to create new training data "
        "for a Convo Core model by chatting. Uses the 'RegexInterpreter', i.e. "
        "`/<intent>` input format.",
    )
    collaborative_core_parser.set_defaults(func=interactive, core_only=True)

    arguments.set_interactive_argument(collaborative_parser)
    arguments.set_interactive_core_argument(collaborative_core_parser)


def interactive(args: argparse.Namespace) -> None:
    _set_not_required_arguments(args)
    files_importer = TrainingDataImporter.load_from_configuration(
        args.config, args.domain, args.data if not args.core_only else [args.stories]
    )

    if args.model is None:
        stories_graph = convo.utils.common.running_in_loop(files_importer.fetch_stories())
        if not stories_graph or stories_graph.is_empty():
            convo.shared.utils.cli.printing_error_exit(
                "Could not run interactive learning without either core "
                "data or a model containing core data."
            )

        zip_model = train.supervise_core(args) if args.core_only else train.train(args)
        if not zip_model:
            convo.shared.utils.cli.printing_error_exit(
                "Could not train an initial model. Either pass convo_paths "
                "to the relevant training files (`--data`, `--config`, `--domain`), "
                "or use 'convo train' to train a model."
            )
    else:
        zip_model = fetch_provided_model(args.model)
        if not (zip_model and os.path.exists(zip_model)):
            convo.shared.utils.cli.printing_error_exit(
                f"Interactive learning process cannot be started as no "
                f"initial model was found at path '{args.model}'.  "
                f"Use 'convo train' to train a model."
            )
        if not args.skip_visualization:
            log.info(f"Loading visualization data from {args.data}.")

    perform_collaborative_learning(args, zip_model, files_importer)


def _set_not_required_arguments(args: argparse.Namespace) -> None:
    args.fixed_model_name = None
    args.store_uncompressed = False


def perform_collaborative_learning(
    args: argparse.Namespace, zipped_model: Text, file_importer: TrainingDataImporter
) -> None:
    from convo.core.train import have_interactive_learning

    args.model = zipped_model

    with model.unpacking_model(zipped_model) as model_path:
        args.core, args.nlu = model.fetch_model_subdirectories(model_path)
        if args.core is None:
            convo.shared.utils.cli.printing_error_exit(
                "Can not run interactive learning on an NLU-only model."
            )

        args.endpoints = convo.cli.utils.fetch_validated_path(
            args.endpoints, "endpoints", DEFAULT_END_POINTS_PATH, True
        )

        have_interactive_learning(args, file_importer)


def fetch_provided_model(arg_model: Text) -> Optional[Text]:
    model_path_flow = convo.cli.utils.fetch_validated_path(
        arg_model, "model", DEFAULT_MODEL_PATH 
    )

    if os.path.isdir(model_path_flow):
        model_path_flow = model.fetch_latest_model(model_path_flow)

    return model_path_flow
