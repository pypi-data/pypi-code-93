import asyncio
import functools
import logging
import multiprocessing
import os
import tempfile
import traceback
import typing
from functools import reduce, wraps
from inspect import isawaitable
from pathlib import Path
from typing import Any, Callable, List, Optional, Text, Union, Dict

from sanic import Sanic, response
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_cors import CORS
from sanic_jwt import Initialize, exceptions

import convo
import convo.core.utils
import convo.shared.utils.common
import convo.shared.utils.io
import convo.utils.endpoints
import convo.utils.io
from convo.shared.core.training_data.story_writer.yaml_story_writer import (
    YAMLStoryAuthor,
)
from convo.shared.nlu.training_data.formats import ConvoYAMLReviewer
from convo.utils import common as common_utils
from convo import model
from convo.constants import BY_DEFAULT_RESPONSE_RESULT_TIMEOUT, MIN_COMPATIBLE_VER
from convo.shared.constants import (
    TRAINING_DATA_DOCUMENTS_URL,
    DOCUMENTS_BASE_URL,
    CONVO_DEFAULT_SENDER_ID ,
    CONVO_DEFAULT_DOMAIN_PATH,
    DEFAULT_MODEL_PATH ,
)
from convo.shared.core.domain import InvalidDomain
from convo.core.agent import CoreAgent
from convo.core.brokers.broker import CoreEventBroker
from convo.core.channels.channel import (
    CollectOutputChannel,
    OutputSocket,
    UserMsg,
)
from convo.shared.core.events import Event
from convo.core.lock_store import LockStore
from convo.core.test import test
from convo.core.tracker_store import TrackerStorage
from convo.shared.core.trackers import DialogueStateTracer, releaseVerbosity
from convo.core.utils import AvailableEndpoints
from convo.nlu.emulators.no_emulator import NotEmulator
from convo.nlu.test import run_eval
from convo.utils.endpoints import EndpointConfiguration

if typing.TYPE_CHECKING:
    from ssl import SSLContext
    from convo.core.processor import MsgProcessor

logger = logging.getLogger(__name__)

JSON_CONTENT_TYPE = "application/json"
YAML_CONTENT_TYPE = "application/x-yaml"

OUTPUT_CHANNEL_QUERY_KEY = "output_channel"
USE_LATEST_INPUT_CHANNEL_AS_OUTPUT_CHANNEL = "latest"
EXECUTE_SIDE_EFFECTS_QUERY_KEY = "execute_side_effects"


class ErrResponse(Exception):
    def __init__(
        self,
        status: int,
        reason: Text,
        message: Text,
        details: Any = None,
        help_url_path: Optional[Text] = None,
    ) -> None:
        self.error_info = {
            "version": convo.__version__,
            "status": "failure",
            "message": message,
            "reason": reason,
            "details": details or {},
            "help": help_url_path,
            "code": status,
        }
        self.status = status
        logger.error(message)
        super(ErrResponse, self).__init__()


def documents(sub_url: Text) -> Text:
    """Create a url to a subpart of the docs."""
    return DOCUMENTS_BASE_URL + sub_url


def confirm_loaded_agent(app: Sanic, require_core_is_ready=False):
    """Wraps a request handler ensuring there is a loaded and usable agent.

    Require the agent to have a loaded Core model if `require_core_is_ready` is
    `True`.
    """

    def decorator_func(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # noinspection PyUnresolvedReferences
            if not app.agent or not (
                app.agent.is_core_prepared()
                if require_core_is_ready
                else app.agent.is_prepared()
            ):
                raise ErrResponse(
                    409,
                    "Conflict",
                    "No agent loaded. To continue processing, a "
                    "model of a trained agent needs to be loaded.",
                    help_url_path=documents("/user-guide/configuring-http-api/"),
                )

            return f(*args, **kwargs)

        return decorated

    return decorator_func


def requires_authorization(app: Sanic, token: Optional[Text] = None) -> Callable[[Any], Any]:
    """Wraps a request handler with token authentication."""

    def decorator(f: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        def conversation_id_from_args(args: Any, kwargs: Any) -> Optional[Text]:
            argnames = convo.shared.utils.common.args_of(f)

            try:
                sender_id_arg_idx = argnames.index("conversation_id")
                if "conversation_id" in kwargs:  # try to fetch from kwargs first
                    return kwargs["conversation_id"]
                if sender_id_arg_idx < len(args):
                    return args[sender_id_arg_idx]
                return None
            except ValueError:
                return None

        def enough_scope(request, *args: Any, **kwargs: Any) -> Optional[bool]:
            jwt_data = request.app.auth.extract_payload(request)
            user = jwt_data.get("user", {})

            username = user.get("username", None)
            role = user.get("role", None)

            if role == "admin":
                return True
            elif role == "user":
                conversation_id = conversation_id_from_args(args, kwargs)
                return conversation_id is not None and username == conversation_id
            else:
                return False

        @wraps(f)
        async def fetch_decorated(request: Request, *args: Any, **kwargs: Any) -> Any:

            provided = request.args.get("token", None)

            # noinspection PyProtectedMember
            if token is not None and provided == token:
                result = f(request, *args, **kwargs)
                if isawaitable(result):
                    result = await result
                return result
            elif app.config.get("USE_JWT") and request.app.auth.is_authenticated(
                request
            ):
                if enough_scope(request, *args, **kwargs):
                    result = f(request, *args, **kwargs)
                    if isawaitable(result):
                        result = await result
                    return result
                raise ErrResponse(
                    403,
                    "NotAuthorized",
                    "User has insufficient permissions.",
                    help_url_path=documents(
                        "/user-guide/configuring-http-api/#security-considerations"
                    ),
                )
            elif token is None and app.config.get("USE_JWT") is None:
                # authentication is disabled
                result = f(request, *args, **kwargs)
                if isawaitable(result):
                    result = await result
                return result
            raise ErrResponse(
                401,
                "NotAuthenticated",
                "User is not authenticated.",
                help_url_path=documents(
                    "/user-guide/configuring-http-api/#security-considerations"
                ),
            )

        return fetch_decorated

    return decorator


def event_verbosity_params(
    request: Request, default_verbosity: releaseVerbosity
) -> releaseVerbosity:
    """Create `releaseVerbosity` object using request params if present."""
    event_verbosity_str = request.args.get(
        "include_events", default_verbosity.name
    ).upper()
    try:
        return releaseVerbosity[event_verbosity_str]
    except KeyError:
        enum_values = ", ".join([e.name for e in releaseVerbosity])
        raise ErrResponse(
            400,
            "BadRequest",
            "Invalid parameter value for 'include_events'. "
            "Should be one of {}".format(enum_values),
            {"parameter": "include_events", "in": "query"},
        )


async def fetch_tracker(
    processor: "MsgProcessor", conversation_id: Text
) -> DialogueStateTracer:
    """Get tracker object from `MsgProcessor`."""
    tracker = await processor.fetch_tracker_with_session_start(conversation_id)
    _validate_confirm_tracker(tracker, conversation_id)

    # `_validate_confirm_tracker` ensures we can't return `None` so `Optional` is not needed
    return tracker  # pytype: disable=bad-return-type


def _validate_confirm_tracker(
    tracker: Optional[DialogueStateTracer], conversation_id: Text
) -> None:
    if not tracker:
        raise ErrResponse(
            409,
            "Conflict",
            f"Could not retrieve tracker with ID '{conversation_id}'. Most likely "
            f"because there is no domain set on the agent.",
        )


def validate_confirm_request_body(request: Request, error_message: Text):
    """Check if `request` has a body."""
    if not request.body:
        raise ErrResponse(400, "BadRequest", error_message)


async def authentication(request: Request):
    """Callback for authentication failed."""
    raise exceptions.AuthenticationFailed(
        "Direct JWT authentication not supported. You should already have "
        "a valid JWT from an authentication provider, Convo will just make "
        "sure that the token is valid, but not issue new tokens."
    )


def create_ssl_context(
    ssl_certificate: Optional[Text],
    ssl_keyfile: Optional[Text],
    ssl_ca_file: Optional[Text] = None,
    ssl_password: Optional[Text] = None,
) -> Optional["SSLContext"]:
    """Create an SSL context if a proper certificate is passed.

    Args:
        ssl_certificate: path to the SSL client certificate
        ssl_keyfile: path to the SSL key file
        ssl_ca_file: path to the SSL CA file for verification (optional)
        ssl_password: SSL private key password (optional)

    Returns:
        SSL context if a valid certificate chain can be loaded, `None` otherwise.

    """

    if ssl_certificate:
        import ssl

        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cafile=ssl_ca_file
        )
        ssl_context.load_cert_chain(
            ssl_certificate, keyfile=ssl_keyfile, password=ssl_password
        )
        return ssl_context
    else:
        return None


def _create_new_emulator(mode: Optional[Text]) -> NotEmulator:
    """Create emulator for specified mode.
    If no emulator is specified, we will use the Convo NLU format."""

    if mode is None:
        return NotEmulator()
    elif mode.lower() == "wit":
        from convo.nlu.emulators.wit import EmulatorWit

        return EmulatorWit()
    elif mode.lower() == "luis":
        from convo.nlu.emulators.luis import EmulatorLUIS

        return EmulatorLUIS()
    elif mode.lower() == "dialogflow":
        from convo.nlu.emulators.dialogflow import EmulatorDialogFlow

        return EmulatorDialogFlow()
    else:
        raise ErrResponse(
            400,
            "BadRequest",
            "Invalid parameter value for 'emulation_mode'. "
            "Should be one of 'WIT', 'LUIS', 'DIALOGFLOW'.",
            {"parameter": "emulation_mode", "in": "query"},
        )


async def _agent_loaded(
    model_path: Optional[Text] = None,
    model_server: Optional[EndpointConfiguration] = None,
    remote_storage: Optional[Text] = None,
    endpoints: Optional[AvailableEndpoints] = None,
    lock_store: Optional[LockStore] = None,
) -> CoreAgent:
    try:
        tracer_store = None
        creator = None
        action_at_last = None

        if endpoints:
            broker = CoreEventBroker.generate(endpoints.event_broker)
            tracer_store = TrackerStorage.generate(
                endpoints.tracker_store, event_broker=broker
            )
            creator = endpoints.nlg
            action_at_last = endpoints.action
            if not lock_store:
                lock_store = LockStore.generate(endpoints.lock_store)

        loaded_agent = await convo.core.agent.agent_load(
            model_path,
            model_server,
            remote_storage,
            generator=creator,
            tracker_store=tracer_store,
            lock_store=lock_store,
            action_endpoint=action_at_last,
        )
    except Exception as e:
        logger.debug(traceback.format_exc())
        raise ErrResponse(
            500, "LoadingError", f"An unexpected error occurred. Error: {e}"
        )

    if not loaded_agent:
        raise ErrResponse(
            400,
            "BadRequest",
            f"CoreAgent with name '{model_path}' could not be loaded.",
            {"parameter": "model", "in": "query"},
        )

    return loaded_agent


def configurations_cors(
    app: Sanic, cors_origins: Union[Text, List[Text], None] = ""
) -> None:
    """Configure CORS origins for the given app."""

    # Workaround so that socketio works with requests from others origins.
    # https://github.com/miguelgrinberg/python-socketio/issues/205#issuecomment-493769183
    app.config.CORS_AUTOMATIC_OPTIONS = True
    app.config.CORS_SUPPORTS_CREDENTIALS = True
    app.config.CORS_EXPOSE_HEADERS = "filename"

    CORS(
        app, resources={r"/*": {"origins": cors_origins or ""}}, automatic_options=True
    )


def add_root_route_flow(app: Sanic):
    """Add '/' route to return hello."""

    @app.get("/")
    async def hello(request: Request):
        """Check if the server is running and responds with the version."""
        return response.text("Hello from Convo: " + convo.__version__)


def create_application(
    agent: Optional["CoreAgent"] = None,
    cors_origins: Union[Text, List[Text], None] = "*",
    auth_token: Optional[Text] = None,
    response_timeout: int = BY_DEFAULT_RESPONSE_RESULT_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Text = "HS256",
    endpoints: Optional[AvailableEndpoints] = None,
):
    """Class representing a Convo HTTP server."""

    application = Sanic(__name__)
    application.config.RESPONSE_TIMEOUT = response_timeout
    configurations_cors(application, cors_origins)

    # Setup the Sanic-JWT extension
    if jwt_secret and jwt_method:
        # since we only want to check signatures, we don't actually care
        # about the JWT method and set the passed secret as either symmetric
        # or asymmetric key. jwt lib will choose the right one based on method
        application.config["USE_JWT"] = True
        Initialize(
            application,
            secret=jwt_secret,
            authentication=authentication,
            algorithm=jwt_method,
            user_id="username",
        )

    application.agent = agent
    # Initialize shared object of type unsigned int for tracking
    # the number of active training processes
    application.active_training_processes = multiprocessing.Value("I", 0)

    @application.exception(ErrResponse)
    async def handle_error_response(request: Request, exception: ErrResponse):
        return response.json(exception.error_info, status=exception.status)

    add_root_route_flow(application)

    @application.get("/version")
    async def version(request: Request):
        """Respond with the version number of the installed Convo."""

        return response.json(
            {
                "version": convo.__version__,
                "minimum_compatible_version": MIN_COMPATIBLE_VER,
            }
        )

    @application.get("/status")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def get_status(request: Request):
        """Respond with the model name and the fingerprint of that model."""

        return response.json(
            {
                "model_file": application.agent.path_to_model_archive
                              or application.agent.model_directory,
                "fingerprint": model.finger_print_from_path_flow(application.agent.model_directory),
                "num_active_training_jobs": application.active_training_processes.value,
            }
        )

    @application.get("/conversations/<conversation_id:path>/tracker")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def retrieve_tracker_back(request: Request, conversation_id: Text):
        """Get a dump of a conversation's tracker including its events."""

        server_verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)
        time_untils = convo.utils.endpoints.float_argument(request, "until")

        tracer = await fetch_tracker(application.agent.create_processor(), conversation_id)

        try:
            if time_untils is not None:
                tracer = tracer.travel_back_in_time(time_untils)

            state = tracer.current_active_state(server_verbosity)
            return response.json(state)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

    @application.post("/conversations/<conversation_id:path>/tracker/events")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def add_events(request: Request, conversation_id: Text):
        """Append a list of events to the state of a conversation"""
        validate_confirm_request_body(
            request,
            "You must provide events in the request body in order to append them"
            "to the state of a conversation.",
        )

        server_verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)

        try:
            async with application.agent.lock_store.secure_lock(conversation_id):
                get_procedure = application.agent.create_processor()
                tracker = get_procedure.fetch_tracker(conversation_id)
                output_channel = _fetch_output_channel(request, tracker)
                _validate_confirm_tracker(tracker, conversation_id)

                event = _fetch_events_from_request_body(request)

                for event in event:
                    tracker.update(event, application.agent.domain)
                if convo.utils.endpoints.boolean_argument(
                    request, EXECUTE_SIDE_EFFECTS_QUERY_KEY, False
                ):
                    await get_procedure.run_side_effects(
                        event, tracker, output_channel
                    )
                application.agent.tracker_store.save(tracker)

            return response.json(tracker.current_active_state(server_verbosity))
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

    def _fetch_events_from_request_body(request: Request) -> List[Event]:
        events = request.json

        if not isinstance(events, list):
            events = [events]

        events = [Event.from_params(event) for event in events]
        events = [event for event in events if event]

        if not events:
            convo.shared.utils.io.raising_warning(
                f"Append event called, but could not extract a valid event. "
                f"Request JSON: {request.json}"
            )
            raise ErrResponse(
                400,
                "BadRequest",
                "Couldn't extract a proper event from the request body.",
                {"parameter": "", "in": "body"},
            )

        return events

    @application.put("/conversations/<conversation_id:path>/tracker/events")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def replace_events(request: Request, conversation_id: Text):
        """Use a list of events to set a conversations tracker to a state."""
        validate_confirm_request_body(
            request,
            "You must provide events in the request body to set the sate of the "
            "conversation tracker.",
        )

        verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)

        try:
            async with application.agent.lock_store.secure_lock(conversation_id):
                tracker = DialogueStateTracer.from_dict(
                    conversation_id, request.json, application.agent.domain.slots
                )

                # will override an existing tracker with the same id!
                application.agent.tracker_store.save(tracker)

            return response.json(tracker.current_active_state(verbosity))
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

    @application.get("/conversations/<conversation_id:path>/story")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def retrieve_story_back(request: Request, conversation_id: Text):
        """Get an end-to-end story corresponding to this conversation."""

        # retrieve tracker and set to requested state
        tracker = await fetch_tracker(application.agent.create_processor(), conversation_id)

        time_untils = convo.utils.endpoints.float_argument(request, "until")

        try:
            if time_untils is not None:
                tracker = tracker.travel_back_in_time(time_untils)

            # dump and return tracker
            state = YAMLStoryAuthor().data_dumps(tracker.as_story().story_steps)
            return response.text(state)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

    @application.post("/conversations/<conversation_id:path>/execute")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def perform_action(request: Request, conversation_id: Text):
        request_parameter = request.json

        perform_execution = request_parameter.get("name", None)

        if not perform_execution:
            raise ErrResponse(
                400,
                "BadRequest",
                "Name of the action not provided in request body.",
                {"parameter": "name", "in": "body"},
            )

        policies = request_parameter.get("policy", None)
        server_confidence = request_parameter.get("confidence", None)
        verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)

        try:
            async with application.agent.lock_store.secure_lock(conversation_id):
                tracker = await fetch_tracker(
                    application.agent.create_processor(), conversation_id
                )
                outcome_channel = _fetch_output_channel(request, tracker)
                await application.agent.perform_action(
                    conversation_id,
                    perform_execution,
                    outcome_channel,
                    policies,
                    server_confidence,
                )

        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

        tracker = await fetch_tracker(application.agent.create_processor(), conversation_id)
        state = tracker.current_active_state(verbosity)

        response_result_body = {"tracker": state}

        if isinstance(outcome_channel, CollectOutputChannel):
            response_result_body["messages"] = outcome_channel.messages

        return response.json(response_result_body)

    @application.post("/conversations/<conversation_id:path>/trigger_intent")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def activate_intent(request: Request, conversation_id: Text) -> HTTPResponse:
        request_params = request.json

        intented_trigger = request_params.get("name")
        entity = request_params.get("entities", [])

        if not intented_trigger:
            raise ErrResponse(
                400,
                "BadRequest",
                "Name of the intent not provided in request body.",
                {"parameter": "name", "in": "body"},
            )

        verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)

        try:
            async with application.agent.lock_store.secure_lock(conversation_id):
                tracker = await fetch_tracker(
                    application.agent.create_processor(), conversation_id
                )
                outcome_channel = _fetch_output_channel(request, tracker)
                if intented_trigger not in application.agent.domain.fetch_intents:
                    raise ErrResponse(
                        404,
                        "NotFound",
                        f"The intent {activate_intent} does not exist in the domain.",
                    )
                await application.agent.trigger_intent(
                    intented_names=intented_trigger,
                    entities=entity,
                    output_channel=outcome_channel,
                    tracker=tracker,
                )
        except ErrResponse:
            raise
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

        state_occurance = tracker.current_active_state(verbosity)

        response_body = {"tracker": state_occurance}

        if isinstance(outcome_channel, CollectOutputChannel):
            response_body["messages"] = outcome_channel.messages

        return response.json(response_body)

    @application.post("/conversations/<conversation_id:path>/predict")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def predict(request: Request, conversation_id: Text) -> HTTPResponse:
        try:
            # Fetches the appropriate bot response in a json format
            results = await application.agent.forecast_next(conversation_id)
            results["scores"] = sorted(
                results["scores"], key=lambda k: (-k["score"], k["action"])
            )
            return response.json(results)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

    @application.post("/conversations/<conversation_id:path>/messages")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def add_msg(request: Request, conversation_id: Text):
        validate_confirm_request_body(
            request,
            "No message defined in request body. Add a message to the request body in "
            "order to add it to the tracker.",
        )

        request_parameter = request.json

        message = request_parameter.get("text")
        transmitter = request_parameter.get("sender")
        parse_data_set = request_parameter.get("parse_data")

        verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)

        # TODO: implement for agent / bot
        if transmitter != "user":
            raise ErrResponse(
                400,
                "BadRequest",
                "Currently, only user messages can be passed to this endpoint. "
                "Messages of sender '{}' cannot be handled.".format(transmitter),
                {"parameter": "sender", "in": "body"},
            )

        user_msg = UserMsg(message, None, conversation_id, parse_data_set)

        try:
            async with application.agent.lock_store.secure_lock(conversation_id):
                tracker = await application.agent.log_msg(user_msg)
            return response.json(tracker.current_active_state(verbosity))
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ConversationError", f"An unexpected error occurred. Error: {e}"
            )

    @application.post("/model/train")
    @requires_authorization(application, auth_token)
    async def server_train(request: Request) -> HTTPResponse:
        """Train a Convo Model."""

        validate_confirm_request_body(
            request,
            "You must provide training data in the request body in order to "
            "train your model.",
        )

        if request.headers.get("Content-type") == YAML_CONTENT_TYPE:
            supervising_payload = _trained_payload_from_yaml(request)
        else:
            supervising_payload = _trained_payload_from_json(request)

        try:
            with application.active_training_processes.get_lock():
                application.active_training_processes.value += 1

            server_loop = asyncio.get_event_loop()

            from convo import train as train_model

            # Declare `model_path` upfront to avoid pytype `name-error`
            model_path_flow: Optional[Text] = None
            # pass `None` to run in default executor
            model_path_flow = await server_loop.run_in_executor(
                None, functools.partial(train_model, **supervising_payload)
            )

            if model_path_flow:
                filename = os.path.basename(model_path_flow)

                return await response.file(
                    model_path_flow, filename=filename, headers={"filename": filename}
                )
            else:
                raise ErrResponse(
                    500,
                    "TrainingError",
                    "Ran training, but it finished without a trained model.",
                )
        except ErrResponse as e:
            raise e
        except InvalidDomain as e:
            raise ErrResponse(
                400,
                "InvalidDomainError",
                f"Provided domain file is invalid. Error: {e}",
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            raise ErrResponse(
                500,
                "TrainingError",
                f"An unexpected error occurred during training. Error: {e}",
            )
        finally:
            with application.active_training_processes.get_lock():
                application.active_training_processes.value -= 1

    @application.post("/model/test/stories")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application, require_core_is_ready=True)
    async def calculate_stories(request: Request) -> HTTPResponse:
        """Evaluate stories against the currently loaded model."""
        validate_confirm_request_body(
            request,
            "You must provide some stories in the request body in order to "
            "evaluate your model.",
        )

        tested_data_set = _test_data_set_file_from_payload(request)

        avail_e2e = convo.utils.endpoints.boolean_argument(request, "e2e", default=False)

        try:
            evaluation = await test(
                tested_data_set, application.agent, e2e=avail_e2e, disable_plotting=True
            )
            return response.json(evaluation)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise ErrResponse(
                500,
                "TestingError",
                f"An unexpected error occurred during evaluation. Error: {e}",
            )

    @application.post("/model/test/convo_intents")
    @requires_authorization(application, auth_token)
    async def calculate_intents(request: Request) -> HTTPResponse:
        """Evaluate intents against a Convo model."""
        validate_confirm_request_body(
            request,
            "You must provide some nlu data in the request body in order to "
            "evaluate your model.",
        )

        test_data = _test_data_set_file_from_payload(request)

        evaluation_agent = application.agent

        model_path = request.args.get("model", None)
        if model_path:
            model_serv = application.agent.model_server
            if model_serv is not None:
                model_serv.url = model_path
            evaluation_agent = await _agent_loaded(
                model_path, model_serv, application.agent.remote_storage
            )

        data_path = os.path.abspath(test_data)

        if not evaluation_agent.model_directory or not os.path.exists(
            evaluation_agent.model_directory
        ):
            raise ErrResponse(409, "Conflict", "Loaded model file not found.")

        model_dir = evaluation_agent.model_directory
        _, nlu_type_model = model.fetch_model_subdirectories(model_dir)

        try:
            evaluation = run_eval(data_path, nlu_type_model, disable_plotting=True)
            return response.json(evaluation)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise ErrResponse(
                500,
                "TestingError",
                f"An unexpected error occurred during evaluation. Error: {e}",
            )

    @application.post("/model/predict")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application, require_core_is_ready=True)
    async def tracker_forecast(request: Request) -> HTTPResponse:
        """ Given a list of events, predicts the next action"""
        validate_confirm_request_body(
            request,
            "No events defined in request_body. Add events to request body in order to "
            "predict the next action.",
        )

        verbosity = event_verbosity_params(request, releaseVerbosity.AFTER_RESTART)
        request_params = request.json
        try:
            tracker = DialogueStateTracer.from_dict(
                CONVO_DEFAULT_SENDER_ID , request_params, application.agent.domain.slots
            )
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                400,
                "BadRequest",
                f"Supplied events are not valid. {e}",
                {"parameter": "", "in": "body"},
            )

        try:
            policy_ensemble = application.agent.policy_ensemble
            probabilities, policy = policy_ensemble.probability_using_finest_policy(
                tracker, application.agent.domain, application.agent.interpreter
            )

            scores = [
                {"action": a, "score": p}
                for a, p in zip(application.agent.domain.action_names, probabilities)
            ]

            return response.json(
                {
                    "scores": scores,
                    "policy": policy,
                    "tracker": tracker.current_active_state(verbosity),
                }
            )
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "PredictionError", f"An unexpected error occurred. Error: {e}"
            )

    @application.post("/model/parse")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def traverse(request: Request) -> HTTPResponse:
        validate_confirm_request_body(
            request,
            "No text message defined in request_body. Add text message to request body "
            "in order to obtain the intent and extracted entities.",
        )
        emulation_mode_type = request.args.get("emulation_mode")
        fetch_emulator = _create_new_emulator(emulation_mode_type)

        try:
            data = fetch_emulator.normalise_request_dict(request.json)
            try:
                parsed_data = await application.agent.parse_message_using_nlu_interpreter(
                    data.get("text")
                )
            except Exception as e:
                logger.debug(traceback.format_exc())
                raise ErrResponse(
                    400, "ParsingError", f"An unexpected error occurred. Error: {e}"
                )
            response_data = fetch_emulator.normalise_response_dict(parsed_data)

            return response.json(response_data)

        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrResponse(
                500, "ParsingError", f"An unexpected error occurred. Error: {e}"
            )

    @application.put("/model")
    @requires_authorization(application, auth_token)
    async def load_model_data(request: Request) -> HTTPResponse:
        validate_confirm_request_body(request, "No path to model file defined in request_body.")

        model_path = request.json.get("model_file", None)
        model_server = request.json.get("model_server", None)
        remote_store = request.json.get("remote_storage", None)

        if model_server:
            try:
                model_server = EndpointConfiguration.from_dict(model_server)
            except TypeError as e:
                logger.debug(traceback.format_exc())
                raise ErrResponse(
                    400,
                    "BadRequest",
                    f"Supplied 'model_server' is not valid. Error: {e}",
                    {"parameter": "model_server", "in": "body"},
                )

        application.agent = await _agent_loaded(
            model_path, model_server, remote_store, endpoints, application.agent.lock_store
        )

        logger.debug(f"Successfully loaded model '{model_path}'.")
        return response.json(None, status=204)

    @application.delete("/model")
    @requires_authorization(application, auth_token)
    async def stash_model(request: Request) -> HTTPResponse:
        model_file_exist = application.agent.model_directory

        application.agent = CoreAgent(lock_store=application.agent.lock_store)

        logger.debug(f"Successfully unloaded model '{model_file_exist}'.")
        return response.json(None, status=204)

    @application.get("/domain")
    @requires_authorization(application, auth_token)
    @confirm_loaded_agent(application)
    async def domain(request: Request) -> HTTPResponse:
        """Get current domain in yaml or json format."""

        obtained = request.headers.get("Accept", default=JSON_CONTENT_TYPE)
        if obtained.endswith("json"):
            domain_name = application.agent.domain.as_dictionary()
            return response.json(domain_name)
        elif obtained.endswith("yml") or obtained.endswith("yaml"):
            domain_path_yaml = application.agent.domain.yaml_as()
            return response.text(
                domain_path_yaml, status=200, content_type=YAML_CONTENT_TYPE
            )
        else:
            raise ErrResponse(
                406,
                "NotAcceptable",
                f"Invalid Accept header. Domain can be "
                f"provided as "
                f'json ("Accept: {JSON_CONTENT_TYPE}") or'
                f'yml ("Accept: {YAML_CONTENT_TYPE}"). '
                f"Make sure you've set the appropriate Accept "
                f"header.",
            )

    return application


def _fetch_output_channel(
    request: Request, tracker: Optional[DialogueStateTracer]
) -> OutputSocket:
    """Returns the `OutputSocket` which should be used for the bot's responses.

    Args:
        request: HTTP request whose query parameters can specify which `OutputSocket`
                 should be used.
        tracker: Tracker for the conversation. Used to get the latest input channel.

    Returns:
        `OutputSocket` which should be used to return the bot's responses to.
    """
    req_output_channels = request.args.get(OUTPUT_CHANNEL_QUERY_KEY)

    if (
        req_output_channels == USE_LATEST_INPUT_CHANNEL_AS_OUTPUT_CHANNEL
        and tracker
    ):
        req_output_channels = tracker.get_input_channel_latest()

    # Interactive training does not set `input_channels`, hence we have to be cautious
    register_input_channel = getattr(request.app, "input_channels", None) or []
    matching_channels = [
        channel
        for channel in register_input_channel
        if channel.name() == req_output_channels
    ]

    # Check if matching channels can provide a valid output channel,
    # otherwise use `CollectOutputChannel`
    return reduce(
        lambda output_channel_created_so_far, input_channel: (
                input_channel.fetch_output_channel() or output_channel_created_so_far
        ),
        matching_channels,
        CollectOutputChannel(),
    )


def _test_data_set_file_from_payload(request: Request) -> Text:
    if request.headers.get("Content-type") == YAML_CONTENT_TYPE:
        return str(_trained_payload_from_yaml(request)["training_files"])
    else:
        return convo.utils.io.create_temp_file(
            request.body, mode="w+b", suffix=".md"
        )


def _trained_payload_from_json(request: Request) -> Dict[Text, Union[Text, bool]]:
    logger.debug(
        "Extracting JSON payload with Markdown training data from request body."
    )

    request_outcome_payload = request.json
    _validation_json_trained_payload(request_outcome_payload)

    # create a temporary dir to store config, domain and
    # training data
    temporary_directory = tempfile.mkdtemp()

    configuration_path = os.path.join(temporary_directory, "config.yml")

    convo.shared.utils.io.writing_text_file(request_outcome_payload["config"], configuration_path)

    if "nlu" in request_outcome_payload:
        nlu_path_flow = os.path.join(temporary_directory, "nlu.md")
        convo.shared.utils.io.writing_text_file(request_outcome_payload["nlu"], nlu_path_flow)

    if "stories" in request_outcome_payload:
        stories_path_flow = os.path.join(temporary_directory, "stories.md")
        convo.shared.utils.io.writing_text_file(request_outcome_payload["stories"], stories_path_flow)

    if "responses" in request_outcome_payload:
        response_outcome_path = os.path.join(temporary_directory, "responses.md")
        convo.shared.utils.io.writing_text_file(
            request_outcome_payload["responses"], response_outcome_path
        )

    domain_pat_flow = CONVO_DEFAULT_DOMAIN_PATH
    if "domain" in request_outcome_payload:
        domain_pat_flow = os.path.join(temporary_directory, "domain.yml")
        convo.shared.utils.io.writing_text_file(request_outcome_payload["domain"], domain_pat_flow)

    model_output_directory = _model_output_folder(
        request_outcome_payload.get(
            "save_to_default_model_directory",
            request.args.get("save_to_default_model_directory", True),
        )
    )

    return dict(
        domain=domain_pat_flow,
        config=configuration_path,
        trained_file=temporary_directory,
        result=model_output_directory,
        by_force_training=request_outcome_payload.get(
            "force", request.args.get("force_training", False)
        ),
    )


def _validation_json_trained_payload(rjs: Dict):
    if "config" not in rjs:
        raise ErrResponse(
            400,
            "BadRequest",
            "The training request is missing the required key `config`.",
            {"parameter": "config", "in": "body"},
        )

    if "nlu" not in rjs and "stories" not in rjs:
        raise ErrResponse(
            400,
            "BadRequest",
            "To train a Convo model you need to specify at least one type of "
            "training data. Add `nlu` and/or `stories` to the request.",
            {"parameters": ["nlu", "stories"], "in": "body"},
        )

    if "stories" in rjs and "domain" not in rjs:
        raise ErrResponse(
            400,
            "BadRequest",
            "To train a Convo model with story training data, you also need to "
            "specify the `domain`.",
            {"parameter": "domain", "in": "body"},
        )

    if "force" in rjs or "save_to_default_model_directory" in rjs:
        convo.shared.utils.io.rasing_deprecate_warning(
            "Specifying 'force' and 'save_to_default_model_directory' as part of the "
            "JSON payload is deprecated. Please use the header arguments "
            "'force_training' and 'save_to_default_model_directory'.",
            documents=documents("/api/http-api"),
        )


def _trained_payload_from_yaml(request: Request,) -> Dict[Text, Union[Text, bool]]:
    logger.debug("Extracting YAML training data from request body.")

    decode = request.body.decode(convo.shared.utils.io.ENCODING_DEFAULT)
    _validation_yaml_trained_payload(decode)

    temporary_directory = tempfile.mkdtemp()
    training_data_set = Path(temporary_directory) / "data.yml"
    convo.shared.utils.io.writing_text_file(decode, training_data_set)

    model_output_folder = _model_output_folder(
        request.args.get("save_to_default_model_directory", True)
    )

    return dict(
        domain=str(training_data_set),
        config=str(training_data_set),
        training_files=temporary_directory,
        output=model_output_folder,
        force_training=request.args.get("force_training", False),
    )


def _model_output_folder(save_to_default_model_directory: bool) -> Text:
    if save_to_default_model_directory:
        return DEFAULT_MODEL_PATH 

    return tempfile.gettempdir()


def _validation_yaml_trained_payload(yaml_text: Text) -> None:
    try:
        ConvoYAMLReviewer().validating(yaml_text)
    except Exception as e:
        raise ErrResponse(
            400,
            "BadRequest",
            f"The request body does not contain valid YAML. Error: {e}",
            help_url_path=TRAINING_DATA_DOCUMENTS_URL,
        )
