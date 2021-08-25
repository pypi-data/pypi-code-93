import inspect
import pytest
import collections
from os import path
from time import strftime
from _pytest.config import Config
from _pytest.fixtures import fixture
from _pytest.pathlib import import_path
from autotest import webdriver


def logging_settings(config):
    log_format = "%(asctime)s %(levelname)-8s %(filename)s::%(module)s::%(funcName)s %(lineno)4d: %(message)s"
    log_date_format = "%Y-%m-%d %H:%M:%S"
    settings = {
        "log_format": log_format,
        "log_date_format": log_date_format,
        "log_file_format": log_format,
        "log_file_date_format": log_date_format
    }
    config.inicfg.update(collections.ChainMap(config.inicfg, settings))
    log_file = config.getini("log_file")
    if log_file:
        log_file = path.normpath(log_file)
        root, ext = path.splitext(log_file)
        logs_path = path.join(
            log_file,
            f"{strftime('%Y-%m-%d-%H%M%S')}.log") if ext == "" else log_file
        config.inicfg.update({"log_file": logs_path})


def get_class(pypath):
    pyfile = path.join(pypath, "custom.py")
    if not path.isfile(pyfile):
        return webdriver.Remote
    pymodule = import_path(pyfile)
    pyclasses = [
        pyclass for name, pyclass in inspect.getmembers(
            pymodule, lambda x: inspect.isclass(x) and x.__base__ == webdriver.
            Remote.__base__)
    ]
    pyclasses.insert(0, webdriver.Remote)
    return type("Remote", tuple(pyclasses), {})


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: Config):
    logging_settings(config)


@fixture(scope="session")
def device(pytestconfig, request):
    Remote = get_class(pytestconfig.rootpath)
    desired_caps = dict(platformName='Android', deviceName='Android Emulator')
    device = Remote('http://localhost:4723/wd/hub', desired_caps)
    yield device
    request.addfinalizer(lambda: device.quit())
