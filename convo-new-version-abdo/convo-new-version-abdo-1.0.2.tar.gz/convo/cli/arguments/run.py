import argparse
from typing import Union

from convo.cli.arguments.default_arguments import add_model_parameter, add_end_point_parameter
from convo.core import constants


def set_run_argument(parser: argparse.ArgumentParser):
    """Arguments for running Convo directly using `convo run`."""
    add_model_parameter(parser)
    add_new_server_arguments(parser)


def set_run_action_argument(parser: argparse.ArgumentParser):
    """Set arguments for running Convo SDK."""
    import convo_sdk.cli.arguments as sdk

    sdk.add_end_point_args(parser)


# noinspection PyProtectedMember
def add_new_port_argument(parser: Union[argparse.ArgumentParser, argparse._ArgumentGroup]):
    """Add an argument for port."""
    parser.add_argument(
        "-p",
        "--port",
        default=constants.BY_DEFAULT_SERVER_PORT,
        type=int,
        help="Port to run the server at.",
    )


def add_new_server_arguments(parser: argparse.ArgumentParser):
    """Add arguments for running API endpoint."""
    parser.add_argument(
        "--log-file",
        type=str,
        # Convo should not log to a file by default, otherwise there will be problems
        # when running on OpenShift
        default=None,
        help="Store logs in specified file.",
    )
    add_end_point_parameter(
        parser,
        help_text="Configuration file for the model server and the connectors as a "
        "yml file.",
    )

    server_args = parser.add_argument_group("Server Settings")

    add_new_port_argument(server_args)

    server_args.add_argument(
        "-t",
        "--auth-token",
        type=str,
        help="Enable token based authentication. Requests need to provide "
        "the token to be accepted.",
    )
    server_args.add_argument(
        "--cors",
        nargs="*",
        type=str,
        help="Enable CORS for the passed origin. Use * to whitelist all origins.",
    )
    server_args.add_argument(
        "--enable-api",
        action="store_true",
        help="Start the web server API in addition to the input channel.",
    )
    server_args.add_argument(
        "--response-timeout",
        default=constants.BY_DEFAULT_RESPONSE_RESULT_TIMEOUT,
        type=int,
        help="Maximum time a response can take to process (sec).",
    )
    server_args.add_argument(
        "--remote-storage",
        help="Set the remote location where your Convo model is stored, e.g. on AWS.",
    )
    server_args.add_argument(
        "--ssl-certificate",
        help="Set the SSL Certificate to create a TLS secured server.",
    )
    server_args.add_argument(
        "--ssl-keyfile", help="Set the SSL Keyfile to create a TLS secured server."
    )
    server_args.add_argument(
        "--ssl-ca-file",
        help="If your SSL certificate needs to be verified, you can specify the CA file "
        "using this parameter.",
    )
    server_args.add_argument(
        "--ssl-password",
        help="If your ssl-keyfile is protected by a password, you can specify it "
        "using this paramer.",
    )

    channel_arguments = parser.add_argument_group("Channels")
    channel_arguments.add_argument(
        "--credentials",
        default=None,
        help="Authentication credentials for the connector as a yml file.",
    )
    channel_arguments.add_argument(
        "--connector", type=str, help="Service to connect to."
    )

    jwt_auth = parser.add_argument_group("JWT Authentication")
    jwt_auth.add_argument(
        "--jwt-secret",
        type=str,
        help="Public key for asymmetric JWT methods or shared secret"
        "for symmetric methods. Please also make sure to use "
        "--jwt-method to select the method of the signature, "
        "otherwise this argument will be ignored.",
    )
    jwt_auth.add_argument(
        "--jwt-method",
        type=str,
        default="HS256",
        help="Method used for the signature of the JWT authentication payload.",
    )
