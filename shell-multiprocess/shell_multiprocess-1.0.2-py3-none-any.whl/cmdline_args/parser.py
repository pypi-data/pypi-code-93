import argparse
from pathlib import Path


def get_parsed_cmdline_args(cmdline_args=None):
    desc = "Script which reads a file with shell commands and runs them in parallel processes."
    parser = argparse.ArgumentParser(description=desc)
    _register_arguments(parser)
    return parser.parse_args(cmdline_args)


def _register_arguments(parser):

    parser.add_argument(
        "filename",
        type=_existing_filepath,
        help="Filename with commands",
    )
    parser.add_argument(
        "processes",
        type=_processes_is_int,
        help="Amount of parallel processes",
    )
    parser.add_argument(
        "-s",
        "--soft-kill",
        action="store_true",
        help="Sends SIGINT signal to subprocesses instead of SIGKILL during cleanup after CTRL-C",
    )

    parser.add_argument(
        "-l",
        "--log-to-file",
        action="store_true",
        help="Send multiprocess sumup to file with name 'multiprocess_{pid}.log'. "
        "Log is being update each time an event occurs and can be viewed to monitor progress.",
    )


def _processes_is_int(processes):
    try:
        return int(processes)
    except ValueError as er:
        raise argparse.ArgumentTypeError(
            f"Invalid process count value '{processes!s}'."
            f" Please provide an integer for amount of workers to be used."
        ) from er


def _existing_filepath(filename: str) -> Path:
    filepath = Path(filename)
    if not filepath.exists():
        raise argparse.ArgumentTypeError(
            f'File "{filepath.absolute()!s}" does not exist. Please provide an existing file name.'
        )
    else:
        return filepath
