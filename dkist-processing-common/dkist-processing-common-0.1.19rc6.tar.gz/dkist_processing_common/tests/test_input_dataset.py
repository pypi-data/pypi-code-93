import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.base import WorkflowDataTaskBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin


class Task(WorkflowDataTaskBase, InputDatasetMixin):
    def run(self):
        pass


INPUT_DATASET_STRING = '{"bucket": "bucket-name", "parameters": [{"parameterName": "param_name", "parameterValues": [{"parameterValueId": 1, "parameterValue": "[[1,2,3],[4,5,6],[7,8,9]]", "parameterValueStartDate": "2000-01-01"}]}], "frames": ["objectKey1", "objectKey2", "objectKeyN"]}'


@pytest.fixture
def input_dataset(tmp_path, recipe_run_id):
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        file_path = task.scratch.workflow_base_path / Path(f"{uuid4().hex[:6]}.ext")
        file_path.write_text(data=INPUT_DATASET_STRING)
        task.tag(path=file_path, tags=Tag.input_dataset())
        input_dataset_object = json.loads(INPUT_DATASET_STRING)
        yield task, input_dataset_object
        task.scratch.purge()
        task.constants.purge()


@pytest.fixture
def multiple_input_datasets(tmp_path, recipe_run_id):
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        for _ in range(2):
            file_path = task.scratch.workflow_base_path / f"{uuid4().hex[:6]}.ext"
            file_path.write_text(data=INPUT_DATASET_STRING)
            task.tag(path=file_path, tags=Tag.input_dataset())
        yield task
        task.scratch.purge()
        task.constants.purge()


def test_input_dataset_document(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: reading the input dataset document
    Then: it matches the string used to create the input dataset
    """
    task, input_dataset_object = input_dataset
    task()
    assert task.input_dataset_document == input_dataset_object


def test_multiple_input_datasets(multiple_input_datasets):
    """
    Given: a task with the InputDatasetMixin and multiple tagged input datasets
    When: reading the input dataset document
    Then: an error is raised
    """
    task = multiple_input_datasets
    with pytest.raises(ValueError):
        task.input_dataset_document


def test_no_input_datasets(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: deleting the input dataset tag and then trying to read the input dataset document
    Then: the input dataset document is empty
    """
    task, _ = input_dataset
    task.scratch._tag_db.clear_tag(tag=Tag.input_dataset())
    assert task.input_dataset_document == dict()


def test_input_dataset_frames(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: getting the frames in the input dataset
    Then: it matches the frames used to create the input dataset
    """
    task, input_dataset_object = input_dataset
    assert task.input_dataset_frames == input_dataset_object.get("frames")


def test_input_dataset_bucket(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: getting the bucket in the input dataset
    Then: it matches the bucket used to create the input dataset
    """
    task, input_dataset_object = input_dataset
    assert task.input_dataset_bucket == input_dataset_object.get("bucket")


def test_input_dataset_parameters(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: getting the parameters in the input dataset
    Then: the names of the parameters match the keys in the returned dictionary
    """
    task, input_dataset_object = input_dataset
    for key, value in task.input_dataset_parameters.items():
        assert key == input_dataset_object["parameters"][0]["parameterName"]


def test_input_dataset_parameters_get(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: asking for a specific parameter value
    Then: the correct value or default is returned
    """
    task, input_dataset_object = input_dataset
    assert task.input_dataset_parameters_get("param_name") == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_input_dataset_parameters_get_default(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: asking for a specific parameter value that does not exist
    Then: the default value is returned
    """
    task, input_dataset_object = input_dataset
    assert task.input_dataset_parameters_get("not_here", default=13) == 13


def test_input_dataset_parameters_get_out_of_range(input_dataset):
    """
    Given: a task with the InputDatasetMixin
    When: asking for a specific parameter value at a time that is too far in the past
    Then: an error is raised
    """
    task, input_dataset_object = input_dataset
    with pytest.raises(ValueError):
        _ = task.input_dataset_parameters_get("param_name", start_date=datetime(1776, 7, 4))
