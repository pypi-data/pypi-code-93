import logging
import os
import sys

import pytest
from click.testing import CliRunner

from workflows import bases, cli


def test_cli_no_dag(mocker):
    mock_import = mocker.patch("importlib.import_module", autospec=True)
    mock_import.return_value.DAGS = None
    runner = CliRunner()
    result = runner.invoke(cli.main, ["config_module", "run", "dag_name"])
    assert result.exit_code == 2
    assert "must provide a DagRegistry" in result.output


def test_cli_run(mocker):
    mock_import = mocker.patch("importlib.import_module", autospec=True)
    registry = bases.DagRegistry()
    registry["dag_name"] = mocker.sentinel.DAG
    mock_import.return_value.DAGS = registry
    mock_execute = mocker.patch("workflows.executor.execute_dag", autospec=True)
    runner = CliRunner()
    result = runner.invoke(cli.main, ["config_module", "run", "dag_name"])
    assert result.exit_code == 0
    mock_import.assert_called_once_with("config_module")
    mock_execute.assert_called_once_with(mocker.sentinel.DAG, None, None)


def test_cli_run_dag_load_exception(mocker):
    mock_import = mocker.patch("importlib.import_module", autospec=True)
    registry = bases.DagRegistry()
    registry["dag_name"] = RuntimeError("asdf")
    mock_import.return_value.DAGS = registry
    runner = CliRunner()
    result = runner.invoke(cli.main, ["config_module", "run", "dag_name"])
    assert result.exit_code == 1
    assert "failed to load" in str(result.exception)


def test_logging_config(caplog):
    cli.configure_logging(None, True)
    try:
        raise RuntimeError()
    except RuntimeError:
        logging.exception("woops")
    assert caplog.text.startswith(
        # can't assert the full message because the file path changes on each computer
        '{"severity": "ERROR", "message": "woops\\nTraceback (most recent call last):\\n  File'
    )


def test_excepthook(caplog):
    cli.configure_logging(None, True)
    sys.excepthook(RuntimeError, RuntimeError(), None)
    assert (
        caplog.text == '{"severity": "ERROR", "message": "Uncaught exception.\\nRuntimeError"}\n'
    )


@pytest.mark.django_db
def test_cli_schedule(mocker):
    mock_import = mocker.patch("importlib.import_module", autospec=True)
    mock_import.return_value.DAGS = bases.DagRegistry()
    mock_schedule = mocker.patch("workflows.scheduler.Scheduler", autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli.main, ["config_module", "schedule", "worker"])
    assert result.exit_code == 0, result.exception
    assert mock_schedule.call_count == 1


def test_scheduler_settings(mocker):
    # test error message if not set
    mocker.patch.dict(os.environ, {"DATABASE_URL": ""})
    with pytest.raises(RuntimeError, match="workflows scheduler requires"):
        import workflows.settings  # noqa

    # test value is set
    mocker.patch.dict(os.environ, {"DATABASE_URL": "postgres://test"})
    from workflows import settings

    assert settings.DATABASE_URL == "postgres://test"
