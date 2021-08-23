import signal

import pytest
from dateutil.relativedelta import relativedelta

from workflows import bases, managers, models, scheduler


@pytest.fixture
def schedule_(mocker):
    registry = bases.DagRegistry()
    # schedule is monthly on the first at midnight
    registry["dag1"] = dag = bases.DAG("description", "dags/dag1", schedule="0 0 1 * *")
    dag.graph.add_edge("1", "2")
    dag.graph.add_edge("other:1", "2")
    registry["no_schedule"] = bases.DAG("description", "dags/dag1")
    return scheduler.Scheduler(registry, mocker.Mock())


@pytest.mark.django_db
def test_trigger_dags(schedule_):
    # not triggered yet
    schedule_.trigger_dags()
    assert models.DagRun.objects.count() == 0

    # first dag run, pretend we are starting on the first of the month
    month_start = schedule_.started.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    schedule_.started = month_start - relativedelta(days=1)
    schedule_.trigger_dags()
    assert models.DagRun.objects.count() == 1
    run = models.DagRun.objects.first()
    assert run.created == month_start

    # nothing to trigger when run again
    schedule_.trigger_dags()
    assert models.DagRun.objects.count() == 1

    # second dag run - move the previous run into the past so it makes a new one
    run.created -= relativedelta(months=1)
    run.save()
    schedule_.trigger_dags()
    assert models.DagRun.objects.count() == 2
    run = models.DagRun.objects.order_by("-created").first()
    assert run.created == month_start


@pytest.mark.django_db
def test_trigger_tasks(schedule_):
    # missing DAG is marked as failed
    dag_run2 = models.DagRun.objects.create(dag="no_such_dag", creator="manual")
    schedule_.trigger_tasks()
    dag_run2.refresh_from_db()
    assert dag_run2.status == models.DagStatus.FAILED

    # trigger task 1
    dag_run = models.DagRun.objects.create(dag="dag1", creator="manual")
    schedule_.trigger_tasks()
    assert models.TaskRun.objects.count() == 1
    task_run = models.TaskRun.objects.get(task="1", attempt=1)
    assert task_run.status == models.TaskStatus.WAITING

    # DAG failed
    task_run.status = models.TaskStatus.FAILED
    task_run.save()
    schedule_.trigger_tasks()
    dag_run.refresh_from_db()
    assert dag_run.status == models.DagStatus.FAILED

    # trigger task 2
    task_run.status = models.TaskStatus.SUCCEEDED
    task_run.save()
    dag_run.status = models.DagStatus.RUNNING
    dag_run.save()
    schedule_.trigger_tasks()
    assert models.TaskRun.objects.count() == 2
    task_run = models.TaskRun.objects.get(task="2", attempt=1)
    assert task_run.status == models.TaskStatus.WAITING

    # DAG succeeded
    task_run.status = models.TaskStatus.SUCCEEDED
    task_run.save()
    schedule_.trigger_tasks()
    dag_run.refresh_from_db()
    assert dag_run.status == models.DagStatus.SUCCEEDED

    # test str functions
    str(dag_run)
    str(task_run)


def test_run_scheduler(mocker, schedule_):
    mock_sleep = mocker.patch("time.sleep", autospec=True)
    mocker.patch.object(managers, "try_advisory_lock", side_effect=[False, True], autospec=True)
    mocker.patch.object(schedule_, "trigger_dags", autospec=True)
    mocker.patch.object(schedule_, "trigger_tasks", autospec=True)
    mocker.patch.object(schedule_, "start_tasks", autospec=True)
    mocker.patch.object(schedule_, "update_tasks", autospec=True)

    # say finished on second loop
    schedule_.task_manager.shutdown.side_effect = iter([False, True])

    # replace signal handlers
    schedule_.handle_signals()
    int_handler = signal.getsignal(signal.SIGINT)
    term_handler = signal.getsignal(signal.SIGTERM)

    # call the signals on sleep
    handler_iter = iter([int_handler, int_handler, term_handler])
    mock_sleep.side_effect = lambda _: next(handler_iter)()

    try:
        schedule_.run()  # running -> shutdown -> shutdown
        schedule_.run()  # running -> terminate
    finally:
        # restore the default handlers
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

    assert mock_sleep.call_count == 3
    assert schedule_.trigger_dags.call_count == 1
    assert schedule_.trigger_tasks.call_count == 1
    assert schedule_.start_tasks.call_count == 2
    assert schedule_.update_tasks.call_count == 5


@pytest.mark.django_db
def test_start_tasks(schedule_):
    dag_run = models.DagRun.objects.create(dag="dag1", creator="manual")
    models.TaskRun.objects.create(dag_run=dag_run, task="1", status=models.TaskStatus.FAILED)
    task_run = models.TaskRun.objects.create(
        dag_run=dag_run, task="2", status=models.TaskStatus.WAITING
    )
    schedule_.task_manager.slots = 1

    schedule_.start_tasks()

    assert schedule_.task_manager.start_task.call_args[0][0] == task_run


@pytest.mark.django_db
def test_update_tasks(schedule_):
    dag_run = models.DagRun.objects.create(dag="dag1", creator="manual")
    models.TaskRun.objects.create(dag_run=dag_run, task="1", status=models.TaskStatus.FAILED)
    task_run = models.TaskRun.objects.create(
        dag_run=dag_run, task="1", status=models.TaskStatus.RUNNING, attempt=2
    )
    schedule_.task_manager.update_tasks.return_value = [task_run]

    schedule_.update_tasks()

    assert list(schedule_.task_manager.update_tasks.call_args[0][0]) == [task_run]
