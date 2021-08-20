import logging
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_SERVER = "https://ql.abzu.ai"

CONFIG_FILE_SEARCH_PATHS = [
    Path.home().joinpath(".config/.feynrc"),
    Path.home().joinpath(".config/feyn.ini"),
    Path.home().joinpath(".feynrc"),
    Path.home().joinpath("feyn.ini"),
]

resolve_config_failed_message = """Could not resolve `server` and `api_token` from configuration file.
Please either put a configuration file named [.feynrc] or [feyn.ini] in your home folder."""

_config_resolver = None


class Config:
    def __init__(self, qlattice: str, api_token: str = None, server: str = None):
        self.qlattice = qlattice
        self.api_token = api_token
        self.server = server or DEFAULT_SERVER


def resolve_config(section=None) -> Optional[Config]:
    # This is here in order to be able to override the configs from tests
    if _config_resolver:
        return _config_resolver(section)  # noqa

    return _resolve_config(section, config_search_paths=CONFIG_FILE_SEARCH_PATHS)


def _resolve_config(section, config_search_paths) -> Optional[Config]:
    # If section specified. Find it in one of the possible configuration file paths
    if section:
        logger.debug("Section [{section}] specified. Searching for config files..")
        config_file = _find_config_file(config_search_paths)

        if config_file is None:
            raise FileNotFoundError(f"Configuration file not found. Searched: {[str(x) for x in config_search_paths]}.")

        logger.debug(f"Found [{config_file}]. Loading the configuration.")
        return _load_from_ini_file(config_file, section)

    # Fall back to first section in a config file
    logger.debug("No luck. Searching for a configuration file instead..")
    config_file = _find_config_file(config_search_paths)
    if config_file:
        logger.debug(f"Found [{config_file}]. Loading the configuration from the first section.")
        first_section = _get_first_section(config_file)
        return _load_from_ini_file(config_file, first_section)

    # Found no configs anywhere
    logger.debug(f"Configuration not resolved. Searched for the configuration in env-vars and files. No luck.")
    return None


def _load_from_ini_file(path, section_name) -> Config:
    parser = ConfigParser()
    parser.read(path)

    if section_name not in parser.sections():
        raise ValueError(f"[{section_name}] not found in configuration file.")

    section = parser[section_name]

    # Next step. Remove this completely
    if "url" in section:
        raise ValueError(f"The parameter `url` in configuration file: {path} is no longer supported. "
                       f"Please use the `server` and `qlattice` parameters instead. "
                       f"Example:\n"
                       f"\n"
                       f"[production]\n"
                       f"qlattice=a1b2c3\n"
                       f"api_token=token\n"
                       f"\n"
                       f"[stage]\n"
                       f"server=https://qlattice.stage.abzu.ai\n"
                       f"qlattice=a1b2c3\n"
                       f"api_token=token\n"
                       f"\n"
                       f"See documentation for more information: "
                       f"https://docs.abzu.ai/docs/guides/setup/accessing.html")

    if "qlattice" not in section:
        raise ValueError(f"[qlattice] not found in configuration.")

    return Config(section["qlattice"], section.get("api_token"), section.get("server"))


def _find_config_file(search_paths):
    existing_config_files = [x for x in search_paths if Path(x).exists()]

    if len(existing_config_files) > 1:
        raise ValueError(f"Multiple configuration files found: {[str(x) for x in existing_config_files]}.")

    if existing_config_files:
        return existing_config_files[0]

    return None


def _get_first_section(path):
    parser = ConfigParser()
    parser.read(path)
    section_names = parser.sections()

    if not section_names:
        raise ValueError(f"No sections found in configuration file.")

    return section_names[0]
