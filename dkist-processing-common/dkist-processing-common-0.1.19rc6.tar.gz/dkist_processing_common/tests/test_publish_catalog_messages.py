from pathlib import Path

import pytest

from dkist_processing_common.tasks.l1_output_data import PublishCatalogMessages


@pytest.fixture
def publish_catalog_messages_task(recipe_run_id):
    with PublishCatalogMessages(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        proposal_id = "publish_catalog_messages_proposal_id"
        task.constants["PROPOSAL_ID"] = proposal_id
        yield task, proposal_id
        task.constants.purge()


def test_frame_messages(publish_catalog_messages_task):
    """
    :Given: a PublishCatalogMessages task
    :When: creating frame messages
    :Then: the attributes are correctly populated
    """
    task, proposal_id = publish_catalog_messages_task
    filenames = [f"test_frame_{i}.ext" for i in range(10)]
    print(filenames)
    filepaths = [Path(f"a/b/c/{filename}") for filename in filenames]
    frame_messages = task.frame_messages(paths=filepaths)
    for message in frame_messages:
        assert message.bucket == "data"
        assert proposal_id in message.objectName
        assert message.conversationId == str(task.recipe_run_id)


def test_object_messages(publish_catalog_messages_task):
    """
    :Given: a PublishCatalogMessages task
    :When: creating object messages
    :Then: the attributes are correctly populated
    """
    task, proposal_id = publish_catalog_messages_task
    object_type = "test_type"
    filenames = [f"test_object_{i}.ext" for i in range(10)]
    print(filenames)
    filepaths = [Path(f"a/b/c/{filename}") for filename in filenames]
    object_messages = task.object_messages(paths=filepaths, object_type=object_type)
    for message in object_messages:
        assert message.bucket == "data"
        assert proposal_id in message.objectName
        assert message.conversationId == str(task.recipe_run_id)
        assert message.objectType == object_type
        assert message.groupId == task.dataset_id
