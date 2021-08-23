import signal
import subprocess

import pytest

from workflows import bases, managers, models


@pytest.mark.django_db
def test_advisory_lock():
    assert managers.try_advisory_lock("workflows") is True


@pytest.fixture
def worker():
    dag_run = models.DagRun.objects.create(dag="dag1", creator="manual")
    models.TaskRun.objects.create(dag_run=dag_run, task="1", status=models.TaskStatus.WAITING)
    return managers.Worker(registry=bases.DagRegistry())


@pytest.mark.django_db
def test_worker_run(worker, mocker):
    mock_popen = mocker.patch("subprocess.Popen", autospec=True)
    task_run = models.TaskRun.objects.first()

    worker.start_task(task_run)

    assert mock_popen.call_count == 1
    assert isinstance(worker.task_run, models.TaskRun)
    assert worker.slots == 0

    task_run.refresh_from_db()
    assert task_run.status == models.TaskStatus.RUNNING

    # already running a process, raise exception
    with pytest.raises(AssertionError):
        worker.start_task(task_run)


@pytest.mark.django_db
def test_worker_update(worker, mocker):
    running = models.TaskRun.objects.none()  # not used :shrug:
    task_run = models.TaskRun.objects.first()

    # no process, exits immediately
    worker.update_tasks(running)

    worker.task_run = task_run
    worker.process = process = mocker.Mock(spec=subprocess.Popen)()
    process.stdout.readlines.return_value = ["log message", '{"message": "something"}']
    process.poll.side_effect = [None, 0, 1]

    # still running
    worker.update_tasks(running)
    task_run.refresh_from_db()
    assert task_run.ended is None

    # succeeded
    worker.update_tasks(running)
    task_run.refresh_from_db()
    assert task_run.status == models.TaskStatus.SUCCEEDED

    # failed
    worker.process = process
    worker.task_run = task_run
    worker.update_tasks(running)
    task_run.refresh_from_db()
    assert task_run.status == models.TaskStatus.FAILED


@pytest.mark.parametrize(
    "method, sig",
    [
        ("shutdown", signal.SIGINT),
        ("terminate", signal.SIGTERM),
    ],
)
def test_shutdown_terminate(method, sig, mocker):
    mock_sig = mocker.patch("os.killpg", autospec=True)
    worker = managers.Worker(registry=None)

    # no process, do nothing
    getattr(worker, method)()
    assert mock_sig.call_count == 0

    # add a process
    worker.process = mocker.Mock(spec=subprocess.Popen)()
    worker.process.pid = 10
    getattr(worker, method)()
    assert mock_sig.call_count == 1
