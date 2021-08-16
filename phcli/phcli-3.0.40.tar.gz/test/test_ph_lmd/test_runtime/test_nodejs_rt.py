import os
import pytest
from phcli.ph_lmd.runtime.nodejs_rt import NodejsRT


nodejs_rt = NodejsRT()


@pytest.mark.skip("lib_path not exists")
def test_nodejs_rt_pkg_layer_libpath():
    args = {
        "lib_path": "node_modules",
        "package_name": "test_nodejs_rt_pkg_layer_libpath.zip"
    }

    nodejs_rt.pkg_layer(args)
    assert os.path.exists(args["package_name"])
    os.remove(args["package_name"])


@pytest.mark.skip("code_path not exists")
def test_nodejs_rt_pkg_code():
    package_name = "test_nodejs_rt_pkg_code.zip"
    args = {
        "code_path": "dist/,config/,app.js",
        "package_name": package_name,
    }
    nodejs_rt.pkg_code(args)
    assert os.path.exists(package_name)
    os.remove(package_name)
