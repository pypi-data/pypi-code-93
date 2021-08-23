import pytest
from django.db import connection

from workflows import bases, tasks


@pytest.fixture
def params():
    return {
        "description": "test task",
        "dag": bases.DAG(description="test DAG", folder="none"),
        "name": "some_file.py",
        "inputs": [],
        "outputs": [],
    }


def test_noop_task(params):
    task = tasks.NoOp(**params)
    assert task.class_parameters == ()
    assert task.execute({}) is None


def test_python_task(params, mocker):
    mock_run = mocker.Mock()
    task = tasks.Python(run=mock_run, **params)  # pragma: no cover

    task.execute({})

    assert task.class_parameters == ()
    mock_run.assert_called_once_with({"conn": None})


@pytest.mark.django_db
def test_sql_task(params, dsn, mocker):
    mock_connect = mocker.patch("psycopg2.connect", autospec=True)
    mock_connect.return_value.__enter__.return_value = connection
    task = tasks.Sql(sql="CREATE TABLE blah (a int)", **params)
    assert task.class_parameters == ("DATABASE_URL",)

    context = {"DATABASE_URL": "none"}
    task.execute(context)

    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM blah")
    assert cursor.fetchone()[0] == 0


def test_big_query_sql(mocker, params):
    mock_bq = mocker.patch("google.cloud.bigquery.Client", autospec=True)
    mock_bq.return_value.query.return_value.total_bytes_billed = 0
    task = tasks.BigQuerySql(sql="SELECT *", **params)  # pragma: no cover
    context = {"GCP_PROJECT": "test"}

    task.execute(context)

    assert task.class_parameters == ("GCP_PROJECT",)
    assert mock_bq.return_value.query.called
    assert mock_bq.return_value.query.return_value.result.called
