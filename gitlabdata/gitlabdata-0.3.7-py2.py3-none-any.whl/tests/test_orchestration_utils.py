import os
import pandas as pd

from gitlabdata.orchestration_utils import (
    snowflake_engine_factory,
    query_executor,
    dataframe_uploader,
)


config_dict = os.environ.copy()


class TestSnowflakeEngineFactory:
    """
    Tests the snowflake_engine_factory.
    """

    config_dict = os.environ.copy()

    def test_connection(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN")
        try:
            connection = engine.connect()
            result = connection.execute("select current_version()").fetchone()[0]
            print(result)
            assert type(result) == str
        finally:
            connection.close()
            engine.dispose()

    def test_database(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN")
        try:
            connection = engine.connect()
            result = connection.execute("select current_database()").fetchone()[0]
            print(result)
            assert result == "TESTING_DB"
        finally:
            connection.close()
            engine.dispose()

    def test_schema(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        try:
            connection = engine.connect()
            result = connection.execute("select current_schema()").fetchone()[0]
            print(result)
            assert result == "GITLAB"
        finally:
            connection.close()
            engine.dispose()


class TestQueryExecutor:
    """
    Tests the query_executor.
    """

    config_dict = os.environ.copy()

    def test_connection(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        query = "select current_version()"
        results = query_executor(engine, query)
        assert type(results[0][0]) == str


class TestDataFrameUploader:
    """
    Tests the dataframe_uploader.
    """

    config_dict = os.environ.copy()

    def test_upload(self):
        """
        Tests that a connection can be made.
        """

        engine = snowflake_engine_factory(config_dict, "SYSADMIN", "GITLAB")
        table = "test_table"
        dummy_dict = {"foo": [1, 2, 3], "bar": [1, 2, 3]}

        # Create a dummy DF to upload
        dummy_df = pd.DataFrame(dummy_dict)
        dataframe_uploader(dummy_df, engine, table)

        query = f"select * from {table}"
        results = query_executor(engine, query)
        query_executor(engine, f"drop table {table}")
        assert results[0][:2] == (1, 1)
