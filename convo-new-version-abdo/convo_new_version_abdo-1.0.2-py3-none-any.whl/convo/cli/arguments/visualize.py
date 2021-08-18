import argparse

from convo.cli.arguments.default_arguments import (
    add_config_parameter,
    add_domain_parameter,
    add_stories_parameter,
    add_out_parameter,
    add_nlu_data_parameter,
)


def set_visualize_stories_arguments(parser: argparse.ArgumentParser):
    add_domain_parameter(parser)
    add_stories_parameter(parser)
    add_config_parameter(parser)

    add_out_parameter(
        parser,
        default="graph.html",
        help_text="Filename of the output path, e.g. 'graph.html'.",
    )

    parser.add_argument(
        "--max-history",
        default=2,
        type=int,
        help="Max history to consider when merge convo_paths in the output graph.",
    )

    add_nlu_data_parameter(
        parser,
        default=None,
        help_text="File or folder containing your NLU data, "
        "used to insert example messages into the graph.",
    )
