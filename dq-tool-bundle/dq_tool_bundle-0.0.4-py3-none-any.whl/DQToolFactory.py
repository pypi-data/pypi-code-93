"""Creating DQTool singleton"""
import os

from pyspark.sql import SparkSession
from box import Box

from dq_tool import DQTool


class DQToolFactory:
    """Factory class for Daipe to provide DQTool singleton instances"""

    def __init__(self, spark: SparkSession, db_store_connection_string: str, db_store_connection: Box):
        """Keep spark session and DB connection at the factory instance level."""
        self._spark = spark
        self._db_store_connection = self._handle_connection_params(
            db_store_connection_string=db_store_connection_string, db_store_connection=db_store_connection
        )

    def create(self) -> DQTool:
        """Construct a DQTool instance and return it"""
        return DQTool(spark=self._spark, db_store_connection=self._db_store_connection)

    _DB_STORE_CONNECTION_KEYS = ("drivername", "host", "port", "database", "username", "password")

    @classmethod
    def _handle_connection_params(cls, db_store_connection_string: str, db_store_connection: Box):
        """Handle database connection from strings and params.
        DB Connection priorities are:
        1. environment connection string
        2. environment parameters (missing pieces filled with config)
        3. config connection string
        4. config parameters
        """
        # handle the db connection priorities
        env_connstr = os.getenv("DQ_TOOL_DB_STORE_CONNECTION_STRING")
        # 1. environment connection string
        if env_connstr:
            return env_connstr
        # 2. environment parameters
        env_params = {k: cls._get_env_value(k) for k in cls._DB_STORE_CONNECTION_KEYS if cls._get_env_value(k)}
        # gaps filled with config params
        params = {**env_params, **{k: v for k, v in db_store_connection.to_dict().items() if v}}
        if env_params:
            return params
        # 3. config connection string
        if db_store_connection_string:
            return db_store_connection_string
        # 4. config params
        if params:
            return params
        return None

    @classmethod
    def _get_env_value(cls, k: str) -> str:
        """Get a value of the corresponding environment variable"""
        return os.getenv("DQ_TOOL_DB_STORE_CONNECTION_{}".format(k.upper()))
