import pytest

from workflows import bases, tasks


def test_registry_update():
    registry = bases.DagRegistry()
    registry["dag1"] = bases.DAG("description", "directory/dag1")
    assert str(registry["dag1"]) == "DAG(dag1)"
    assert str(registry) == "DagRegistry([dag1])"
    with pytest.raises(RuntimeError, match="Cannot overwrite"):
        registry["dag1"] = bases.DAG("name", "some/directory")
    with pytest.raises(RuntimeError, match="Cannot overwrite"):
        registry.update(registry)

    registry.update(bases.DagRegistry())


def test_registry_exceptions():
    registry = bases.DagRegistry()
    registry["dag1"] = AssertionError("thing failed")
    with pytest.raises(bases.RegistrationError):
        _ = registry["dag1"]


def test_registry_validate():
    registry = bases.DagRegistry()
    registry["good_dag"] = dag = bases.DAG("name", "some/name")
    tasks.NoOp("description", dag, "task1", ["other_dag:task2"], [])
    assert registry.validate() is False, "Missing DAG"

    registry["other_dag"] = dag = bases.DAG("name", "some/directory")
    assert registry.validate() is False, "Missing a task"

    task = tasks.NoOp("description", dag, "task2", [], [])
    assert str(task) == "NoOp(directory:task2)"
    assert registry.validate() is True, "Should be valid"

    registry._dags["other_dag"] = Exception("failed to load")
    assert registry.validate() is False, "DAG failed to load"


def test_registry_hooks(mocker, caplog):
    registry = bases.DagRegistry()
    call_args = []

    def hook1(event, **kwargs):
        call_args.append((event, kwargs))

    registry.register_hook(hook1)

    def hook2(event, **kwargs):
        call_args.append((event, kwargs))
        raise RuntimeError()

    registry.register_hook(hook2)

    registry.call_hooks(
        bases.Event.TASK_FINISH,
        task=mocker.sentinel.Task,
        exception=mocker.sentinel.Exc,
    )

    assert call_args[0][0] == bases.Event.TASK_FINISH
    assert call_args[0][1] == dict(
        dag=None,
        task=mocker.sentinel.Task,
        dag_run=None,
        task_run=None,
        exception=mocker.sentinel.Exc,
    )
    assert "Event hook hook2 failed on Event.TASK_FINISH" in caplog.text
