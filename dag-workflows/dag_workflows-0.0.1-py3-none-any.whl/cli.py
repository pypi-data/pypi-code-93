import importlib
import json
import logging
import os
import sys

import click
import django
from django.core import management

from workflows import bases, executor

LOGGER = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.argument("config")
@click.option("-v", "--verbose", "log_level", help="Log debug messages", flag_value=logging.DEBUG)
@click.option("--quiet", "log_level", help="Log fewer messages", flag_value=logging.WARNING)
@click.option("--log-json/--log-text", help="Log JSON messages", envvar="LOG_JSON")
def main(ctx, config, log_level, log_json):
    configure_logging(log_level, log_json)
    LOGGER.info("Workflows starting with configuration module %s", config)
    sys.path.insert(0, os.getcwd())  # hacky? better ideas?
    module = importlib.import_module(config)
    dags = getattr(module, "DAGS")
    if not isinstance(dags, bases.DagRegistry):
        raise click.BadParameter(
            f"Config file {config} must provide a DagRegistry in variable DAGS"
        )
    dags.config_module = config
    ctx.obj = dags


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"severity": record.levelname, "message": super().format(record)})


def configure_logging(log_level, log_json):
    # create a root handler if none exists
    logging.basicConfig(level=log_level or logging.INFO, format="%(name)s - %(message)s")

    if log_json:
        # Override the handler to format as JSON
        root = logging.getLogger()
        for handler in root.handlers:
            handler.setFormatter(JsonFormatter())

        # Prevent exceptions from printing independently of logs
        def log_exception(type, value, traceback):
            logging.error("Uncaught exception.", exc_info=(type, value, traceback))

        sys.excepthook = log_exception


@main.command()
@click.pass_context
@click.argument("dag")
@click.option("-b", "--begin", help="Beginning transformation")
@click.option("-e", "--end", help="Ending transformation")
@click.option("-o", "--only", help="Only run this transformation")
def run(ctx, dag, begin, end, only):
    """Run a series of transformations from a DAG"""
    LOGGER.info("Running DAG %s", dag)
    dag = ctx.obj[dag]
    executor.execute_dag(dag, only or begin, only or end)


@main.command()
@click.pass_context
@click.argument("manager")
def schedule(ctx, manager):
    """Execute all DAGs according to their schedules using the given manager"""

    # configure settings (does nothing if already configured)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workflows.settings")
    django.setup()

    # import the scheduler here after django setup
    from workflows import managers, scheduler

    # run workflows migrations if needed
    management.call_command("migrate", "workflows")

    if manager not in managers.MANAGERS:
        managers = ", ".join(managers.MANAGERS.keys())
        raise click.BadParameter(f"Please specify a supported manager: {managers}")

    registry = ctx.obj
    manager = managers.MANAGERS[manager](registry=registry)
    schedule_ = scheduler.Scheduler(registry, manager)
    schedule_.run()
