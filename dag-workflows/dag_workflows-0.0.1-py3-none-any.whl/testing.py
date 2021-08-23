"""
This module provides a fixture for writing unit tests. It requires pytest-django by default but
you can override the `conn` fixtures to provide a different db setup and connection,
ie without Django. See https://docs.pytest.org/en/6.2.x/fixture.html#override-fixtures

The fixture should be registered automatically. To use it:

    def test_my_transform(workflows):
        workflows.execute_task("my_dag", "my_transform.sql")
        rows = workflows.execute_sql("SELECT * FROM my_transform")
        assert len(rows) == 1

"""
import os

import pytest

from workflows import bases, executor


@pytest.fixture()
def conn():
    """
    This fixture returns a connection to the test database. The
    connection should have an open transaction which will be rolled
    back after the test to avoid interference between tests. Override
    this fixture to provide a different connection, ie without Django.
    """
    from django.db import connection

    return connection.connection


@pytest.fixture()
def workflows(mocker, db, conn):
    """
    This fixture provides methods for testing workflows. It uses the
    database connection provided by `conn` to run the populate the context
    with a 'DATABASE_URL'.
    """

    class WorkflowsTestFixture:
        @staticmethod
        def setup_task_inputs(task: bases.Task, values: dict = None):
            """Use this method to create input tables and populate them before running
            your task. It calls setup() on each output of the input tasks."""
            values = values or {}
            for input_name in task.inputs:
                input_dag = task.dag.name
                if ":" in input_name:  # task external to this dag
                    input_dag, input_name = input_name.split(":")
                input_ = task.dag.registry[input_dag].get_task(input_name)
                for output in input_.outputs:
                    output.test_setup({"conn": conn}, values.get(output.name))

        @staticmethod
        def execute_task(task: bases.Task, parameters: dict = None):
            context = {"DATABASE_URL": "test"}
            context.update(parameters or {})
            task.execute(context)

            # return the current table state
            return {output.name: output.test_results({"conn": conn}) for output in task.outputs}

        @staticmethod
        def execute_dag(dag: bases.DAG, env_vars: dict = None, begin: str = None, end: str = None):
            """Run an entire DAG"""
            context = {"DATABASE_URL": "test"}
            context.update(env_vars or {})
            mocker.patch.dict(os.environ, context)
            executor.execute_dag(dag, begin, end)

        @staticmethod
        def execute_sql(sql: str):
            cursor = conn.cursor()
            cursor.execute(sql)
            try:
                return cursor.fetchall()
            except conn.DatabaseError:
                return  # statement returns no rows

    # the mock bypasses the context manager, thus avoiding a commit during tests
    mock_connect = mocker.patch("workflows.tasks.get_db_connection", autospec=True)
    mock_connect.return_value.__enter__.return_value = conn
    return WorkflowsTestFixture()
