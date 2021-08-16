import pytest

from prunner.main import Executioner
from prunner.tasks import TaskStrategy

CONFIG_DIR = "example"


@pytest.fixture
def executor():
    return Executioner({"PRUNNER_CONFIG_DIR": CONFIG_DIR})


def test_execute_pipeline(executor):
    executor.execute_pipeline("structural")


def test_get_pipeline_that_dont_exists(executor: Executioner):
    with pytest.raises(ValueError):
        executor.get_task("Doesn't exist")


def test_get_pipeline_that_exists(executor: Executioner):
    task = executor.get_task("generate_file")
    assert isinstance(task, TaskStrategy)
