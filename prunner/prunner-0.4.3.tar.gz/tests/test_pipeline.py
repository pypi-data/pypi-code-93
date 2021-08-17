import os

import pytest
from prunner.tasks import (
    TaskStrategy,
    LoadVariablesTask,
    SetVariablesTask,
    GenerateFileTask,
    FunctionTask,
    ParamsNotDefined,
)
from prunner.loaders import SectionNotDefined

CONFIG_DIR = "example"


@pytest.fixture
def env():
    return {
        "FOO": "bar",
        "USER": "Jack",
        "HOME": "/home/jack/",
        "PRUNNER_CONFIG_DIR": CONFIG_DIR,
        "DRYRUN": True,
    }


@pytest.fixture
def load_variables(env):
    return LoadVariablesTask.from_settings(env)


@pytest.fixture
def generate_file(env):
    return GenerateFileTask.from_settings(env)


@pytest.fixture
def set_variables():
    return SetVariablesTask()


@pytest.fixture
def functions(env):
    return FunctionTask.from_settings(env)


def test_executor_load_variables(env, load_variables):
    results = load_variables.execute("simple", env)
    assert 0 < len(results)


def test_executor_load_variables_has_expansion(env, load_variables):
    raw_input = "$HOME/users/$USER"
    loaded_variables = load_variables.execute("simple", env)
    actual = loaded_variables["complex_substitution"]
    assert raw_input != actual


def test_executor_load_variables_bad_argument(env, load_variables):
    with pytest.raises(TypeError):
        load_variables.execute(None, env)


def test_executor_load_variables_nonexistent_set_throws_error(env, load_variables):
    with pytest.raises(SectionNotDefined):
        load_variables.execute("not exist", env)


def test_generate_file_receives_str_param(env, generate_file):
    with pytest.raises(TypeError):
        generate_file.execute("template = nope.jinja", env)


def test_saving_generated_file(env, generate_file):
    result = generate_file.execute(
        {
            "template": "pbs_head.jinja2",
            "filepath": "delete_me.sh",
            "variable": "script_path",
        },
        env,
    )
    expected_excerpt = (
        "#PBS -S /bin/bash\n#PBS -l nodes=1:ppn=1,walltime=4:00:00,mem=4gb\n"
    )

    filepath = result["script_path"]
    assert os.path.exists(filepath)

    with open(filepath, "r") as fd:
        actual_content = fd.read()

    assert expected_excerpt in actual_content

    # clean up generated file
    os.remove(filepath)
    assert not os.path.exists(filepath)


def test_call_function(env, functions):
    env["SUBJECT"] = "proj:x:y:z"
    expected = {
        "PROJECT": "proj",
        "SUBJECT_ID": "x",
        "SUBJECT_CLASSIFIER": "y",
        "SUBJECT_EXTRA": "z",
        "SESSION": "x_y",
    }
    actual = functions.execute("split_subject", env)
    assert expected == actual


def test_function_receives_non_str_param(env, functions):
    with pytest.raises(TypeError):
        functions.execute({}, env)


def test_function_missing_param(env, functions):
    with pytest.raises(ParamsNotDefined):
        functions.execute("split_subject", {})


def test_calling_function_throws_error(env, functions):
    env["SUBJECT"] = "missing_stuff:x"
    with pytest.raises(ValueError):
        functions.execute("split_subject", env)


def test_set_variables(env, set_variables):
    value = "New User Account"
    result = set_variables.execute({"USER": value}, env)
    assert result["USER"] == value


def test_set_variables_receives_param_of_wrong_type(env, set_variables):
    with pytest.raises(TypeError):
        set_variables.execute([], env)

    with pytest.raises(TypeError):
        set_variables.execute(" Fail me ", env)
