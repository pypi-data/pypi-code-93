from pathlib import Path
from typing import Dict, Tuple, Type, TypeVar
from pydantic import BaseSettings
import logging
from os import environ as env

log_level = getattr(
    logging, env.get("CRYPTOSHRED_LOG_LEVEL", "WARNING").upper(), 30
)  # Setting a default here is pretty defensive. Anyhow nothing lost by doing it

log = logging.getLogger()
log.setLevel(log_level)

C = TypeVar("C", bound="Configuration.Config")


class Configuration(BaseSettings):
    dynamo_backend_iv_param: str
    dynamo_backend_table_name: str = "cryptoshred-keys"

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls: Type[C],
            init_settings: Dict,
            env_settings: Dict,
            file_secret_settings: Dict,
        ) -> Tuple:
            return (env_settings, init_settings, file_secret_settings)


def get_configuration(
    profile: str = "default", *, config_dir: Path = Path.home().joinpath(".cryptoshred")
) -> Configuration:
    log.info("Getting Configuration")

    if profile:
        env_file_location = config_dir.joinpath(f"{profile}.env").absolute()
        return Configuration(_env_file=env_file_location)

    return Configuration()
