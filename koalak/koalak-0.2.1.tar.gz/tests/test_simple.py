import koalak
import pytest
from koalak import exceptions


def nothing(**args):
    pass


def test_framework():
    # FIXME: I don't like this test
    name = koalak.get_unique_framework_name()
    framework = koalak.mkframework(name)
    assert koalak.get_framework(name) is framework


@pytest.mark.skip
def test_plugin():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("test")
    class BaseTest:
        pass

    assert framework.get_plugins("test") == []
    pm_test = framework.get_plugin_manager("test")
    assert pm_test.get_plugins() == []


@pytest.mark.skip
def test_sub_plugin():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("collector")
    class BaseCollector:
        pass

    class SimpleCollector(BaseCollector):
        name = "simple"

    assert framework.get_plugin("collector", "simple") is SimpleCollector
    pm_collector = framework.get_plugin_manager("collector")
    assert pm_collector.get_plugin("simple") is SimpleCollector

    assert pm_collector.get_plugins() == [SimpleCollector]


@pytest.mark.skip
def test_two_plugin_managers():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("collector")
    class BaseCollector:
        pass

    class XCollector(BaseCollector):
        name = "x"

    class YCollector(BaseCollector):
        name = "y"

    @framework.mkpluginmanager("installer")
    class BaseInstaller:
        pass

    class XInstaller(BaseInstaller):
        name = "x"

    class YInstaller(BaseInstaller):
        name = "y"

    assert framework.get_plugins("collector") == [XCollector, YCollector]
    assert framework.get_plugins("installer") == [XInstaller, YInstaller]

    assert framework.get_plugin("collector", "x") is XCollector
    assert framework.get_plugin("collector", "y") is YCollector
    assert framework.get_plugin("installer", "x") is XInstaller
    assert framework.get_plugin("installer", "y") is YInstaller

    pm_collector = framework.get_plugin_manager("collector")
    assert pm_collector.get_plugin("x") is XCollector
    assert pm_collector.get_plugin("y") is YCollector

    pm_installer = framework.get_plugin_manager("installer")
    assert pm_installer.get_plugin("x") is XInstaller
    assert pm_installer.get_plugin("y") is YInstaller


def test_error_framework_already_exist():
    framework_name = koalak.get_unique_framework_name()
    framework1 = koalak.mkframework(framework_name)  # noqa: F841

    with pytest.raises(exceptions.FrameworkAlreadyExistException):
        framework2 = koalak.mkframework(framework_name)  # noqa: F841


@pytest.mark.skip
def test_error_plugin_manager_already_exist():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("a")
    class A:
        pass

    with pytest.raises(exceptions.PluginManagerAlreadyExistException):

        @framework.mkpluginmanager("a")
        class B:
            pass


@pytest.mark.skip
def test_error_plugin_alread_exist():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("plugin")
    class BasePlugin:
        pass

    class APlugin(BasePlugin):
        name = "a"

    with pytest.raises(exceptions.PluginAlreadyExistException):

        class AagainPlugin(BasePlugin):
            name = "a"


@pytest.mark.skip
def test_get_frameworks():
    framework1 = koalak.mkframework()
    framework2 = koalak.mkframework()

    frameworks = koalak.get_frameworks()
    assert framework1 in frameworks
    assert framework2 in frameworks
