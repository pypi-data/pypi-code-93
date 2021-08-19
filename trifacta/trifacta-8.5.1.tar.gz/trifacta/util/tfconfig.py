import configparser
import os
from pathlib import Path

CONFIG_FILE_PATH = str(Path.home()) + "/.trifacta.py.conf"
CONFIGURATION = "CONFIGURATION"


def check_config(filepath: str = CONFIG_FILE_PATH):
    raw_config, config_exist = read_raw_config(filepath)

    if not config_exist or CONFIGURATION not in raw_config:
        raise (
            PermissionError(
                "Trifacta access has not been configured. Try running setup_configuration()"
            )
        )
    config, config_exist = read_config(filepath)
    # generate KeyError for any missing keys
    config["username"]
    config["endpoint"]
    config["token"]
    return True


def setup_configuration(
        username: str, token: str, endpoint: str = "http://localhost:3005",
        filepath: str = CONFIG_FILE_PATH
):
    config = configparser.ConfigParser()

    config[CONFIGURATION] = {"username": username, "endpoint": endpoint, "token": token}

    with open(filepath, "w") as f:
        config.write(f)

    check_config(filepath)
    # print_raw_config(config)


def read_raw_config(filepath: str = CONFIG_FILE_PATH) -> (configparser.ConfigParser, bool):
    if not os.path.isfile(filepath):
        return None, False

    config = configparser.ConfigParser()
    config.read(filepath)
    return config, True


def read_config(filepath: str = CONFIG_FILE_PATH) -> (configparser.ConfigParser, bool):
    config, config_exist = read_raw_config(filepath)
    if not config_exist:
        return None, False
    return config[CONFIGURATION], config_exist

# def print_raw_config(config: configparser.ConfigParser):
#     for each_section in config.sections():
#         print(each_section)
#         for (each_key, each_val) in config.items(each_section):
#             print("- ", each_key + ": ", each_val)
