import networkx
import pytest

from workflows import bases, executor


@pytest.mark.parametrize(
    "start, stop, expected",
    [
        (None, None, {"1", "2", "3"}),
        ("1", None, {"1", "3"}),
        (None, "3", {"1", "2", "3"}),
        ("3", "3", {"3"}),
    ],
)
def test_get_subgraph(start, stop, expected):
    graph = networkx.DiGraph([("1", "3"), ("2", "3")])
    for x in ["1", "2", "3"]:
        graph.nodes[x]["task"] = x
    tasks = executor.get_sorted_tasks(graph, start, stop)
    assert set(tasks) == expected


def test_execute_dag(mocker):
    dag = bases.DAG("test", "xyz", registry=mocker.Mock())
    task1 = mocker.Mock(all_parameters=["PARAMETER"])
    task2 = mocker.Mock(all_parameters=["PARAMETER"])
    task2.execute.side_effect = RuntimeError("task2 fails")
    dag.graph.add_node("1", task=task1)
    dag.graph.add_node("2", task=task2)
    dag.graph.add_edge("1", "2")
    mocker.patch.dict("os.environ", {"PARAMETER": "ROUGE"})

    with pytest.raises(RuntimeError, match="task2 fails"):
        executor.execute_dag(dag)

    assert task1.execute.call_count == 1
    assert task1.execute.call_args[0][0] == {"PARAMETER": "ROUGE"}
    assert dag.registry.call_hooks.call_args_list == [
        mocker.call(bases.Event.TASK_START, task=task1),
        mocker.call(bases.Event.TASK_FINISH, task=task1),
        mocker.call(bases.Event.TASK_START, task=task2),
        mocker.call(bases.Event.TASK_FINISH, task=task2, exception=task2.execute.side_effect),
    ]
