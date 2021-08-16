import click
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import re
import webbrowser

from spell import deployment_constants
from spell.api.base_client import SpellDecoder
from spell.api.exceptions import UnauthorizedRequest
from spell.configs.config_handler import ConfigException
from spell.cli.commands.keys import generate, get_remote_key
from spell.cli.commands.logout import logout
from spell.cli.log import logger
from spell.cli.exceptions import ExitException, api_client_exception_handler
from spell.cli.utils import try_add_known_host
from spell.cli.utils import cli_ssh_key_path


@click.command(name="login")
@click.pass_context
@click.option(
    "--identity",
    "identity",
    help="Spell username or email address",
)
@click.password_option(
    help="Spell password",
    prompt=False,
)
def login(ctx, identity, password):
    """
    Login to your Spell account.

    By default, authentication is handled by the Spell web console in your web browser.
    Alternatively, identity and password can be specified using command line options.

    If you don't have an account with Spell, please create one at https://spell.ml.
    """
    config_handler = ctx.obj["config_handler"]
    config = config_handler.config

    # Log out of existing session, if any.
    if config:
        try:
            ctx.invoke(logout, quiet=True)
        except Exception as e:
            logger.warning("Log out failed for previous session: %s", e)

    if config_handler.config is None:
        config_handler.load_default_config(type="global")

    config = config_handler.config
    client = ctx.obj["client"]

    # TODO: IPC - consider what this means for the proposed removal of the endpoint
    # Login with user/pass in Jupyter context. Login via web console probably won't work.
    if "JPY_PARENT_PID" in os.environ and not identity:
        identity = click.prompt("Username")

    if identity:
        if not password:
            password = click.prompt("Password", hide_input=True)
        user, token, spell_admin_auth_token = login_via_password(client, identity, password)
    else:
        user, token, spell_admin_auth_token = login_via_web(ctx.obj["web_url"])

    logger.info("Sucessfully logged in.")
    client.token = token
    config.token = token
    config.spell_admin_auth_token = spell_admin_auth_token
    config.user_name = user.user_name
    config.email = user.email

    # If an owner is not configured, default to the organization (if any)
    if not config.owner:
        if not user.memberships:
            if deployment_constants.on_prem:
                raise ExitException(
                    "You are not part of any organization, "
                    "please contact your system administrator to continue using Spell"
                )
            else:
                config.owner = config.user_name
        else:
            # in onprem, always fetch the first membership.
            # otherwise if there is only one org, use that, otherwise fall back on community (see main.py)
            if deployment_constants.on_prem or len(user.memberships) == 1:
                config.owner = user.memberships[0].organization.name
            else:
                config.owner = config.user_name
    try:
        config_handler.write()
    except ConfigException as e:
        raise ExitException(e.message)

    # Generate CLI key for user if one does not exist, or if the existing one
    # is not registered with the user's Spell account
    local_key = cli_ssh_key_path(config_handler)
    matching_remote_key = os.path.isfile(local_key) and get_remote_key(ctx, local_key)
    if not matching_remote_key:
        ctx.invoke(generate, force=True)

    # Attempt to add git.spell.ml to known_hosts, ignore failures
    try_add_known_host()

    click.echo(u"Hello, {}!".format(user_addressing_noun(user)))


def login_via_password(client, identity, password):
    with api_client_exception_handler():
        try:
            if is_email(identity):
                return client.login_with_email(identity, password)
            else:
                return client.login_with_username(identity, password)
        except UnauthorizedRequest as exception:
            raise ExitException(str(exception))


def login_via_web(web_root_url):
    user = None
    token = None
    spell_admin_auth_token = None

    class NewSessionRequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            nonlocal user, token, spell_admin_auth_token

            length = int(self.headers["Content-Length"])
            payload = json.loads(self.rfile.read(length), cls=SpellDecoder)
            user = payload["user"]
            token = payload["token"]
            spell_admin_auth_token = payload["spell_admin_auth_token"]

            self.send_response(204)
            self.end_headers()

        def log_message(self, *args):
            pass  # Do not log HTTP traffic.

    httpd = HTTPServer(("localhost", 0), NewSessionRequestHandler)
    port = httpd.server_address[1]
    web_auth_url = "{}/local/login?port={}".format(web_root_url, port)
    webbrowser.open(web_auth_url)
    click.echo(u"Waiting for authentication from the Spell web console…")
    click.echo(u"Login URL: {}".format(web_auth_url))
    httpd.handle_request()

    return user, token, spell_admin_auth_token


def is_email(input):
    return re.match(".+@.+[.].+", input) is not None


def user_addressing_noun(user):
    nouns = [user.full_name, user.user_name, user.email]
    return next((s for s in nouns if s), "")
