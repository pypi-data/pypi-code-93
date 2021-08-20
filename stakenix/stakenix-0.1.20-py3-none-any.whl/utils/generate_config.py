from pathlib import Path
from sys import platform
from yaml import safe_dump

FOLDER_PATH = Path.home().joinpath(".stakenix")
CONFIG_PATH = FOLDER_PATH.joinpath("config.yaml")


def generate_config() -> None:
    config = {
        "sql": {
            "mysql": {
                "driver": {"name": "mysql+mysqlconnector", "connection_args": {}},
                "databases": {
                    "default": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_password",
                    },
                    "lucky_partners": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_password",
                    },
                    "lucky_partners_backup": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_password",
                    }
                },
            },
            "postgresql": {
                "driver": {
                    "name": "postgresql",
                    "connection_args": {"options": "-csearch_path={}"},
                },
                "databases": {
                    "default": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "database_name": "analyst_db",
                    },
                    "alpa": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_username",
                        "database_name": "rocketplay",
                    },
                    "tableau": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "database_name": "workgroup",
                    },
                },
            },
            "clickhouse": {
                "driver": {"name": "clickhouse", "connection_args": {}},
                "databases": {
                    "default": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_username",
                    }
                },
            },
            "mssql": {
                "driver": {
                    "name": "mssql+pymssql" if platform == "linux" else "mssql",
                    "connection_args": {}
                    if platform == "linux"
                    else {"driver": "ODBC Driver 17 for SQL Server"},
                },
                "databases": {
                    "default": {
                        "host": "place_for_host",
                        "port": "place_for_port",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "database_name": "BPMonline7102CustomerCenterSoftkeyRUS_1453921_0613",
                    }
                },
            },
        },
        "nosql": {
            "mongodb": {
                "databases": {
                    "pobeda": {
                        "database_name": "pobeda",
                        "host": "place_for_host",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "ssh_host": "place_for_ssh_host",
                        "ssh_username": "place_for_username",
                    },
                    "lara": {
                        "database_name": "lotoru",
                        "host": "place_for_host",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "ssh_host": "place_for_ssh_host",
                        "ssh_username": "place_for_username",
                    },
                    "vipt": {
                        "database_name": "vipt",
                        "host": "place_for_host",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "ssh_host": "place_for_ssh_host",
                        "ssh_username": "place_for_username",
                    },
                    "mk5": {
                        "database_name": "vulkan",
                        "host": "place_for_host",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "ssh_host": "place_for_ssh_host",
                        "ssh_username": "place_for_username",
                    },
                    "vipclub": {
                        "database_name": "vipclub",
                        "host": "place_for_host",
                        "username": "place_for_username",
                        "password": "place_for_password",
                        "ssh_host": "place_for_ssh_host",
                        "ssh_username": "place_for_username",
                    },
                }
            }
        },
        "grafana": {
            "url": "place_for_url",
            "headers": {
                "Authorization": "place_for_header",
                "Content-Type": "place_for_header",
                "Accept": "place_for_header",
            },
        },
    }

    if not FOLDER_PATH.exists():
        FOLDER_PATH.mkdir()

    with open(CONFIG_PATH, "w") as file:
        safe_dump(config, file, sort_keys=False)

    print("Config successfully generated")
    print(f"Path to config: {CONFIG_PATH}")


if __name__ == "__main__":

    if CONFIG_PATH.exists():
        print(f"There is already a config. Do you want to rewrite it? [y/n]: ", end="")

    answer = ""
    retries = 3
    while answer not in ["y", "n"]:
        retries -= 1

        answer = input()

        if retries == 0:
            print("\nAttempts exhausted.")
            break

        if answer == "y":
            generate_config()
        elif answer == "n":
            print(f"\nDeclined. Closing module.")
            break
        else:
            print("Wrong input. Possible values [y/n]. Please try again: ", end="")