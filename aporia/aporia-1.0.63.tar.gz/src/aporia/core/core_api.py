import atexit
from contextlib import suppress
import logging
from typing import Dict, Optional

from aporia.model import Model
from .api.create_model_version import (
    run_create_model_version_query,
    validate_fields_input,
)
from .config import Config
from .context import get_context, init_context, reset_context
from .errors import AporiaError, handle_error
from .event_loop import EventLoop
from .graphql_client import GraphQLClient
from .logging_utils import init_logger, LOGGER_NAME, set_log_level

logger = logging.getLogger(LOGGER_NAME)


def init(
    token: Optional[str] = None,
    host: Optional[str] = None,
    environment: Optional[str] = None,
    port: Optional[int] = None,
    verbose: Optional[bool] = None,
    throw_errors: Optional[bool] = None,
    debug: Optional[bool] = None,
):
    """Initializes the Aporia SDK.

    Args:
        token: Authentication token.
        host: Controller host.
        environment: Environment in which aporia is initialized (e.g production, staging).
        port: Controller port. Defaults to 443.
        verbose: True to enable verbose error messages. Defaults to False
        throw_errors: True to cause errors to be raised as exceptions. Defaults to False.
        debug: True to enable debug logs and stack traces in log messages. Defaults to False.

    Notes:
        * The token, host and environment parameters are required.
        * All of the parameters here can also be defined as environment variables:
            * token -> APORIA_TOKEN
            * host -> APORIA_HOST
            * environment -> APORIA_ENVIRONMENT
            * port -> APORIA_PORT
            * verbose -> APORIA_VERBOSE
            * throw_errors -> APORIA_THROW_ERRORS
            * debug -> APORIA_DEBUG
        * Values passed as parameters to aporia.init() override the values from
          the corresponding environment variables.
    """
    init_logger()

    logger.debug("Initializing Aporia SDK.")

    try:
        config = Config(
            token=token,
            host=host,
            environment=environment,
            port=port,
            verbose=verbose,
            throw_errors=throw_errors,
            debug=debug,
        )

        set_log_level(config.debug)

        event_loop = EventLoop()
        graphql_client = GraphQLClient(token=config.token, host=config.host, port=config.port)

        init_context(graphql_client=graphql_client, event_loop=event_loop, config=config)

        atexit.register(shutdown)
        logger.debug("Aporia SDK initialized.")
    except Exception as err:
        handle_error(
            message_format="Initializing Aporia SDK failed, error: {}",
            verbose=False if verbose is None else verbose,
            throw_errors=False if throw_errors is None else throw_errors,
            debug=False if debug is None else debug,
            original_exception=err,
        )


def shutdown():
    """Shuts down the Aporia SDK.

    Notes:
        * It is advised to call flush() before calling shutdown(), to ensure that
          all of the data that was sent reaches the controller.
    """
    logger.debug("Shutting down Aporia SDK.")
    with suppress(Exception):
        reset_context()


def create_model_version(
    model_id: str,
    model_version: str,
    model_type: str,
    features: Dict[str, str],
    predictions: Dict[str, str],
    raw_inputs: Optional[Dict[str, str]] = None,
    metrics: Optional[Dict[str, str]] = None,
) -> Optional[Model]:
    """Create a new model version, and defines a schema for it.

    Args:
        model_id (str): Model identifier, as received from the Aporia dashboard.
        model_version (str): Model version - this can be any string that represents the model
            version, such as "v1" or a git commit hash.
        model_type (str): Model type (also known as objective). The supported model types are:
            * "regression" - for regression models
            * "binary" - for binary classification models
            * "multiclass" - for multiclass classification models
        features (Dict[str, str]): Schema for model features (See notes)
        predictions (Dict[str, str]): Schema for prediction results (See notes)
        raw_inputs (Dict[str, str], optional): Schema for raw inputs (See notes). Defaults to None.
        metrics (Dict[str, str], optional): Schema for prediction metrics (See notes). Defaults to None.

    Notes:
        * A schema is a dict, in which the keys are the fields you wish to report, and the
          values are the types of those fields. For example:
            {
                "feature1": "numeric",
                "feature2": "datetime"
            }
        * The valid field types (and corresponding python types) are:
            | Field Type    | Python Types
            | ------------- | ------------
            | "numeric"     | float, int
            | "categorical" | int
            | "boolean"     | bool
            | "string"      | str
            | "datetime"    | datetime.datetime, or str representing a datetime in ISO-8601 format
            | "vector"      | list of floats
            | "text"        | str (to be used as free text)

    Returns:
        Model object for the new version.
    """
    context = get_context()

    try:
        if len(model_id) == 0 or len(model_version) == 0:
            raise AporiaError("model_id and model_version must be non-empty strings.")

        validate_fields_input(
            features=features,
            predictions=predictions,
            raw_inputs=raw_inputs,
            metrics=metrics,
        )

        context.event_loop.run_coroutine(
            run_create_model_version_query(
                graphql_client=context.graphql_client,
                model_id=model_id,
                model_version=model_version,
                model_type=model_type,
                features=features,
                predictions=predictions,
                raw_inputs=raw_inputs,
                metrics=metrics,
            )
        )

        return Model(model_id=model_id, model_version=model_version)
    except Exception as err:
        handle_error(
            message_format="Creating model version failed, error: {}",
            verbose=context.config.verbose,
            throw_errors=context.config.throw_errors,
            debug=context.config.debug,
            original_exception=err,
        )

        return None
