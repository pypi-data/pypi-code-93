import click
from sdccli.cli.settings.notification import notification
from sdccli.cli.settings.user import user
from sdccli.cli.settings.team import team
from sdccli.cli.settings.access_key import access_key


@click.group(short_help='Settings operations')
@click.option('--secure', is_flag=True, help='Work with Sysdig Secure settings instead of Sysdig Monitor')
@click.pass_obj
def settings(cnf, secure):
    cnf.sd = cnf.sdsecure if secure else cnf.sdmonitor


settings.add_command(notification)
settings.add_command(user)
settings.add_command(team)
settings.add_command(access_key)
