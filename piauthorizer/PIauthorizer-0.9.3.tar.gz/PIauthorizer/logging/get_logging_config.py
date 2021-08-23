import configparser
import os
from pathlib import Path


def get_logging_config(config_path: str) -> configparser.ConfigParser:
    """Generate a configuration object from a logging config file by adding an externally specified log level (if available)

    Args:
        config_path (str): path to the logging.conf file

    Raises:
        ValueError: If the externally specified log level is invalid

    Returns:
        configparser.ConfigParser: a ConfigParser object used to set up the logging config
    """
    if not Path(config_path).is_file():
        raise ValueError(
            f"Provided logging config file does not exist: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_path)

    external_log_level = os.environ.get("LOG_LEVEL")

    if external_log_level:
        python_logging_levels = (
            'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET')

        if external_log_level not in python_logging_levels:
            raise ValueError(
                f"External logging level is invalid: '{external_log_level}'. "
                f"Please use one of the following: {python_logging_levels}")
        print(f"Setting LOG_LEVEL from ENV VAR to '{external_log_level}'")

        handlers = [x for x in config.sections() if x.startswith("handler_")]

        for h in handlers:
            config[h]['level'] = external_log_level
    else:
        print("LOG_LEVEL not set externally. Using specified level from the configuration file.")

    return config
