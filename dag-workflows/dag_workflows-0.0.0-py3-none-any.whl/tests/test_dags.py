import pytest

from workflows import bases, dags


def test_dag_failure(caplog):
    # try to register a directory that does not contain a workflow.yaml file
    dags.register_directory("workflows")
    assert "No workflow.yaml file found" in caplog.text


def test_task_invalid_file():
    with pytest.raises(bases.RegistrationError, match="Unsupported file type"):
        dags.register_task(None, "file.txt")


def test_task_sql_header(tmp_path):
    sql_file = tmp_path / "test.sql"
    sql_file.write_text("SELECT * FROM foo")
    with pytest.raises(bases.RegistrationError, match="Cannot find a YAML spec"):
        dags.register_task(None, str(sql_file))


def test_task_no_type(tmp_path):
    sql_file = tmp_path / "test.sql"
    sql_file.write_text("/*description: blah*/SELECT * FROM foo")
    with pytest.raises(bases.RegistrationError, match="`type` is a required field"):
        dags.register_task(None, str(sql_file))


def test_task_bad_type(tmp_path):
    sql_file = tmp_path / "test.sql"
    sql_file.write_text("/*type: blah*/SELECT * FROM foo")
    with pytest.raises(AssertionError, match='Type "Blah" not found'):
        dags.register_task(None, str(sql_file))


def test_task_yaml(tmp_path):
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("type: no_op\n")
    with pytest.raises(TypeError, match="missing 2 required"):
        dags.register_task(None, str(yaml_file))
