import datetime
from unittest import mock

import pytest
from kubernetes.client import exceptions
from kubernetes.client import models as k8s

from workflows import bases, managers, models, tasks


@pytest.fixture
def manager(mocker):
    mocker.patch("kubernetes.config.load_incluster_config", autospec=True)
    mocker.patch("kubernetes.client.CoreV1Api")  # autospec is slow on this bc it is so large
    dag_run = models.DagRun.objects.create(
        dag="dag1",
        creator="manual",
        created=datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc),
    )
    models.TaskRun.objects.create(dag_run=dag_run, task="1", status=models.TaskStatus.WAITING)
    registry = bases.DagRegistry()
    registry["dag1"] = dag = bases.DAG("some dag", "dags/dag1")
    tasks.NoOp("a task", dag, "1", inputs=[], worker_config={"kube_image": "busybox"})
    return managers.Kubernetes(registry=registry)


@pytest.mark.parametrize(
    "create_response, status",
    [
        (None, models.TaskStatus.RUNNING),
        (exceptions.ApiException(), models.TaskStatus.FAILED),
    ],
)
@pytest.mark.django_db
def test_start_tasks(manager, create_response, status):
    manager.client.create_namespaced_pod.side_effect = create_response
    task_run = models.TaskRun.objects.first()

    manager.start_task(task_run)

    assert manager.client.create_namespaced_pod.call_count == 1
    call_kwargs = manager.client.create_namespaced_pod.call_args[1]
    assert isinstance(call_kwargs["body"], k8s.V1Pod)
    assert call_kwargs["body"].metadata.name == "dag1-1-20100101t000000-1"
    task_run.refresh_from_db()
    assert task_run.status == status

    # should be constant
    assert manager.slots == 20
    assert manager.slots == 20


def mock_response(value):
    response = mock.MagicMock(spec=k8s.V1Pod())
    response.status.phase = value
    return lambda **_: response


@pytest.mark.parametrize(
    "status_response, status",
    [
        (mock_response("Running"), models.TaskStatus.RUNNING),
        (mock_response("Succeeded"), models.TaskStatus.SUCCEEDED),
        (mock_response("Failed"), models.TaskStatus.FAILED),
        (exceptions.ApiException, models.TaskStatus.FAILED),
    ],
)
@pytest.mark.django_db
def test_update_tasks(manager, status_response, status):
    task_run = models.TaskRun.objects.first()
    task_run.status = models.TaskStatus.RUNNING
    task_run.save()
    manager.client.read_namespaced_pod.side_effect = status_response
    manager.client.delete_namespaced_pod.side_effect = status_response

    manager.update_tasks([task_run])

    assert manager.client.read_namespaced_pod.call_count == 1
    assert manager.client.delete_namespaced_pod.call_count == (
        0 if status == models.TaskStatus.RUNNING else 1
    )
    task_run.refresh_from_db()
    assert task_run.status == status


def test_in_cluster_false(mocker):
    mock_config = mocker.patch("kubernetes.config.load_kube_config", autospec=True)
    mocker.patch("kubernetes.client.CoreV1Api", autospec=True)
    registry = bases.DagRegistry()
    registry.worker_config = {"kube_in_cluster": False}
    manager = managers.Kubernetes(registry=registry)
    assert mock_config.call_count == 1

    # test shutdown
    assert manager.shutdown() is True
    assert manager.terminate() is None


def test_safe_label():
    assert (
        managers.Kubernetes._safe_label(
            ["superlonglabelgetstruncatedsomehowsuperlonglabelgetstruncatedsomehow"]
        )
        == "superlonglabelgetstruncatedsomehowsuperlonglabelgetst-05d5aee2c"
    )
