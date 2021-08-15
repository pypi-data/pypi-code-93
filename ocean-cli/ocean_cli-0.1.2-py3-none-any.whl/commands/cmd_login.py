import click
from getpass import getpass

from ocean import api, code
from ocean.main import pass_env


@click.command()
@pass_env
def cli(ctx):
    email = click.prompt("Email")
    password = getpass("Password: ")

    res = api.post(ctx, code.API_SIGNIN, {code.EMAIL: email, code.PASSWORD: password})

    if res.status_code == 200:
        body = res.json()
        ctx.update_config(code.TOKEN, body.get(code.TOKEN))
        ctx.update_config("uuid", body.get("user").get("uuid"))
        ctx.update_config("username", body.get("user").get("email").split("@")[0])
        click.echo("Login Success.")
    else:
        click.echo("Login Failed.")
