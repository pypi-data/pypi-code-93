import logging

from convo_sdk import utils
from convo_sdk.endpoint import creating_args_parser, execute


def main_from_args(args):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("matplotlib").setLevel(logging.WARN)

    utils.color_logging_config(args.loglevel)
    utils.updating_sanic_log_level()

    execute(
        args.actions,
        args.port,
        args.cors,
        args.ssl_certificate,
        args.ssl_keyfile,
        args.ssl_password,
        args.auto_reload,
    )


def main():
    # Running as standalone python application
    arg_parser = creating_args_parser()
    cmdline_args = arg_parser.parse_args()

    main_from_args(cmdline_args)


if __name__ == "__main__":
    main()
