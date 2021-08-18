import argparse

from convo.cli.arguments.default_arguments import add_model_parameter
from convo.cli.arguments.run import add_new_server_arguments


def set_shell_argument(parser: argparse.ArgumentParser):
    add_model_parameter(parser)
    add_new_server_arguments(parser)


def set_shell_nlu_argument(parser: argparse.ArgumentParser):
    add_model_parameter(parser)
