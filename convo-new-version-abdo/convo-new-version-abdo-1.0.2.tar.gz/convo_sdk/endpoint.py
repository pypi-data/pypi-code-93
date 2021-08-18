import argparse
import logging
import types
from typing import List, Text, Union, Optional, Any
from ssl import SSLContext

from sanic import Sanic, response
from sanic.response import HTTPResponse
from sanic.request import Request
from sanic_cors import CORS

from convo_sdk import utils
from convo_sdk.cli.arguments import add_end_point_args
from convo_sdk.constants import SERVER_PORT_DEFAULT
from convo_sdk.executor import ActExecutor
from convo_sdk.interfaces import ActExecutionRejection, ActionNotFoundException

log = logging.getLogger(__name__)


def configurations_cors(
    app: Sanic, cors_origins: Union[Text, List[Text], None] = ""
) -> None:
    """Configure CORS origins for the given app."""

    CORS(
        app, resources={r"/*": {"origins": cors_origins or ""}}, automatic_options=True
    )


def ssl_context_creation(
    ssl_certificate: Optional[Text],
    ssl_keyfile: Optional[Text],
    ssl_password: Optional[Text] = None,
) -> Optional[SSLContext]:
    """Create a SSL context if a certificate is passed."""

    if ssl_certificate:
        import ssl

        ssl_context_data = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        ssl_context_data.load_cert_chain(
            ssl_certificate, keyfile=ssl_keyfile, password=ssl_password
        )
        return ssl_context_data
    else:
        return None


def creating_args_parser():
    """Parse all the command line arguments for the run script."""

    analyser = argparse.ArgumentParser(description="starts the action endpoint")
    add_end_point_args(analyser)
    utils.add_logging_opt_args(analyser)
    return analyser


def creating_application(
    action_package_name: Union[Text, types.ModuleType],
    cors_origins: Union[Text, List[Text], None] = "*",
    auto_reload: bool = False,
) -> Sanic:
    """Create a Sanic application and return it.

    Args:
        action_package_name: Name of the package or module to load actions
            from.
        cors_origins: CORS origins to allow.
        auto_reload: When `True`, auto-reloading of actions is enabled.

    Returns:
        A new Sanic application ready to be run.
    """
    application = Sanic(__name__, configure_logging=False)

    configurations_cors(application, cors_origins)

    run = ActExecutor()
    run.register_package(action_package_name)

    @application.get("/health")
    async def health(_) -> HTTPResponse:
        """Ping endpoint to check if the server is running and well."""
        body_val = {"status": "ok"}
        return response.json(body_val, status=200)

    @application.post("/webhook")
    async def webhook(request: Request) -> HTTPResponse:
        """Webhook to retrieve action calls."""
        act_call = request.json
        if act_call is None:
            body_val = {"error": "Invalid body_val request"}
            return response.json(body_val, status=400)

        utils.version_compatibility_check(act_call.get("version"))

        if auto_reload:
            run.reload()

        try:
            res = await run.run(act_call)
        except ActExecutionRejection as e:
            log.debug(e)
            body_val = {"error": e.message, "action_name": e.action_name}
            return response.json(body_val, status=400)
        except ActionNotFoundException as e:
            log.error(e)
            body_val = {"error": e.message, "action_name": e.action_name}
            return response.json(body_val, status=404)

        return response.json(res, status=200)

    @application.get("/actions")
    async def act(_) -> HTTPResponse:
        print('@application.get("/actions")')
        """List all registered actions."""
        if auto_reload:
            run.reload()

        body_val = [{"name": k} for k in run.act.keys()]
        return response.json(body_val, status=200)

    return application


def execute(
    action_package_name: Union[Text, types.ModuleType],
    port: Union[Text, int] = SERVER_PORT_DEFAULT,
    cors_origins: Union[Text, List[Text], None] = "*",
    ssl_certificate: Optional[Text] = None,
    ssl_keyfile: Optional[Text] = None,
    ssl_password: Optional[Text] = None,
    auto_reload: bool = False,
) -> None:
    log.info("Starting action endpoint server...")
    application = creating_application(
        action_package_name, cors_origins=cors_origins, auto_reload=auto_reload
    )
    ssl_context_data = ssl_context_creation(ssl_certificate, ssl_keyfile, ssl_password)
    rules = "https" if ssl_context_data else "http"

    log.info(f"Action endpoint is up and running on {rules}://localhost:{port}")
    application.run("0.0.0.0", port, ssl=ssl_context_data, workers=utils.no_of_sanic_workers())


if __name__ == "__main__":
    import convo_sdk.__main__

    convo_sdk.__main__.main()
