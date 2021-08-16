import os
from phcli.ph_lmd.runtime.python_rt import PythonRT


go_rt = PythonRT()


def test_go_rt_pkg_layer_pipenv():
    args = {
        "package_name": "test_go_rt_layer_pipenv.zip",
        "is_pipenv": True,
    }

    go_rt.pkg_layer(args)
    assert os.path.exists(args["package_name"])
    os.remove(args["package_name"])


def test_go_rt_pkg_layer_libpath():
    args = {
        "lib_path": "/Users/clock/workSpace/Python/aws_lambda_deploy/.venv/lib/go3.8/site-packages/",
        "package_name": "test_go_rt_layer_libpath.zip"
    }

    go_rt.pkg_layer(args)
    assert os.path.exists(args["package_name"])
    os.remove(args["package_name"])


def test_go_rt_pkg_code():
    args = {
        "code_path": "aws_lambda_deploy",
        "package_name": "test_go_rt_pkg_code.zip"
    }
    package_name = "test_go_rt_pkg_code.zip"
    go_rt.pkg_code(args)
    assert os.path.exists(package_name)
    os.remove(package_name)
