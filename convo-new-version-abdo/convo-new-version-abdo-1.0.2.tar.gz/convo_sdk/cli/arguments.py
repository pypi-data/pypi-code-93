import argparse

from convo_sdk.constants import SERVER_PORT_DEFAULT


def action_argument(action):
    if "/" in action:
        raise argparse.ArgumentTypeError(
            "Invalid actions format. Actions file should be a python module "
            "and passed with module notation (e.g. directory.actions)."
        )
    else:
        return action


def add_end_point_args(parser):
    parser.add_argument(
        "-p",
        "--port",
        default=SERVER_PORT_DEFAULT,
        type=int,
        help="port to run the server at",
    )
    parser.add_argument(
        "--cors",
        nargs="*",
        type=str,
        help="enable CORS for the passed origin. Use * to whitelist all origins",
    )
    parser.add_argument(
        "--actions",
        type=action_argument,
        default=None,
        help="name of action package to be loaded",
    )
    parser.add_argument(
        "--ssl-keyfile",
        default=None,
        help="Set the SSL certificate to create a TLS secured server.",
    )
    parser.add_argument(
        "--ssl-certificate",
        default=None,
        help="Set the SSL certificate to create a TLS secured server.",
    )
    parser.add_argument(
        "--ssl-password",
        default=None,
        help="If your ssl-keyfile is protected by a password, you can specify it "
        "using this paramer.",
    )
    parser.add_argument(
        "--auto-reload",
        help="Enable auto-reloading of modules containing Action subclasses.",
        action="store_true",
    )
