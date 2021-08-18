import argparse
import asyncio
import importlib.util
import logging
from multiprocessing import get_context
import os
import signal
import sys
import traceback
from typing import Iterable, List, Optional, Text, Tuple

import aiohttp
from convo.exceptions import DependencyExceptionMissing
import ruamel.yaml as yaml

from convo import telemetry
from convo.cli import SubParsersAction
from convo.cli.arguments import x as arguments
import convo.cli.utils
from convo.constants import (
    BY_DEFAULT_LOGING_LEVEL_X,
    BY_DEFAULT_PORT,
    BY_DEFAULT_X_PORT,
)
from convo.shared.constants import (
    DEFAULT_CONFIGURATION_PATH,
    DEFAULT_CRED_PATH,
    CONVO_DEFAULT_DOMAIN_PATH,
    DEFAULT_END_POINTS_PATH,
    CONVO_DOCUMENTS_BASE_URL,
)
from convo.core.utils import AvailableEndpoints
from convo.shared.exceptions import XTermsError 
import convo.shared.utils.cli
import convo.shared.utils.io
import convo.utils.common
from convo.utils.endpoints import EndpointConfiguration
import convo.utils.io

logger = logging.getLogger(__name__)

DEFAULT_EVENTS_DB = "events.db"


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add all convo x parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """
    x_parser_arguments = {
        "parents": parents,
        "conflict_handler": "resolve",
        "formatter_class": argparse.ArgumentDefaultsHelpFormatter,
    }

    if is_x_installed():
        # we'll only show the help msg for the command if Convo X is actually installed
        x_parser_arguments["help"] = "Starts the Convo X interface."

    shell_parser = subparsers.add_parser("x", **x_parser_arguments)
    shell_parser.set_defaults(func=convo_x)

    arguments.set_x_arguments(shell_parser)


def _convo_service(
    args: argparse.Namespace,
    endpoints: AvailableEndpoints,
    convo_x_url: Optional[Text] = None,
    cred_path: Optional[Text] = None,
):
    """Starts the Convo application."""
    from convo.core.run import serve_application

    # needs separate logging configuration as it is started in its own process
    convo.utils.common.setting_logging_level(args.loglevel)
    convo.utils.io.config_color_logging(args.loglevel)

    if not cred_path:
        cred_path = _prepare_credentials_for_convo_x(
            args.credentials, convo_x_url=convo_x_url
        )

    serve_application(
        endpoints=endpoints,
        port=args.port,
        credentials=cred_path,
        cors=args.cors,
        auth_token=args.auth_token,
        enable_api=True,
        jwt_secret=args.jwt_secret,
        jwt_method=args.jwt_method,
        ssl_certificate=args.ssl_certificate,
        ssl_keyfile=args.ssl_keyfile,
        ssl_ca_file=args.ssl_ca_file,
        ssl_password=args.ssl_password,
    )


def _prepare_credentials_for_convo_x(
    cred_path: Optional[Text], convo_x_url: Optional[Text] = None
) -> Text:
    cred_path = convo.cli.utils.fetch_validated_path(
        cred_path, "credentials", DEFAULT_CRED_PATH, True
    )
    if cred_path:
        cred = convo.shared.utils.io.read_configuration_file(cred_path)
    else:
        cred = {}

    # this makes sure the Convo X is properly configured no matter what
    if convo_x_url:
        cred["convo"] = {"url": convo_x_url}
    dumped_credentials = yaml.dump(cred, default_flow_style=False)
    tmp_credentials = convo.utils.io.create_temp_file(dumped_credentials, "yml")

    return tmp_credentials


def _override_endpoints_for_local_x(
    endpoints: AvailableEndpoints, convo_x_token: Text, convo_x_url: Text
):
    endpoints.model = _fetch_model_endpoint(endpoints.model, convo_x_token, convo_x_url)
    endpoints.event_broker = _fetch_event_broker_endpoint(endpoints.event_broker)


def _fetch_model_endpoint(
    model_terminal: Optional[EndpointConfiguration], convo_x_token: Text, convo_x_url: Text
) -> EndpointConfiguration:
    # If you change that, please run a test with Convo X and speak to the bot
    default_convox_model_server_url = (
        f"{convo_x_url}/projects/default/models/tags/production"
    )

    model_terminal = model_terminal or EndpointConfiguration()

    # Checking if endpoint.yml has existing url, if so give
    # warning we are overwriting the endpoint.yml file.
    custom_url = model_terminal.url

    if custom_url and custom_url != default_convox_model_server_url:
        logger.info(
            f"Ignoring url '{custom_url}' from 'endpoints.yml' and using "
            f"'{default_convox_model_server_url}' instead."
        )

    custom_wait_time_pulls = model_terminal.kwargs.get("wait_time_between_pulls")
    return EndpointConfiguration(
        default_convox_model_server_url,
        token=convo_x_token,
        wait_time_between_pulls=custom_wait_time_pulls or 2,
    )


def _fetch_event_broker_endpoint(
    event_broker_endpoint: Optional[EndpointConfiguration],
) -> EndpointConfiguration:
    import questionary

    default_event_broker_endpoint = EndpointConfiguration(
        type="sql", dialect="sqlite", db=DEFAULT_EVENTS_DB
    )
    if not event_broker_endpoint:
        return default_event_broker_endpoint
    elif not _is_correct_action_broker(event_broker_endpoint):
        convo.shared.utils.cli.printing_error(
            f"Convo X currently only supports a SQLite event broker with path "
            f"'{DEFAULT_EVENTS_DB}' when running locally. You can deploy Convo X "
            f"with Docker ({CONVO_DOCUMENTS_BASE_URL}/installation-and-setup/"
            f"docker-compose-quick-install/) if you want to use other event broker "
            f"configurations."
        )
        continue_with_default_event_broker = questionary.confirm(
            "Do you want to continue with the default SQLite event broker?"
        ).ask()

        if not continue_with_default_event_broker:
            sys.exit(0)

        return default_event_broker_endpoint
    else:
        return event_broker_endpoint


def _is_correct_action_broker(event_broker: EndpointConfiguration) -> bool:
    return all(
        [
            event_broker.type == "sql",
            event_broker.kwargs.get("dialect", "").lower() == "sqlite",
            event_broker.kwargs.get("db") == DEFAULT_EVENTS_DB,
        ]
    )


def start_convo_for_local_convo_x(args: argparse.Namespace, convo_x_token: Text):
    """Starts the Convo X API with Convo as a background process."""

    cred_path, terminal_path = _fetch_cred_and_endpoints_paths(args)
    terminal = AvailableEndpoints.read_last_points(terminal_path)

    convo_x_url = f"http://localhost:{args.convo_x_port}/api"
    _override_endpoints_for_local_x(terminal, convo_x_token, convo_x_url)

    vars(args).update(
        dict(
            nlu_model=None,
            cors="*",
            auth_token=args.auth_token,
            enable_api=True,
            endpoints=terminal,
        )
    )

    ctx = get_context("spawn")
    p = ctx.Process(
        target=_convo_service, args=(args, terminal, convo_x_url, cred_path)
    )
    p.daemon = True
    p.start()
    return p


def is_x_installed() -> bool:
    """Check if Convo X is installed."""

    # we could also do something like checking if `import convox` works,
    # the issue with that is that it actually does import the package and this
    # takes some time that we don't want to spend when booting the CLI
    return importlib.util.find_spec("convox") is not None


def generate_convo_x_token(length: int = 16):
    """Generate a hexadecimal secret token used to access the Convo X API.

    A new token is generated on every `convo x` command.
    """

    from secrets import token_hex

    return token_hex(length)


def _configuration_logging(args: argparse.Namespace):
    from convo.core.utils import configure_file_logging
    from convo.utils.common import setting_logging_level

    log_levels = args.loglevel or BY_DEFAULT_LOGING_LEVEL_X

    if isinstance(log_levels, str):
        log_levels = logging.getLevelName(log_levels)

    logging.basicConfig(level=log_levels)
    convo.utils.io.config_color_logging(args.loglevel)

    setting_logging_level(log_levels)
    configure_file_logging(logging.root, args.log_file)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.ERROR)

    if not log_levels == logging.DEBUG:
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger("py.warnings").setLevel(logging.ERROR)


def is_project_setup(args: argparse.Namespace, project_path: Text) -> bool:
    configuration_path = _fetch_configuration_path(args)
    mandatory_file = [configuration_path, CONVO_DEFAULT_DOMAIN_PATH]

    for f in mandatory_file:
        if not os.path.exists(os.path.join(project_path, f)):
            return False

    return True


def _validate_convo_x_start(args: argparse.Namespace, project_path: Text):
    if not is_x_installed():
        convo.shared.utils.cli.printing_error_exit(
            "Convo X is not installed. The `convo x` "
            "command requires an installation of Convo X. "
            "Instructions on how to install Convo X can be found here: "
            "https://convo.com/docs/convo-x/."
        )

    if args.port == args.convo_x_port:
        convo.shared.utils.cli.printing_error_exit(
            "The port for Convo X '{}' and the port of the Convo server '{}' are the "
            "same. We need two different ports, one to run Convo X (e.g. delivering the "
            "UI) and another one to run a normal Convo server.\nPlease specify two "
            "different ports using the arguments '--port' and '--convo-x-port'.".format(
                args.convo_x_port, args.port
            )
        )

    if not is_project_setup(args, project_path):
        convo.shared.utils.cli.printing_error_exit(
            "This dir is not a valid Convo project. Use 'convo init' "
            "to create a new Convo project or switch to a valid Convo project "
            "dir (see https://convo.com/docs/convo/command-line-interface#convo-init)."
        )

    _verify_domain(os.path.join(project_path, CONVO_DEFAULT_DOMAIN_PATH))

    if args.data and not os.path.exists(args.data):
        convo.shared.utils.cli.printing_warning(
            "The provided data path ('{}') does not exists. Convo X will start "
            "without any training data.".format(args.data)
        )


def _verify_domain(domain_path: Text):
    from convo.shared.core.domain import Domain, InvalidDomain

    try:
        Domain.load(domain_path)
    except InvalidDomain as e:
        convo.shared.utils.cli.printing_error_exit(
            "The provided domain file could not be loaded. " "Error: {}".format(e)
        )


def convo_x(args: argparse.Namespace):
    from convo.cli.utils import signal_handler

    signal.signal(signal.SIGINT, signal_handler)

    _configuration_logging(args)

    if args.production:
        execute_in_production(args)
    else:
        execute_locally(args)


async def _pull_runtime_configuration_from_server(
    config_endpoint: Optional[Text],
    attempts: int = 60,
    wait_time_between_pulls: float = 5,
    keys: Iterable[Text] = ("endpoints", "credentials"),
) -> Optional[List[Text]]:
    """Pull runtime config from `config_endpoint`.

    Returns a list of convo_paths to yaml data_dumps, each containing the contents of one of
    `keys`.
    """

    while attempts:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config_endpoint) as resp:
                    if resp.status == 200:
                        rjs = await resp.json()
                        try:
                            return [
                                convo.utils.io.create_temp_file(rjs[k])
                                for k in keys
                            ]
                        except KeyError as e:
                            convo.shared.utils.cli.printing_error_exit(
                                "Failed to find key '{}' in runtime config. "
                                "Exiting.".format(e)
                            )
                    else:
                        logger.debug(
                            "Failed to get a proper response from remote "
                            "server. Status Code: {}. Response: '{}'"
                            "".format(resp.status, await resp.text())
                        )
        except aiohttp.ClientError as e:
            logger.debug(f"Failed to connect to server. Retrying. {e}")

        await asyncio.sleep(wait_time_between_pulls)
        attempts -= 1

    convo.shared.utils.cli.printing_error_exit(
        "Could not fetch runtime config from server at '{}'. "
        "Exiting.".format(config_endpoint)
    )


def execute_in_production(args: argparse.Namespace):
    from convo.shared.utils.cli import printing_success

    printing_success("Starting Convo X in production mode... 🚀")

    cred_path, terminal_path = _fetch_cred_and_endpoints_paths(args)
    terminals = AvailableEndpoints.read_last_points(terminal_path)

    _convo_service(args, terminals, None, cred_path)


def _fetch_configuration_path(args: argparse.Namespace,) -> Optional[Text]:
    configuration_path = convo.cli.utils.fetch_validated_path(
        args.config, "config", DEFAULT_CONFIGURATION_PATH
    )

    return configuration_path


def _fetch_cred_and_endpoints_paths(
    args: argparse.Namespace,
) -> Tuple[Optional[Text], Optional[Text]]:
    config_endpoint = args.config_endpoint
    if config_endpoint:
        endpoints_config_path, cred_path = convo.utils.common.running_in_loop(
            _pull_runtime_configuration_from_server(config_endpoint)
        )

    else:
        endpoints_config_path = convo.cli.utils.fetch_validated_path(
            args.endpoints, "endpoints", DEFAULT_END_POINTS_PATH, True
        )
        cred_path = None

    return cred_path, endpoints_config_path


def execute_locally(args: argparse.Namespace):
    try:
        # noinspection PyUnresolvedReferences
        from convox.community import local  # pytype: disable=import-error
    except ModuleNotFoundError:
        raise DependencyExceptionMissing(
            f"Convo X does not seem to be installed, but it is needed for this CLI command."
            f"You can find more information on how to install Convo X in local mode"
            f"in the documentation: "
            f"{CONVO_DOCUMENTS_BASE_URL}/installation-and-setup/install/local-mode"
        )

    args.convo_x_port = args.convo_x_port or BY_DEFAULT_X_PORT
    args.port = args.port or BY_DEFAULT_PORT

    project_path_flow = "."

    _validate_convo_x_start(args, project_path_flow)

    convo_x_token = generate_convo_x_token()
    processes = start_convo_for_local_convo_x(args, convo_x_token=convo_x_token)

    configuration_path = _fetch_configuration_path(args)

    telemetry.track_convo_x_local()

    # noinspection PyBroadException
    try:
        local.main(
            args, project_path_flow, args.data, token=convo_x_token, config_path=configuration_path
        )
    except XTermsError :
        # User didn't accept the Convo X terms.
        pass
    except Exception:
        print(traceback.format_exc())
        convo.shared.utils.cli.printing_error(
            "Sorry, something went wrong (see error above). Make sure to start "
            "Convo X with valid data and valid domain and config files. Please, "
            "also check any warnings that popped up.\nIf you need help fixing "
            "the issue visit our forum: https://forum.convo.com/."
        )
    finally:
        processes.terminate()
