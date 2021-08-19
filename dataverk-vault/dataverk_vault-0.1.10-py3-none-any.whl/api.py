import os
import json
from dataverk_vault.connectors.vault import VaultConnector
from dataverk_vault.context.settings import read_environment_settings


def read_secrets():
    """ Read secrets from vault

    :return: dictionary with secrets from vault
    """
    secrets = read_environment_settings()
    with VaultConnector(secrets) as vault_conn:
        return vault_conn.read_secrets()


def set_secrets_as_envs():
    """ Read secrets from vault and set environment variables

    :return: None
    """
    secrets = read_secrets()
    os.environ.update(
        {key: (value if not isinstance(value, dict) else json.dumps(value)) for key, value in secrets.items()})


def get_database_creds(vault_path):
    """ Fetch new database credentials

    :param vault_path
    :return: database credentials: str in format "<username>:<password>"
    """
    secrets = read_environment_settings()
    with VaultConnector(secrets) as vault_conn:
        return vault_conn.get_db_credentials(vault_path)
