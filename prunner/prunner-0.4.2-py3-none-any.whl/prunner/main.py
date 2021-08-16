#!/bin/python3
import argparse
import os

from prunner.ImmutableDict import ImmutableDict
from prunner.executioner import Executioner
from prunner.util import convert_args_to_dict


def parse_arguments(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="The configuration directory to use. Default is $PWD.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose (for debugging pipeline)."
    )
    parser.add_argument(
        "--dryrun",
        "-n",
        action="store_true",
        help="Dry-run. Don't execute local scripts.",
    )
    parser.add_argument(
        "PIPELINE", help="The name of the pipeline to run", default="DEFAULT"
    )
    parser.add_argument(
        "ARGS",
        help="The rest of the args get passed to the pipeline.",
        nargs=argparse.REMAINDER,
    )
    parsed_args = parser.parse_args(args)
    config_dir = (
        os.path.abspath(parsed_args.config) if parsed_args.config else os.getcwd()
    )
    print(config_dir, parsed_args)
    rest_of_args = convert_args_to_dict(parsed_args.ARGS)

    variables = {
        "PRUNNER_CONFIG_DIR": config_dir,
        "DRYRUN": parsed_args.dryrun,
        "VERBOSE": parsed_args.verbose,
        "DEFAULT_PIPELINE": parsed_args.PIPELINE,
        **rest_of_args,
    }
    return variables


def main():
    args = parse_arguments()

    # Import all the environment variables and prefix with `ENV_`
    variables = ImmutableDict({f"ENV_{k}": v for k, v in os.environ.items()})

    # Add the CLI args to variables
    variables.update(args)

    r = Executioner(variables)
    r.execute_pipeline(variables["DEFAULT_PIPELINE"])
    return r


if __name__ == "__main__":
    main()
