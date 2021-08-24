import click

from convisoappsec.version import __version__

from convisoappsec.flow import api

from .deploy import deploy
from .finding import finding
from .sast import sast
from .sca import sca
from .vulnerability import vulnerability
from .context import pass_flow_context
from convisoappsec.flowcli import help_option


def api_url_autocompletion(*args, **kargs):
    return [
        api.PRODUCTION_API_URL,
        api.STAGING_API_URL,
        api.DEVELOPMENT_API_URL,
    ]


@click.group()
@click.option(
    '-k',
    '--api-key',
    show_envvar=True,
    envvar="FLOW_API_KEY",
    help="The api key to access flow resources.",
)
@click.option(
    '-u',
    '--api-url',
    show_envvar=True,
    envvar="FLOW_API_URL",
    default=api.DEFAULT_API_URL,
    show_default=True,
    autocompletion=api_url_autocompletion,
    help='The api url to access flow resources.',
)
@click.option(
    '-i',
    '--api-insecure',
    show_envvar=True,
    envvar="FLOW_API_INSECURE",
    default=False,
    show_default=True,
    is_flag=True,
    help='HTTPS requests to untrusted hosts is enable.',
)
@help_option
@click.version_option(
    __version__,
    '-v',
    '--version',
    message=('%(prog)s %(version)s')
)
@pass_flow_context
def cli(flow_context, api_key, api_url, api_insecure):
    flow_context.key = api_key
    flow_context.url = api_url
    flow_context.insecure = api_insecure


cli.add_command(deploy)
cli.add_command(finding)
cli.add_command(sast)
cli.add_command(sca)
cli.add_command(vulnerability)

cli.epilog = '''
  Run flow COMMAND --help for more information on a command.
'''
