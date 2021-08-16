import os

import koalak
import pytest
from koalak.utils import temp_pathname


def test_simple():
    """Test framework can be created"""
    framework = koalak.mkframework()


# @pytest.mark.skip(reason="tmp_pathname not implemented")
def test_double_init():
    """If we call init twice raise Error"""
    with temp_pathname() as pathname:
        framework = koalak.mkframework(homepath=pathname)
        framework.init()
        with pytest.raises(TypeError):
            framework.init()


# @pytest.mark.skip(reason="tmp_pathname not implemented")
def test_homepath_alone():
    """Homepath is created after init"""
    with temp_pathname() as pathname:
        framework = koalak.mkframework(homepath=pathname)
        assert not os.path.exists(pathname)
        framework.init()
        assert os.path.isdir(pathname)


def test__repr__and__str__():
    framework = koalak.mkframework()
    assert repr(framework) == str(framework) == "<Framework>"

    framework = koalak.mkframework("wordlistools")
    assert repr(framework) == str(framework) == "<Framework [wordlistools]>"


# @pytest.mark.skip(reason="tmp_pathname not implemented")
def test_homepath_plugins_alone():
    """Test that folder plugins is created"""
    with temp_pathname() as pathname:
        framework = koalak.mkframework(homepath=pathname)
        plugins = framework.mkpluginmanager()
        assert not os.path.exists(pathname)
        framework.init()
        assert os.path.isdir(pathname)
        assert os.path.isdir(os.path.join(pathname, "plugins"))


# @pytest.mark.skip(reason="tmp_pathname not implemented")
def test_homepath_plugins_with_homepath():
    """Test that we can chose the folder name of plugins"""
    with temp_pathname() as pathname:
        framework = koalak.mkframework(homepath=pathname)
        plugins = framework.mkpluginmanager(homepath="tools")
        assert not os.path.exists(pathname)
        framework.init()
        assert os.path.isdir(pathname)
        assert not os.path.isdir(os.path.join(pathname, "plugins"))
        assert os.path.isdir(os.path.join(pathname, "tools"))
