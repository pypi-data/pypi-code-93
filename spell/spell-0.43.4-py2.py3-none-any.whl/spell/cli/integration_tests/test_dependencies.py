from collections import namedtuple
from pip_chill.pip_chill import Distribution
import pytest
import yaml

from spell.shared import dependencies
from spell.shared.dependencies import (
    NoVirtualEnvFound,
    PipDependencies,
    CondaDependencies,
    InvalidDependencyConfig,
    merge_dependencies,
)


def test_pip_deps_no_env(mocker):
    mocker.patch.object(dependencies, "in_virtualenv", new=lambda: False)
    with pytest.raises(NoVirtualEnvFound):
        PipDependencies.from_env()


def test_pip_deps_from_env(mocker):
    mocker.patch.object(dependencies, "in_virtualenv", new=lambda: True)
    mock_requirements = [
        Distribution("tensorflow"),
        Distribution("spell"),
        Distribution("beautifulsoup4", version="0.1.2"),
    ]
    mocker.patch.object(dependencies, "chill", new=lambda no_chill: (mock_requirements, []))
    deps = PipDependencies.from_env()
    assert len(deps.deps) == 1
    assert deps.deps[0].line == "beautifulsoup4==0.1.2"


def test_pip_deps_from_requirements_file(mocker):
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    req_file = "\n".join(req_deps)
    m = mocker.mock_open(read_data=req_file)
    mocker.patch("builtins.open", m)
    deps = PipDependencies.from_requirements_file("/some/path")
    assert [d.line for d in deps.deps] == req_deps[1:]


def test_pip_deps_from_requirements_file_invalid_spec(mocker):
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4", "~~invalid!=dep"]
    req_file = "\n".join(req_deps)
    m = mocker.mock_open(read_data=req_file)
    mocker.patch("builtins.open", m)
    with pytest.raises(InvalidDependencyConfig) as e:
        PipDependencies.from_requirements_file("/some/path")
        assert e.message == "Could not parse requirement ~~invalid!=dep"


def test_pip_reqs_from_strings():
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    deps = PipDependencies.from_strings(req_deps)
    assert [d.line for d in deps.deps] == req_deps
    assert len(deps.overridden_framework_packages) == 1
    assert deps.overridden_framework_packages[0].line == req_deps[0]


def test_pip_reqs_from_strings_invalid_spec():
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4", "~~invalid!=dep"]
    with pytest.raises(InvalidDependencyConfig) as e:
        PipDependencies.from_strings(req_deps)
        assert e.message == "Could not parse requirement ~~invalid!=dep"


def test_pip_deps_update():
    req_deps1 = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    req_deps2 = ["tensorflow==1.2.3", "pytorch>2.0", "bar>=1.2.3", "click"]
    deps1 = PipDependencies.from_strings(req_deps1)
    deps2 = PipDependencies.from_strings(req_deps2)
    deps1.update(deps2)
    expected_deps = {
        "pytorch>2.0",
        "foo",
        "bar>=1.2.3",
        "tensorflow==1.2.3",
        "click",
    }
    assert {d.line for d in deps1.deps} == expected_deps
    assert {d.line for d in deps1.overridden_framework_packages} == {
        "pytorch>2.0",
        "tensorflow==1.2.3",
    }


MockProcessReturn = namedtuple("MockProcessReturn", "returncode stdout")


def test_conda_deps_from_env(mocker):
    conda = """
name: my-env
prefix: /some/tmp/here
dependencies:
  - foo
  - bar
"""
    mock_return = MockProcessReturn(0, conda)
    mocker.patch("subprocess.run", new=lambda cmd, stdout: mock_return)
    deps = CondaDependencies.from_env()
    assert deps.environment == {"dependencies": ["foo", "bar"]}


def test_conda_deps_bad_return_code(mocker):
    conda = """
name: my-env
prefix: /some/tmp/here
dependencies:
  - foo
  - bar
"""
    mock_return = MockProcessReturn(1, conda)
    mocker.patch("subprocess.run", new=lambda cmd, stdout: mock_return)
    with pytest.raises(InvalidDependencyConfig):
        CondaDependencies.from_env()


def test_conda_deps_from_env_bad_yaml(mocker):
    mock_return = MockProcessReturn(0, "foo:\nbar")
    mocker.patch("subprocess.run", new=lambda cmd, stdout: mock_return)
    with pytest.raises(InvalidDependencyConfig):
        CondaDependencies.from_env()


def test_conda_deps_from_file(mocker):
    conda = """
name: my-env
prefix: /some/tmp/here
dependencies:
  - foo
  - bar
"""
    m = mocker.mock_open(read_data=conda)
    mocker.patch("builtins.open", m)
    deps = CondaDependencies.from_file("/some/path")
    assert deps.environment == yaml.safe_load(conda)


def test_conda_deps_from_file_invalid_yaml(mocker):
    conda = """
dependencies:
  - foo
  - bar
oops
"""
    m = mocker.mock_open(read_data=conda)
    mocker.patch("builtins.open", m)
    with pytest.raises(InvalidDependencyConfig):
        CondaDependencies.from_file("/some/path")


def test_merge_deps_only_pip_env_deps():
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    deps = PipDependencies.from_strings(req_deps)
    new_deps = merge_dependencies(deps, None, None, [])
    assert new_deps is deps


def test_merge_deps_only_conda_env_deps(mocker):
    conda = """
name: my-env
prefix: /some/tmp/here
dependencies:
  - foo
  - bar
"""
    m = mocker.mock_open(read_data=conda)
    mocker.patch("builtins.open", m)
    deps = CondaDependencies.from_file("/some/path")
    new_deps = merge_dependencies(deps, None, None, [])
    assert new_deps is deps


def test_merge_deps_only_conda_file(mocker):
    conda = """
name: my-env
prefix: /some/tmp/here
dependencies:
  - foo
  - bar
"""
    m = mocker.mock_open(read_data=conda)
    mocker.patch("builtins.open", m)
    deps = merge_dependencies(None, "/some/path/environment.yml", None, [])
    assert deps.environment == yaml.safe_load(conda)


def test_merge_deps_only_req_file(mocker):
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    req_file = "\n".join(req_deps)
    m = mocker.mock_open(read_data=req_file)
    mocker.patch("builtins.open", m)
    deps = merge_dependencies(None, None, "/something/requirements.txt", [])
    assert [d.line for d in deps.deps] == req_deps[1:]


def test_merge_deps_only_pip():
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    deps = merge_dependencies(None, None, None, req_deps)
    assert [d.line for d in deps.deps] == req_deps


def test_merge_deps_pip_env_and_conda_file(mocker):
    req_deps = ["pytorch==1.2.3", "foo", "bar>=1.5.4"]
    deps = PipDependencies.from_strings(req_deps)
    conda = """
name: my-env
prefix: /some/tmp/here
dependencies:
  - foo
  - bar
"""
    m = mocker.mock_open(read_data=conda)
    mocker.patch("builtins.open", m)
    with pytest.raises(InvalidDependencyConfig):
        merge_dependencies(deps, "/path/to/env.yml", None, [])


def test_merge_deps_conda_env_and_conda_file(mocker):
    conda1_lines = [
        "name: my-env",
        "prefix: /some/tmp/here",
        "dependencies:",
        "  - foo1",
        "  - bar1",
    ]
    conda2_lines = [
        "name: my-env",
        "prefix: /some/tmp/here",
        "dependencies:",
        "  - foo2",
        "  - bar2",
    ]

    m = mocker.mock_open(read_data="\n".join(conda1_lines))
    mocker.patch("builtins.open", m)
    deps = CondaDependencies.from_file("/some/path")
    m = mocker.mock_open(read_data="\n".join(conda2_lines))
    mocker.patch("builtins.open", m)
    with pytest.raises(InvalidDependencyConfig):
        merge_dependencies(deps, "env.yml", None, [])
