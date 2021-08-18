__version__ = "0.10"

import os
from configparser import ConfigParser
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import create_database, drop_database, database_exists


DEFAULT_CONFIG_FILENAME = ".captif-db.ini"
DEFAULT_CONFIG_PATH = Path.home().joinpath(DEFAULT_CONFIG_FILENAME)
DRIVERNAME = "mysql+mysqldb"


def get_config_path():
    config_path_str = os.environ.get("CAPTIF_DB_CONFIG_PATH")
    return DEFAULT_CONFIG_PATH if config_path_str is None else Path(config_path_str)


CONFIG_PATH = get_config_path()


class ConfigError(Exception):
    pass


def config(config_path):
    config_ = ConfigParser()
    config_.read(config_path)
    return config_


def get_config_param(parameter, raise_exception=True, config_path=CONFIG_PATH):
    value = config(config_path).get("GENERAL", parameter, fallback="")

    if value:
        return value

    if raise_exception:
        raise ConfigError(f"'{parameter}' not defined in the config file")

    return None


class Config:

    HOST = get_config_param("host")
    PORT = get_config_param("port")
    USERNAME = get_config_param("username")
    PASSWORD = get_config_param("password")

    SSL_CA = get_config_param("ssl_ca", raise_exception=False)
    SSL_CERT = get_config_param("ssl_cert", raise_exception=False)
    SSL_KEY = get_config_param("ssl_key", raise_exception=False)

    def __init__(self, config_path=CONFIG_PATH):
        """
        Allows a version of the Config object to be generated from a custom config file.

        """
        self.HOST = get_config_param("host", config_path=config_path)
        self.PORT = get_config_param("port", config_path=config_path)
        self.USERNAME = get_config_param("username", config_path=config_path)
        self.PASSWORD = get_config_param("password", config_path=config_path)

        self.SSL_CA = get_config_param("ssl_ca", raise_exception=False, config_path=config_path)
        self.SSL_CERT = get_config_param("ssl_cert", raise_exception=False, config_path=config_path)
        self.SSL_KEY = get_config_param("ssl_key", raise_exception=False, config_path=config_path)

    @classmethod
    def database_connection_str(cls, database):
        return URL.create(
            drivername=DRIVERNAME,
            username=cls.USERNAME,
            password=cls.PASSWORD,
            host=cls.HOST,
            port=cls.PORT,
            database=database,
            query=cls.ssl_args(),
        )

    @classmethod
    def ssl_args(cls):
        ssl_dict = {
            "ssl_ca": cls.SSL_CA,
            "ssl_cert": cls.SSL_CERT,
            "ssl_key": cls.SSL_KEY,
        }
        return {kk: vv for kk, vv in ssl_dict.items() if vv is not None}


class DbSession:
    database = None  # Database name
    base = None  # SQLAlchemy Base object
    factory = None
    engine = None

    @staticmethod
    def create_engine(database, echo=False):
        return create_engine(
            Config.database_connection_str(database),
            echo=echo,
        )

    @classmethod
    def global_init(cls, test_db=False):
        if cls.factory:
            return

        cls.__check_class_definition()

        if test_db:
            cls.database += "_test"

        engine = cls.create_engine(cls.database, echo=test_db)

        cls.engine = engine
        cls.factory = sessionmaker(bind=engine)

        if database_exists(engine.url):
            if test_db:
                drop_database(engine.url)
                create_database(engine.url)
        else:
            create_database(engine.url)

        cls.base.metadata.create_all(engine)

    @classmethod
    def __check_class_definition(cls):
        if (cls.database is None) or (cls.base is None):
            raise NotImplementedError(
                f"class attributes 'database' and 'base' are not defined in "
                f"{cls.__name__} class definition"
            )
