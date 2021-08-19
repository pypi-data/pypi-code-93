from typing import Any, Dict

from dagster import default_executors, executor
from dagster.core.errors import DagsterInvariantViolationError

DAGSTER_CLOUD_EXECUTOR_NAME = "cloud_isolated_step"
DAGSTER_CLOUD_EXECUTOR_CONFIG_SCHEMA: Dict[str, Any] = {}


@executor(
    name=DAGSTER_CLOUD_EXECUTOR_NAME,
    config_schema=DAGSTER_CLOUD_EXECUTOR_CONFIG_SCHEMA,
)
def cloud_isolated_step_executor(_context):
    raise DagsterInvariantViolationError("This executor should never run within user code")


default_cloud_executors = default_executors + [cloud_isolated_step_executor]
