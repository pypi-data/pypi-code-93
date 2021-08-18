import asyncio
import logging
import uuid
import os
import shutil
from functools import partial
from typing import Any, List, Optional, Text, Union

import convo.core.utils
import convo.shared.utils.common
import convo.utils
import convo.utils.common
import convo.utils.io
from convo import model, server, telemetry
from convo.constants import ENVIRONMENT_SANIC_BACKLOG
from convo.core import agent, channels, constants
from convo.core.agent import CoreAgent
from convo.core.brokers.broker import CoreEventBroker
from convo.core.channels import console
from convo.core.channels.channel import InputSocket
import convo.core.interpreter
from convo.core.lock_store import LockStore
from convo.core.tracker_store import TrackerStorage
from convo.core.utils import AvailableEndpoints
import convo.shared.utils.io
from sanic import Sanic
from asyncio import AbstractEventLoop

log = logging.getLogger()  # get the root logger


def generate_http_input_channels(
    channel: Optional[Text], credentials_file: Optional[Text]
) -> List["InputSocket"]:
    """Instantiate the chosen input channel."""

    if credentials_file:
        all_cred = convo.shared.utils.io.read_configuration_file(credentials_file)
    else:
        all_cred = {}

    if channel:
        if len(all_cred) > 1:
            log.info(
                "Connecting to channel '{}' which was specified by the "
                "'--connector' argument. Any others channels will be ignored. "
                "To connect to all given channels, omit the '--connector' "
                "argument.".format(channel)
            )
        return [_generate_single_channel(channel, all_cred.get(channel))]
    else:
        return [_generate_single_channel(c, k) for c, k in all_cred.items()]


def _generate_single_channel(channel, credentials) -> Any:
    from convo.core.channels import BUILTIN_CHANNELS

    if channel in BUILTIN_CHANNELS:
        return BUILTIN_CHANNELS[channel].from_cred(credentials)
    else:
        # try to load channel based on class name
        try:
            input_channel_class_name = convo.shared.utils.common.class_name_from_module_path(
                channel
            )
            return input_channel_class_name.from_cred(credentials)
        except (AttributeError, ImportError):
            raise Exception(
                "Failed to find input channel class for '{}'. Unknown "
                "input channel. Check your credentials configuration to "
                "make sure the mentioned channel is not misspelled. "
                "If you are creating your own channel, make sure it "
                "is a proper name of a class in a module.".format(channel)
            )


def _genrate_app_without_api(cors: Optional[Union[Text, List[Text]]] = None):
    app = Sanic(__name__, configure_logging=False)
    server.add_root_route_flow(app)
    server.configurations_cors(app, cors)
    return app


def configure_application(
    input_channels_name: Optional[List["InputSocket"]] = None,
    cors: Optional[Union[Text, List[Text], None]] = None,
    auth_token: Optional[Text] = None,
    enable_api: bool = True,
    response_timeout: int = constants.BY_DEFAULT_RESPONSE_RESULT_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Optional[Text] = None,
    route: Optional[Text] = "/webhooks/",
    port: int = constants.BY_DEFAULT_SERVER_PORT,
    endpoints: Optional[AvailableEndpoints] = None,
    log_file: Optional[Text] = None,
    conversation_id: Optional[Text] = uuid.uuid4().hex,
):
    """Run the agent."""
    from convo import server

    convo.core.utils.configuration_of_file_logging(log, log_file)

    if enable_api:
        app = server.create_application(
            cors_origins=cors,
            auth_token=auth_token,
            response_timeout=response_timeout,
            jwt_secret=jwt_secret,
            jwt_method=jwt_method,
            endpoints=endpoints,
        )
    else:
        app = _genrate_app_without_api(cors)

    if input_channels_name:
        channels.channel.register(input_channels_name, app, route=route)
    else:
        input_channels_name = []

    if log.isEnabledFor(logging.DEBUG):
        convo.core.utils.routes_listing(app)

    # configure async loop logging
    async def configure_asynchronised_logging():
        if log.isEnabledFor(logging.DEBUG):
            convo.utils.io.enable_asynchronous_loop_debugging(asyncio.get_event_loop())

    app.add_task(configure_asynchronised_logging)

    if "cmdline" in {c.name() for c in input_channels_name}:

        async def run_command_line_io(running_app: Sanic):
            """Small wrapper to shut down the server once cmd io is done."""
            await asyncio.sleep(1)  # allow server to start

            await console.record_msg(
                server_url=constants.BY_DEFAULT_SERVER_FORMAT.format("http", port),
                sender_id=conversation_id,
            )

            log.info("Killing Sanic server now.")
            running_app.stop()  # kill the sanic server

        app.add_task(run_command_line_io)

    return app


def serve_app(
    model_path: Optional[Text] = None,
    run_channel: Optional[Text] = None,
    port: int = constants.BY_DEFAULT_SERVER_PORT,
    credentials: Optional[Text] = None,
    cors: Optional[Union[Text, List[Text]]] = None,
    auth_token: Optional[Text] = None,
    enable_api: bool = True,
    response_timeout: int = constants.BY_DEFAULT_RESPONSE_RESULT_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Optional[Text] = None,
    endpoints: Optional[AvailableEndpoints] = None,
    remote_storage: Optional[Text] = None,
    log_file: Optional[Text] = None,
    ssl_certificate: Optional[Text] = None,
    ssl_keyfile: Optional[Text] = None,
    ssl_ca_file: Optional[Text] = None,
    ssl_password: Optional[Text] = None,
    conversation_id: Optional[Text] = uuid.uuid4().hex,
):
    """Run the API entrypoint."""
    from convo import server

    if not run_channel and not credentials:
        run_channel = "cmdline"

    input_channels_name = generate_http_input_channels(run_channel, credentials)

    application = configure_application(
        input_channels_name,
        cors,
        auth_token,
        enable_api,
        response_timeout,
        jwt_secret,
        jwt_method,
        port=port,
        endpoints=endpoints,
        log_file=log_file,
        conversation_id=conversation_id,
    )

    ssl_context_data = server.create_ssl_context(
        ssl_certificate, ssl_keyfile, ssl_ca_file, ssl_password
    )
    rules = "https" if ssl_context_data else "http"

    log.info(
        f"Starting Convo server on {constants.BY_DEFAULT_SERVER_FORMAT.format(rules, port)}"
    )

    application.register_listener(
        partial(load_agent_on_boot, model_path, endpoints, remote_storage),
        "before_server_start",
    )

    # noinspection PyUnresolvedReferences
    async def trash_model_file(_app: Sanic, _loop: Text) -> None:
        if application.agent.model_directory:
            shutil.rmtree(_app.agent.model_directory)

    no_workers = convo.core.utils.no_of_sanic_workers(
        endpoints.lock_store if endpoints else None
    )

    telemetry.traverse_server_start(
        input_channels_name, endpoints, model_path, no_workers, enable_api
    )

    application.register_listener(trash_model_file, "after_server_stop")

    convo.utils.common.updating_sanic_log_level(log_file)
    application.run(
        host="0.0.0.0",
        port=port,
        ssl=ssl_context_data,
        backlog=int(os.environ.get(ENVIRONMENT_SANIC_BACKLOG, "100")),
        workers=no_workers,
    )


# noinspection PyUnusedLocal
async def load_agent_on_boot(
    model_path: Text,
    endpoints: AvailableEndpoints,
    remote_storage: Optional[Text],
    app: Sanic,
    loop: AbstractEventLoop,
):
    """Load an agent.

    Used to be scheduled on server start
    (hence the `app` and `loop` arguments)."""

    # noinspection PyBroadException
    try:
        with model.fetch_model(model_path) as unpacked_model:
            _, nlu_model = model.fetch_model_subdirectories(unpacked_model)
            _interpreter = convo.core.interpreter.generate_interpreter(
                endpoints.nlu or nlu_model
            )
    except Exception:
        log.debug(f"Could not load interpreter from '{model_path}'.")
        _interpreter = None

    _get_broker = CoreEventBroker.generate(endpoints.event_broker)
    _tracker_storage = TrackerStorage.create(endpoints.tracker_store, event_broker=_get_broker)
    _lock_storage = LockStore.create(endpoints.lock_store)

    server_model = endpoints.model if endpoints and endpoints.model else None

    try:
        app.agent = await agent.agent_load(
            model_path,
            model_server=server_model,
            remote_storage=remote_storage,
            interpreter=_interpreter,
            generator=endpoints.nlg,
            tracker_store=_tracker_storage,
            lock_store=_lock_storage,
            action_endpoint=endpoints.action,
        )
    except Exception as e:
        convo.shared.utils.io.raising_warning(
            f"The model at '{model_path}' could not be loaded. " f"Error: {e}"
        )
        app.agent = None

    if not app.agent:
        convo.shared.utils.io.raising_warning(
            "CoreAgent could not be loaded with the provided configuration. "
            "Load default agent without any model."
        )
        app.agent = CoreAgent(
            interpreter=_interpreter,
            generator=endpoints.nlg,
            tracker_store=_tracker_storage,
            action_endpoint=endpoints.action,
            model_server=server_model,
            remote_storage=remote_storage,
        )

    log.info("Convo server is up and running.")
    return app.agent
