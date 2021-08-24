import json
import os
from typing import Dict

import click

import anyscale


CREDENTIALS_FILE = "~/.anyscale/credentials.json"


def _validate_credential(token: str) -> None:
    if not token.startswith("sss_"):
        url = anyscale.util.get_endpoint("/credentials")
        raise click.ClickException(
            "Your user credentials are invalid. Please go to "
            f"{url} and follow the instructions to properly set your credentials."
        )


def load_credentials() -> str:
    # The environment variable ANYSCALE_CLI_TOKEN can be used to
    # overwrite the credentials in ~/.anyscale/credentials.json
    env_token = os.environ.get("ANYSCALE_CLI_TOKEN")
    if env_token is not None:
        _validate_credential(env_token)
        return env_token
    path = os.path.expanduser(CREDENTIALS_FILE)
    if not os.path.exists(path):
        url = anyscale.util.get_endpoint("/credentials")
        host = anyscale.util.get_endpoint("")
        raise click.ClickException(
            "Credentials not found. You need to create an account at {} "
            "and then go to {} and follow the instructions.".format(host, url)
        )
    with open(path) as f:
        try:
            credentials: Dict[str, str] = json.load(f)
        except json.JSONDecodeError:
            msg = (
                "Unable to load user credentials.\n\nTip: Try creating your "
                "user credentials again by going to {} and "
                "following the instructions. If this does not work, "
                "please contact Anyscale support!".format(
                    anyscale.util.get_endpoint("/credentials")
                )
            )
            raise click.ClickException(msg)
    received_token = credentials.get("cli_token")
    if received_token is None:
        raise click.ClickException(
            "The credential file is not valid. Please regenerate it by following "
            "the instructions at {}".format(anyscale.util.get_endpoint("/credentials"))
        )
    _validate_credential(received_token)
    return received_token
