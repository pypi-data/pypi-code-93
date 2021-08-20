from os import getenv
from pathlib import Path
from sys import platform
from yaml import safe_dump


def generate_env_config() -> None:
    config = {
        "sql": {
            "mysql": {
                "driver": {"name": "mysql+mysqlconnector", "connection_args": {}},
                "databases": {
                    "default": {
                        "host": getenv("MYSQL_DEFAULT_HOST"),
                        "port": getenv("MYSQL_DEFAULT_PORT"),
                        "username": getenv("MYSQL_DEFAULT_USERNAME"),
                        "password": getenv("MYSQL_DEFAULT_PASSWORD"),
                    },
                    "lucky_partners": {
                        "host": getenv("MYSQL_LP_HOST"),
                        "port": getenv("MYSQL_LP_PORT"),
                        "username": getenv("MYSQL_LP_USERNAME"),
                        "password": getenv("MYSQL_LP_PASSWORD"),
                    },
                     "lucky_partners_backup": {
                        "host": getenv("MYSQL_LP_BACKUP_HOST"),
                        "port": getenv("MYSQL_LP_BACKUP_PORT"),
                        "username": getenv("MYSQL_LP_BACKUP_USERNAME"),
                        "password": getenv("MYSQL_LP_BACKUP_PASSWORD"),
                    },
                },
            },
            "postgresql": {
                "driver": {
                    "name": "postgresql",
                    "connection_args": {"options": "-csearch_path={}"},
                },
                "databases": {
                    "default": {
                        "host": getenv("PG_DEFAULT_HOST"),
                        "port": getenv("PG_DEFAULT_PORT"),
                        "username": getenv("PG_DEFAULT_USERNAME"),
                        "password": getenv("PG_DEFAULT_PASSWORD"),
                        "database_name": "analyst_db",
                    },
                    "alpa": {
                        "host": getenv("PG_ALPA_HOST"),
                        "port": getenv("PG_ALPA_PORT"),
                        "username": getenv("PG_ALPA_USERNAME"),
                        "password": getenv("PG_ALPA_PASSWORD"),
                        "database_name": "rocketplay",
                    },
                    "tableau": {
                        "host": getenv("PG_TABLEAU_HOST"),
                        "port": getenv("PG_TABLEAU_PORT"),
                        "username": getenv("PG_TABLEAU_USERNAME"),
                        "password": getenv("PG_TABLEAU_PASSWORD"),
                        "database_name": "workgroup",
                    }
                },
            },
            "clickhouse": {
                "driver": {"name": "clickhouse", "connection_args": {}},
                "databases": {
                    "default": {
                        "host": getenv("CH_DEFAULT_HOST"),
                        "port": getenv("CH_DEFAULT_PORT"),
                        "username": getenv("CH_DEFAULT_USERNAME"),
                        "password": getenv("CH_DEFAULT_PASSWORD"),
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
                        "host": getenv("MSSQL_DEFAULT_HOST"),
                        "port": getenv("MSSQL_DEFAULT_PORT"),
                        "username": getenv("MSSQL_DEFAULT_USERNAME"),
                        "password": getenv("MSSQL_DEFAULT_PASSWORD"),
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
                        "host": getenv("POBEDA_MONGODB_HOST"),
                        "username": getenv("POBEDA_MONGODB_USERNAME"),
                        "password": getenv("POBEDA_MONGODB_PASSWORD"),
                        "ssh_host": getenv("POBEDA_SSH_HOST"),
                        "ssh_username": getenv("POBEDA_SSH_USERNAME"),
                    },
                    "lara": {
                        "database_name": "lotoru",
                        "host": getenv("LARA_MONGODB_HOST"),
                        "username": getenv("LARA_MONGODB_USERNAME"),
                        "password": getenv("LARA_MONGODB_PASSWORD"),
                        "ssh_host": getenv("LARA_SSH_HOST"),
                        "ssh_username": getenv("LARA_SSH_USERNAME"),
                    },
                    "vipt": {
                        "database_name": "vipt",
                        "host": getenv("VIPT_MONGODB_HOST"),
                        "username": getenv("VIPT_MONGODB_USERNAME"),
                        "password": getenv("VIPT_MONGODB_PASSWORD"),
                        "ssh_host": getenv("VIPT_SSH_HOST"),
                        "ssh_username": getenv("VIPT_SSH_USERNAME"),
                    },
                    "mk5": {
                        "database_name": "vulkan",
                        "host": getenv("MK5_MONGODB_HOST"),
                        "username": getenv("MK5_MONGODB_USERNAME"),
                        "password": getenv("MK5_MONGODB_PASSWORD"),
                        "ssh_host": getenv("MK5_SSH_HOST"),
                        "ssh_username": getenv("MK5_SSH_USERNAME"),
                    },
                    "vipclub": {
                        "database_name": "vipclub",
                        "host": getenv("VIPCLUB_MONGODB_HOST"),
                        "username": getenv("VIPCLUB_MONGODB_USERNAME"),
                        "password": getenv("VIPCLUB_MONGODB_PASSWORD"),
                        "ssh_host": getenv("VIPCLUB_SSH_HOST"),
                        "ssh_username": getenv("VIPCLUB_SSH_USERNAME"),
                    },
                }
            }
        },
        "grafana": {
            "url": getenv("GRAFANA_URL"),
            "headers": {
                "Authorization": getenv("GRAFANA_AUTH"),
                "Content-Type": getenv("GRAFANA_CONTENT_TYPE"),
                "Accept": getenv("GRAFANA_ACCEPT"),
            },
        },
    }

    path = Path.home().joinpath(".stakenix")
    config_path = path.joinpath("config.yaml")

    if not path.exists():
        path.mkdir()

    with open(config_path, "w") as file:
        safe_dump(config, file, sort_keys=False)

    print("Config successfully generated")
    print(f"Path to config: {config_path}")


if __name__ == "__main__":
    generate_env_config()