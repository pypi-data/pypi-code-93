import os
import pytest
from phcli.ph_lmd.runtime.python_rt import PythonRT


python_rt = PythonRT()


@pytest.mark.skip("Pipenv is slow for the first time")
def test_python_rt_pkg_layer_pipenv():
    args = {
        "package_name": "test_python_rt_layer_pipenv.zip",
        "is_pipenv": True,
    }

    python_rt.pkg_layer(args)
    assert os.path.exists(args["package_name"])
    os.remove(args["package_name"])


def test_python_rt_pkg_layer_libpath():
    args = {
        "lib_path": ".venv/lib/python3.8/site-packages/",
        "package_name": "test_python_rt_layer_libpath.zip"
    }

    python_rt.pkg_layer(args)
    assert os.path.exists(args["package_name"])
    os.remove(args["package_name"])


def test_python_rt_pkg_code():
    args = {
        "code_path": "./phlmd",
        "package_name": "test_python_rt_pkg_code.zip"
    }
    package_name = "test_python_rt_pkg_code.zip"
    python_rt.pkg_code(args)
    assert os.path.exists(package_name)
    os.remove(package_name)
