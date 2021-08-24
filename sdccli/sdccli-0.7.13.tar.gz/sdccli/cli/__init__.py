import click
import sys
from sdccli.cli.alert import alert
from sdccli.cli.backup import backup
from sdccli.cli.capture import capture
from sdccli.cli.command import command
from sdccli.cli.compliance import compliance
from sdccli.cli.dashboard import dashboard
from sdccli.cli.eventv1 import eventv1
from sdccli.cli.event import event
from sdccli.cli.policy import policy
from sdccli.cli.scanning import scanning
from sdccli.cli.settings import settings
from sdccli.cli.profile import profile
from sdccli.cli.dashboardv2 import dashboard_v2
from sdccli.config import Config
from sdccli import __version__


if sys.version_info.major < 3:
    print("Warning: You are using python {}.{}, it's recommended to use python 3".format(sys.version_info.major, sys.version_info.minor))
    print("         reinstall it using python3:")
    print("         $ python3 setup.py install")
    print("")


@click.group()
@click.option("-c", "--config",
              help="Uses the provided file as a config file. If the config file is not provided, it will be "
                   "searched at ~/.config/sdc-cli/config.yml and /etc/sdc-cli/config.yml.")
@click.option("-e", "--env", help="Uses a preconfigured environment in the config file. If it's not provided, "
                                  "it will use the 'main' environment or retrieve it from the env var SDC_ENV.")
@click.option("--json", is_flag=True, help="Output raw API JSON")
@click.version_option(__version__, '-v', '--version')
@click.pass_context
def cli(ctx, config, env, json):
    """
    You can provide the monitor/secure tokens by the SDC_MONITOR_TOKEN and SDC_SECURE_TOKEN environment variables.
    """
    cnf = Config(json)
    cnf.load(config, env)
    ctx.obj = cnf


cli.add_command(alert)
cli.add_command(backup)
cli.add_command(capture)
cli.add_command(command)
cli.add_command(compliance)
cli.add_command(dashboard)
cli.add_command(eventv1)
cli.add_command(event)
cli.add_command(policy)
cli.add_command(scanning)
cli.add_command(profile)
cli.add_command(settings)
cli.add_command(dashboard_v2)

if getattr(sys, 'frozen', False):
    cli(sys.argv[1:])
