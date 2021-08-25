import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from consolebundle.CommandManager import CommandManager
from consolebundle.ConsoleArgumentParser import ConsoleArgumentParser
from pyfonycore.bootstrap.config import config_reader


def format_full_command_help(help_message, command_name):
    formatted_command_string = " ".join(command_name)
    help_message = help_message.replace("[command_name [command_name ...]]", formatted_command_string)
    help_message = help_message.replace("command_name", formatted_command_string)
    return help_message

def log_commands(command_manager: CommandManager, logger):
    print("\n[Available commands]:", flush=True)
    for existing_command in command_manager.get_commands():
        logger.info(existing_command.get_command().replace(":", " ") + " - " + existing_command.get_description())

def log_subcommands(command_manager: CommandManager, command_name: list, logger):
    print("\n[Available space-separated commands]:", flush=True)
    for existing_command in command_manager.get_commands():
        prefixes_same, sep = command_manager.prefixes_same_on_separators(existing_command.get_command(), command_name)
        if prefixes_same:
            logger.info(
                f"{' '.join(existing_command.get_command().split(sep))} - " + existing_command.get_description())

def run_command():
    _load_dot_env()
    arguments_parser = _create_arguments_parser()

    known_args = arguments_parser.parse_known_args()[0]

    bootstrap_config = config_reader.read()
    container = bootstrap_config.container_init_function(known_args.env, bootstrap_config)
    command_manager: CommandManager = container.get("consolebundle.CommandManager")

    logger = container.get("consolebundle.logger")
    logger.warning("Running command in {} environment".format(known_args.env.upper()))

    if len(sys.argv) < 2 or (known_args.help_selected and len(known_args.command_name) < 1):
        logger.error("Command not specified, example usage: console mynamespace:mycommand")

        log_commands(command_manager, logger)

        sys.exit(0)
    elif command_manager.command_prefix_only(known_args.command_name):

        log_subcommands(command_manager, known_args.command_name, logger)

        sys.exit(0)

    try:
        command = command_manager.get_by_name(known_args.command_name)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    command.configure(arguments_parser)
    arguments_parser.set_command_name(known_args.command_name)

    if known_args.help_selected:
        help_message = arguments_parser.format_help()

        logger.info(format_full_command_help(help_message, known_args.command_name))

        sys.exit(0)
    else:
        known_args = arguments_parser.parse_known_args()[0]
        command.run(known_args)


def _create_arguments_parser():
    arguments_parser = ConsoleArgumentParser(add_help=None)
    arguments_parser.add_argument("-h", "--help", dest="help_selected",
                                  action='store_const', const=True, default=False)
    arguments_parser.add_argument(dest="command_name", nargs='*')

    env_kwargs = dict(required=False, help="Environment")

    if "APP_ENV" in os.environ:
        env_kwargs["default"] = os.environ["APP_ENV"]

    arguments_parser.add_argument("-e", "--env", **env_kwargs)

    return arguments_parser


def _load_dot_env():
    dot_env_file_path = Path.cwd() / ".env"

    if dot_env_file_path.exists():
        load_dotenv(dotenv_path=str(dot_env_file_path), override=True)


if __name__ == "__main__":
    run_command()
