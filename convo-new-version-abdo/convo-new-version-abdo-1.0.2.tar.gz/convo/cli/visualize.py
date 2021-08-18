import argparse
import os
from typing import List

from convo.cli import SubParsersAction
from convo.cli.arguments import visualize as arguments
from convo.shared.constants import CONVO_DEFAULT_DATA_PATH 
import convo.shared.data
import convo.utils.common


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all visualization parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    imaginary_parser = subparsers.add_parser(
        "visualize",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Visualize stories.",
    )
    imaginary_parser.set_defaults(func=imaginary_stories)

    arguments.set_visualize_stories_arguments(imaginary_parser)


def imaginary_stories(args: argparse.Namespace):
    import convo.core.visualize

    args.stories = convo.shared.data.get_core_dir(args.stories)
    if args.nlu is None and os.path.exists(CONVO_DEFAULT_DATA_PATH ):
        args.nlu = convo.shared.data.get_nlu_directory(CONVO_DEFAULT_DATA_PATH)

    convo.utils.common.running_in_loop(
        convo.core.anticipate(
            args.config, args.domain, args.stories, args.nlu, args.out, args.max_history
        )
    )
