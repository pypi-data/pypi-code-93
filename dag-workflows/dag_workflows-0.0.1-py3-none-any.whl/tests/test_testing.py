def test_execute_sql(workflows):
    assert workflows.execute_sql("SELECT 1") == [(1,)]
    assert workflows.execute_sql("CREATE TABLE blah (name text)") is None


def test_execute_dag(workflows, mocker):
    mock_execute = mocker.patch("workflows.executor.execute_dag", autospec=True)
    workflows.execute_dag(mocker.sentinel.DAG)
    mock_execute.assert_called_once_with(mocker.sentinel.DAG, None, None)
