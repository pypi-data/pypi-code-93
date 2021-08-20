import dataclasses
import logging
from typing import Dict

import dacite
from racetrack_client.log.context_error import wrap_context
from racetrack_client.client_config.io import load_client_config, save_client_config
from racetrack_client.client_config.client_config import Credentials, ClientConfig


def set_credentials(repo_url: str, username: str, token_password: str):
    client_config = load_client_config()
    client_config.git_credentials[repo_url] = Credentials(username=username, password=token_password)
    logging.info(f'git credentials added for repo: {repo_url}')
    save_client_config(client_config)


def set_config_var(var_name: str, var_value: str):
    client_config = load_client_config()
    config_dict: Dict = dataclasses.asdict(client_config)

    assert var_name in config_dict, f'client config doesn\'t have variable named {var_name}'
    config_dict[var_name] = var_value
    with wrap_context('converting variable to target data type'):
        client_config = dacite.from_dict(
            data_class=ClientConfig,
            data=config_dict,
            config=dacite.Config(cast=[]),
        )

    logging.info(f'Client variable {var_name} set to: {var_value}')
    save_client_config(client_config)
