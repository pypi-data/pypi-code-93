import os
import sys
import tempfile

import koalak
import pytest
from koalak.utils import temp_pathname, tmp_module


def test_simple():
    plugins = koalak.mkpluginmanager("plugin")

    @plugins.mkbaseplugin
    class BasePlugin:
        pass

    class SimplePlugin(BasePlugin):
        name = "simple"

    assert plugins["simple"] == SimplePlugin
    assert list(plugins) == [SimplePlugin]


def test_two_plugins():
    plugins = koalak.mkpluginmanager("plugin")

    @plugins.mkbaseplugin
    class BasePlugin:
        pass

    class OnePlugin(BasePlugin):
        name = "one"

    class TwoPlugin(BasePlugin):
        name = "two"

    assert plugins["one"] == OnePlugin
    assert plugins["two"] == TwoPlugin
    assert list(plugins) == [OnePlugin, TwoPlugin]


def test_with_framework():
    framework = koalak.mkframework()
    plugins = framework.mkpluginmanager("tools")

    @plugins.mkbaseplugin
    class BasePlugin:
        pass

    class SimplePlugin(BasePlugin):
        name = "simple"

    assert plugins["simple"] == SimplePlugin
    assert list(plugins) == [SimplePlugin]


@pytest.mark.skip
def test_error_abstract_method():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("test")
    class BaseTest:
        @framework.abstract
        def x(self):
            pass

    class XTest(BaseTest):
        name = "x"

        def x(self):
            pass

    with pytest.raises(TypeError):

        class YTest(BaseTest):
            name = "y"


@pytest.mark.skip
def test_abstract_subplugin():
    framework = koalak.mkframework()

    @framework.mkpluginmanager("test")
    class XPlugin:
        name = "x"

        @framework.abstract
        def abstract_func(self):
            pass

    class AbstractPlugin(XPlugin):
        koala = framework.abstract()
        name = "y"

    class NonAbstractPlugin(AbstractPlugin):
        name = "z"

        def abstract_func(self):
            pass


def test_load_plugins():
    # TODO: Test with existing directory and without
    with tempfile.TemporaryDirectory() as plugin_path:
        plugins = koalak.mkpluginmanager(homepath=plugin_path)

        @plugins.mkbaseplugin
        class BasePlugin:
            pass

        class APlugin:
            name = "A"

        # Temporally create a module so it can be importable by the plugin
        with tmp_module(context={"BasePlugin": BasePlugin}) as module:
            name_module = module.__name__
            print(name_module, name_module in sys.modules)
            data_file = f"""from {name_module} import BasePlugin
class BPlugin(BasePlugin):
    name = 'B'
    """
            with open(os.path.join(plugin_path, "plugin.py"), "w") as f:
                print("in path", os.path.join(plugin_path, "plugin.py"))
                print("data_file", data_file)
                f.write(data_file)

            # Init folder and plugins
            plugins.init()
            assert plugins["B"].name == "B"  # Just check that "B" is loaded in plugnis


def test_init_without_homepath():
    plugins = koalak.mkpluginmanager()
    with pytest.raises(TypeError):
        plugins.init()  # No error should be raised


@pytest.mark.skip(reason="tmp_pathname not implemented yet")
def test_double_init():
    with temp_pathname() as pathname:
        plugins = koalak.mkpluginmanager(homepath=pathname)
        plugins.init()
        with pytest.raises(TypeError):
            plugins.init()


@pytest.mark.skip(reason="tmp_pathname not implemented yet")
def test_init_with_homepath():
    with temp_pathname() as pathname:
        plugins = koalak.mkpluginmanager(homepath=pathname)
        plugins.init()
        assert os.path.isdir(plugins.homepath)


def test_constraint_attr():
    plugins = koalak.mkpluginmanager()

    @plugins.mkbaseplugin
    class BasePlugin:
        help = plugins.attr()

    class APlugin(BasePlugin):
        name = "A"
        help = "Something"

    with pytest.raises(TypeError):
        # Must define help
        class BPlugin(BasePlugin):
            name = "B"


def test_constraint_attr_type():
    plugins = koalak.mkpluginmanager()

    @plugins.mkbaseplugin
    class BasePlugin:
        help = plugins.attr(type=str)

    class APlugin(BasePlugin):
        name = "A"
        help = "Something"

    with pytest.raises(TypeError):
        # Help must be a string
        class BPlugin(BasePlugin):
            name = "B"
            help = 5


def test_constraint_attr_inheritable_true():
    plugins = koalak.mkpluginmanager()

    @plugins.mkbaseplugin
    class BasePlugin:
        x = plugins.attr()  # By default inheritable is True

    class APlugin(BasePlugin):
        name = "A"
        x = 1

    class BPlugin(APlugin):
        name = "B"


def test_constraint_attr_inheritable_false():
    plugins = koalak.mkpluginmanager()

    @plugins.mkbaseplugin
    class BasePlugin:
        x = plugins.attr(inheritable=False)

    class APlugin(BasePlugin):
        name = "A"
        x = 1

    with pytest.raises(TypeError):

        class BPlugin(APlugin):
            name = "B"


def test__repr__and__str__():
    pm = koalak.mkpluginmanager()
    assert repr(pm) == str(pm) == "<PluginManager>"

    pm = koalak.mkpluginmanager("tools")
    assert repr(pm) == str(pm) == "<PluginManager [tools]>"
