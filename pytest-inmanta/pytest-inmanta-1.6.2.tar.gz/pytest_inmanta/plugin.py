"""
    Copyright 2019 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import glob
import importlib
import json
import logging
import math
import os
import shutil
import sys
import tempfile
import typing
import warnings
from collections import defaultdict
from distutils import dir_util
from pathlib import Path
from textwrap import dedent
from types import FunctionType, ModuleType

import pytest
import yaml
from pytest import CaptureFixture
from tornado import ioloop

import inmanta.ast
from inmanta import compiler, config, const, module, protocol
from inmanta.agent import cache, handler
from inmanta.agent import io as agent_io
from inmanta.agent.handler import HandlerContext, ResourceHandler
from inmanta.data import LogLine
from inmanta.data.model import AttributeStateChange, ResourceIdStr
from inmanta.execute.proxy import DynamicProxy
from inmanta.export import Exporter, ResourceDict, cfg_env
from inmanta.protocol import json_encode
from inmanta.resources import Resource

if typing.TYPE_CHECKING:
    from inmanta.agent.io.local import IOBase

from .handler import DATA

CURDIR = os.getcwd()
LOGGER = logging.getLogger()


option_to_env = {
    "inm_venv": "INMANTA_TEST_ENV",
    "inm_module_repo": "INMANTA_MODULE_REPO",
    "inm_install_mode": "INMANTA_INSTALL_MODE",
    "inm_no_load_plugins": "INMANTA_TEST_NO_LOAD_PLUGINS",
}


def pytest_addoption(parser) -> None:
    group = parser.getgroup("inmanta", "inmanta module testing plugin")
    group.addoption(
        "--venv",
        dest="inm_venv",
        help="folder in which to place the virtual env for tests (will be shared by all tests), overrides INMANTA_TEST_ENV. "
        "This options depends on symlink support. This does not work on all windows versions. "
        "On windows 10 you need to run pytest in an admin shell. "
        "Using a fixed virtual environment can speed up running the tests.",
    )
    group.addoption(
        "--use-module-in-place",
        action="store_true",
        help="tell pytest-inmanta to run with the module in place, useful for debugging. "
        "Makes inmanta add the parent directory of your module directory to it's directory path, instead of copying your "
        "module to a temporary libs directory. "
        "It allows testing the current module against specific versions of dependent modules. "
        "Using this option can speed up the tests, because the module dependencies are not downloaded multiple times.",
    )
    group.addoption(
        "--module_repo",
        dest="inm_module_repo",
        action="append",
        help="location to download modules from, overrides INMANTA_MODULE_REPO."
        "Can be specified multiple times to add multiple locations",
    )
    group.addoption(
        "--install_mode",
        dest="inm_install_mode",
        help="Install mode for modules downloaded during this test, overrides INMANTA_INSTALL_MODE.",
        choices=module.INSTALL_OPTS,
    )
    group.addoption(
        "--no_load_plugins",
        action="store_true",
        dest="inm_no_load_plugins",
        help="Don't load plugins in the Project class. Overrides INMANTA_TEST_NO_LOAD_PLUGINS."
        "The value of INMANTA_TEST_NO_LOAD_PLUGINS environment variable has to be a non-empty string to not load plugins."
        "When not using this option during the testing of plugins with the `project.get_plugin_function` method, "
        "it's possible that the module's `plugin/__init__.py` is loaded multiple times, "
        "which can cause issues when it has side effects, as they are executed multiple times as well.",
    )


def get_opt_or_env_or(config, key: str, default: str) -> str:
    if config.getoption(key):
        return config.getoption(key)
    if option_to_env[key] in os.environ:
        return os.environ[option_to_env[key]]
    return default


def get_module_info() -> typing.Tuple[str, str]:
    curdir = CURDIR
    # Make sure that we are executed in a module
    dir_path = curdir.split(os.path.sep)
    while (
        not os.path.exists(os.path.join(os.path.join("/", *dir_path), "module.yml"))
        and len(dir_path) > 0
    ):
        dir_path.pop()

    if len(dir_path) == 0:
        raise Exception(
            "Module test case have to be saved in the module they are intended for. "
            "%s not part of module path" % curdir
        )

    module_dir = os.path.join("/", *dir_path)
    with open(os.path.join(module_dir, "module.yml")) as m:
        module_name = yaml.safe_load(m)["name"]

    return module_dir, module_name


@pytest.fixture()
def inmanta_plugins(
    project: "Project",
) -> typing.Iterator["InmantaPluginsImportLoader"]:
    importer: InmantaPluginsImporter = InmantaPluginsImporter(project)
    yield importer.loader


@pytest.fixture()
def project(
    project_shared: "Project", capsys: CaptureFixture
) -> typing.Iterator["Project"]:
    DATA.clear()
    project_shared.clean()
    project_shared.init(capsys)
    yield project_shared
    project_shared.clean()


@pytest.fixture()
def project_no_plugins(
    project_shared_no_plugins, capsys: CaptureFixture
) -> typing.Iterator["Project"]:
    warnings.warn(
        DeprecationWarning(
            "The project_no_plugins fixture is deprecated in favor of the %s environment variable."
            % option_to_env["inm_no_load_plugins"]
        )
    )
    DATA.clear()
    project_shared_no_plugins.clean()
    project_shared_no_plugins.init(capsys)
    yield project_shared_no_plugins
    project_shared_no_plugins.clean()


def get_module_data(filename: str) -> str:
    """
    Get the given filename from the module directory in the source tree
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_path, "module", filename), "r") as fd:
        return fd.read()


@pytest.fixture(scope="session")
def project_shared(
    project_factory: typing.Callable[[typing.Dict[str, typing.Any]], "Project"]
) -> "Project":
    """
    A test fixture that creates a new inmanta project with the current module in. The returned object can be used
    to add files to the unittest module, compile a model and access the results, stdout and stderr.
    """
    yield project_factory()


# Temporary workaround for plugins loading multiple times (inmanta/pytest-inmanta#49)
@pytest.fixture(scope="session")
def project_shared_no_plugins(
    project_factory: typing.Callable[[typing.Dict[str, typing.Any]], "Project"]
) -> "Project":
    """
    A test fixture that creates a new inmanta project with the current module in. The returned object can be used
    to add files to the unittest module, compile a model and access the results, stdout and stderr.
    This project is initialized with load_plugins == False.
    """
    yield project_factory(load_plugins=False)


@pytest.fixture(scope="session")
def project_factory(request: pytest.FixtureRequest) -> typing.Callable[[], "Project"]:
    """
    A factory that constructs a single Project.
    """
    _sys_path = sys.path
    test_project_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(test_project_dir, "libs"))

    repo_options = get_opt_or_env_or(
        request.config, "inm_module_repo", "https://github.com/inmanta/"
    )
    repos = []
    if isinstance(repo_options, list):
        for repo in repo_options:
            repos += repo.split(" ")
    else:
        repos = repo_options.split(" ")

    install_mode = get_opt_or_env_or(request.config, "inm_install_mode", "release")

    modulepath = ["libs"]
    in_place = request.config.getoption("--use-module-in-place")
    if in_place:
        modulepath.append(str(Path(os.getcwd()).parent))

    env_override = get_opt_or_env_or(request.config, "inm_venv", None)
    if env_override and not os.path.isdir(env_override):
        raise Exception(f"Specified venv {env_override} does not exist")
    if env_override is not None:
        try:
            os.symlink(env_override, os.path.join(test_project_dir, ".env"))
        except OSError:
            LOGGER.exception(
                "Unable to use shared env (symlink creation from %s to %s failed).",
                env_override,
                os.path.join(test_project_dir, ".env"),
            )
            raise

    with open(os.path.join(test_project_dir, "project.yml"), "w+") as fd:
        fd.write(
            """name: testcase
description: Project for testcase
repo: ['%(repo)s']
modulepath: ['%(modulepath)s']
downloadpath: libs
install_mode: %(install_mode)s
"""
            % {
                "repo": "', '".join(repos),
                "install_mode": install_mode,
                "modulepath": "', '".join(modulepath),
            }
        )

    # copy the current module in
    module_dir, module_name = get_module_info()
    if not in_place:
        dir_util.copy_tree(
            module_dir, os.path.join(test_project_dir, "libs", module_name)
        )

    def create_project(**kwargs):
        extended_kwargs: typing.Dict[str, object] = {
            "load_plugins": not get_opt_or_env_or(
                request.config, "inm_no_load_plugins", False
            ),
            **kwargs,
        }
        test_project = Project(test_project_dir, **extended_kwargs)

        # create the unittest module
        test_project.create_module(
            "unittest",
            initcf=get_module_data("init.cf"),
            initpy=get_module_data("init.py"),
        )

        return test_project

    yield create_project

    try:
        shutil.rmtree(test_project_dir)
    except PermissionError:
        LOGGER.warning(
            "Cannot cleanup test project %s. This can be caused because we try to remove a virtual environment, "
            "loaded by this python process. Try to use a shared environment with --venv",
            test_project_dir,
        )

    sys.path = _sys_path


class MockProcess(object):
    """
    A mock agentprocess
    """

    def __init__(self):
        self._io_loop = ioloop.IOLoop.current()


class MockAgent(object):
    """
    A mock agent for unit testing
    """

    def __init__(self, uri):
        self.uri = uri
        self.process = MockProcess()
        self._env_id = cfg_env.get()


class InmantaPluginsImportLoader:
    """
    Makes inmanta_plugins packages (Python source for inmanta modules) available dynamically so that tests can use them
    safely without having to refresh imports when the compiler is reset.
    """

    def __init__(self, importer: "InmantaPluginsImporter") -> None:
        self._importer: InmantaPluginsImporter = importer

    def __getattr__(self, name: str):
        submodules: typing.Optional[
            typing.Dict[str, ModuleType]
        ] = self._importer.get_submodules(name)
        fq_mod_name: str = f"inmanta_plugins.{name}"
        if submodules is None or fq_mod_name not in submodules:
            raise AttributeError("No inmanta module named %s" % name)
        return submodules[fq_mod_name]


class InmantaPluginsImporter:
    def __init__(self, project: "Project") -> None:
        self.project: Project = project
        self.loader: InmantaPluginsImportLoader = InmantaPluginsImportLoader(self)

    def get_submodules(
        self, module_name: str
    ) -> typing.Optional[typing.Dict[str, ModuleType]]:
        inmanta_project: module.Project = module.Project.get()
        if not inmanta_project.loaded:
            raise Exception(
                "Dynamically importing from inmanta_plugins requires a loaded inmanta.module.Project. Make sure to use the"
                " project fixture."
            )
        modules: typing.Dict[str, module.Module] = inmanta_project.get_modules()
        if module_name not in modules:
            return None
        result = {}
        importlib.invalidate_caches()
        for _, fq_submod_name in self.get_plugin_files_for_module(modules[module_name]):
            result[str(fq_submod_name)] = importlib.import_module(fq_submod_name)
        return result

    # TODO: this method duplicates inmanta.module.Module.get_plugin_files (2020.4), see #76
    def get_plugin_files_for_module(
        self, mod: module.Module
    ) -> typing.Iterator[typing.Tuple[str, str]]:
        """
        Returns a tuple (absolute_path, fq_mod_name) of all python files in this module.
        """
        plugin_dir: str = os.path.join(mod._path, "plugins")

        if not os.path.exists(plugin_dir):
            return iter(())

        if not os.path.exists(os.path.join(plugin_dir, "__init__.py")):
            raise Exception(
                "The plugin directory %s should be a valid python package with a __init__.py file"
                % plugin_dir
            )
        return (
            (
                file_name,
                mod._get_fq_mod_name_for_py_file(file_name, plugin_dir, mod.name),
            )
            for file_name in glob.iglob(
                os.path.join(plugin_dir, "**", "*.py"), recursive=True
            )
        )


class Project:
    """
    This class provides a TestCase class for creating module unit tests. It uses the current module and loads required
    modules from the provided repositories. Additional repositories can be provided by setting the INMANTA_MODULE_REPO
    environment variable. Repositories are separated with spaces.
    """

    def __init__(self, project_dir: str, load_plugins: bool = True) -> None:
        self._test_project_dir = project_dir
        self._stdout: typing.Optional[str] = None
        self._stderr: typing.Optional[str] = None
        self.types: typing.Optional[typing.Dict[str, inmanta.ast.Type]] = None
        self.version: typing.Optional[int] = None
        self.resources: ResourceDict = {}
        self._root_scope: typing.Optional[inmanta.ast.Namespace] = None
        self._exporter: typing.Optional[Exporter] = None
        self._blobs: typing.Dict[str, bytes] = {}
        self._facts: typing.Dict[
            ResourceIdStr, typing.Dict[str, typing.Any]
        ] = defaultdict(dict)
        self._should_load_plugins: bool = load_plugins
        self._plugins: typing.Optional[typing.Dict[str, FunctionType]] = None
        self._load()
        self._capsys: typing.Optional[CaptureFixture] = None
        self.ctx: typing.Optional[HandlerContext] = None
        self._handlers: typing.Set[ResourceHandler] = set()
        config.Config.load_config()

    def init(self, capsys: CaptureFixture) -> None:
        self._stdout = None
        self._stderr = None
        self._capsys = capsys
        self.types = None
        self.version = None
        self.resources = {}
        self._root_scope = None
        self._exporter = None
        self._blobs = {}
        self._facts = defaultdict(dict)
        self.ctx = None
        self._handlers = set()
        self._load()
        config.Config.load_config()

    def add_blob(self, key: str, content: bytes, allow_overwrite: bool = True) -> None:
        """
        Add a blob identified with the hash of the content as key
        """
        if isinstance(content, str):
            warnings.warn("received a string, but expect bytes", DeprecationWarning)
            content = content.encode("utf-8")
        if key in self._blobs and not allow_overwrite:
            raise Exception("Key %s already stored in blobs" % key)
        self._blobs[key] = content

    def stat_blob(self, key: str) -> bool:
        return key in self._blobs

    def get_blob(self, key: str) -> bytes:
        return self._blobs[key]

    def add_fact(self, resource_id: ResourceIdStr, name: str, value: object) -> None:
        self._facts[resource_id][name] = value

    def get_handler(self, resource: Resource, run_as_root: bool) -> ResourceHandler:
        # TODO: if user is root, do not use remoting
        c = cache.AgentCache()
        if run_as_root:
            agent = MockAgent("ssh://root@localhost")
        else:
            agent = MockAgent("local:")

        c.open_version(resource.id.version)
        try:
            p = handler.Commander.get_provider(c, agent, resource)  # typing: ignore
            p.set_cache(c)
            p.get_file = lambda x: self.get_blob(x)  # typing: ignore
            p.stat_file = lambda x: self.stat_blob(x)  # typing: ignore
            p.upload_file = lambda x, y: self.add_blob(x, y)  # typing: ignore
            p.run_sync = ioloop.IOLoop.current().run_sync  # typing: ignore
            self._handlers.add(p)
            return p
        except Exception as e:
            raise e

    def finalize_context(self, ctx: handler.HandlerContext) -> None:
        # ensure logs can be serialized
        json_encode({"message": ctx.logs})

    def get_resource(
        self, resource_type: str, **filter_args: typing.Dict[str, object]
    ) -> typing.Optional[Resource]:
        """
        Get a resource of the given type and given filter on the resource attributes. If multiple resource match, the
        first one is returned. If none match, None is returned.

        :param resource_type: The exact type used in the model (no super types)
        """

        def apply_filter(resource: Resource) -> bool:
            for arg, value in filter_args.items():
                if not hasattr(resource, arg):
                    return False

                if getattr(resource, arg) != value:
                    return False

            return True

        for resource in self.resources.values():
            if not resource.is_type(resource_type):
                continue

            if not apply_filter(resource):
                continue

            resource = self.check_serialization(resource)
            return resource

        return None

    def deploy(
        self, resource: Resource, dry_run: bool = False, run_as_root: bool = False
    ) -> HandlerContext:
        """
        Deploy the given resource with a handler
        """
        assert resource is not None

        h = self.get_handler(resource, run_as_root)

        assert h is not None

        ctx = handler.HandlerContext(resource)
        h.execute(ctx, resource, dry_run)
        self.finalize_context(ctx)
        self.ctx = ctx
        self.finalize_handler(h)
        return ctx

    def dryrun(self, resource: Resource, run_as_root: bool = False) -> HandlerContext:
        return self.deploy(resource, True, run_as_root)

    def deploy_resource(
        self,
        resource_type: str,
        status: const.ResourceState = const.ResourceState.deployed,
        run_as_root: bool = False,
        change: const.Change = None,
        **filter_args: typing.Dict[str, object],
    ) -> Resource:
        """
        Deploy a resource of the given type, that matches the filter and assert the outcome

        :param resource_type: the type of resource to deploy
        :param filter_args: a set of kwargs, the resource must have all matching attributes set to the given values
        :param run_as_root: run the handler as root or not
        :param status: the expected status of the deployment
        :param change: the expected change performed by the handler

        :return: the resource
        """
        res = self.get_resource(resource_type, **filter_args)
        assert res is not None, "No resource found of given type and filter args"

        ctx = self.deploy(res, run_as_root)
        if ctx.status != status:
            print("Deploy did not result in correct status")
            print("Requested changes: ", ctx._changes)
            for log in ctx.logs:
                print("Log: ", log._data["msg"])
                print(
                    "Kwargs: ",
                    [
                        "%s: %s" % (k, v)
                        for k, v in log._data["kwargs"].items()
                        if k != "traceback"
                    ],
                )
                if "traceback" in log._data["kwargs"]:
                    print("Traceback:\n", log._data["kwargs"]["traceback"])

        assert ctx.status == status
        if change is not None:
            assert ctx._change == change
        self.finalize_context(ctx)
        return res

    def dryrun_resource(
        self,
        resource_type: str,
        status: const.ResourceState = const.ResourceState.dry,
        run_as_root: bool = False,
        **filter_args: typing.Dict[str, object],
    ) -> typing.Dict[str, AttributeStateChange]:
        """
        Run a dryrun for a specific resource.

        :param resource_type: the type of resource to run, as a fully qualified inmanta type (e.g. `unittest::Resource`),
            see :py:meth:`get_resource`
        :param status: the expected result status
            (for dryrun the success status is :py:attr:`inmanta.const.ResourceState.dry`)
        :param run_as_root: run the mock agent as root
        :param filter_args: filters for selecting the resource, see :py:meth:`get_resource`
        """
        res = self.get_resource(resource_type, **filter_args)
        assert res is not None, "No resource found of given type and filter args"

        ctx = self.dryrun(res, run_as_root)
        assert ctx.status == status
        return ctx.changes

    def io(self, run_as_root: bool = False) -> "IOBase":
        version = 1
        if run_as_root:
            ret = agent_io.get_io(None, "ssh://root@localhost", version)
        else:
            ret = agent_io.get_io(None, "local:", version)
        return ret

    def create_module(self, name: str, initcf: str = "", initpy: str = "") -> None:
        module_dir = os.path.join(self._test_project_dir, "libs", name)
        os.mkdir(module_dir)
        os.mkdir(os.path.join(module_dir, "model"))
        os.mkdir(os.path.join(module_dir, "files"))
        os.mkdir(os.path.join(module_dir, "templates"))
        os.mkdir(os.path.join(module_dir, "plugins"))

        with open(os.path.join(module_dir, "model", "_init.cf"), "w+") as fd:
            fd.write(initcf)

        with open(os.path.join(module_dir, "plugins", "__init__.py"), "w+") as fd:
            fd.write(initpy)

        with open(os.path.join(module_dir, "module.yml"), "w+") as fd:
            fd.write(
                f"""name: {name}
version: 0.1
license: Test License
            """
            )

    def _load(self) -> None:
        """
        Load the current module and compile an otherwise empty project
        """
        _, module_name = get_module_info()
        with open(os.path.join(self._test_project_dir, "main.cf"), "w+") as fd:
            fd.write(f"import {module_name}")
        test_project = module.Project(self._test_project_dir)
        module.Project.set(test_project)
        test_project.load()
        # refresh plugins
        if self._should_load_plugins is not None:
            self._plugins = self._load_plugins()

    def compile(self, main: str, export: bool = False, no_dedent: bool = True) -> None:
        """
        Compile the configuration model in main. This method will load all required modules.

        :param main: The model to compile
        :param export: Whether the model should be exported after the compile
        :param no_dedent: Don't remove additional indentation in the model
        """
        # Dedent the input format
        model = dedent(main.strip("\n")) if not no_dedent else main

        # write main.cf
        with open(os.path.join(self._test_project_dir, "main.cf"), "w+") as fd:
            fd.write(model)

        # logging model with line numbers
        def enumerate_model(model: str):
            lines = model.split("\n")
            leading_zeros = math.floor(math.log(len(lines), 10)) + 1
            line_numbers_model = "\n".join(
                [
                    f"{str(number).zfill(leading_zeros)}    {line}"
                    for number, line in enumerate(lines, start=1)
                ]
            )
            return line_numbers_model

        LOGGER.debug(f"Compiling model:\n{enumerate_model(model)}")

        # compile the model
        test_project = module.Project(self._test_project_dir)
        module.Project.set(test_project)
        test_project.load()
        # refresh plugins
        if self._should_load_plugins is not None:
            self._plugins = self._load_plugins()

        # flush io capture buffer
        self._capsys.readouterr()

        (types, scopes) = compiler.do_compile(refs={"facts": self._facts})

        exporter = Exporter()

        version, resources = exporter.run(types, scopes, no_commit=not export)

        for key, blob in exporter._file_store.items():
            self.add_blob(key, blob)

        self._root_scope = scopes
        self.version = version
        self.resources = resources
        self.types = types
        self._exporter = exporter

        captured = self._capsys.readouterr()

        self._stdout = captured.out
        self._stderr = captured.err

    def deploy_latest_version(self, full_deploy: bool = False) -> None:
        """Release and push the latest version to the server (uses the current configuration, either with a fixture or
        set by the test.
        """
        if self.version is None:
            raise Exception("Run project.compile first")
        conn = protocol.SyncClient("compiler")
        LOGGER.info("Triggering deploy for version %d" % self.version)
        tid = cfg_env.get()
        agent_trigger_method = const.AgentTriggerMethod.get_agent_trigger_method(
            full_deploy
        )
        conn.release_version(tid, self.version, True, agent_trigger_method)

    def get_last_context(self) -> typing.Optional[HandlerContext]:
        return self.ctx

    def get_last_logs(self) -> typing.Optional[typing.List[LogLine]]:
        if self.ctx:
            return self.ctx.logs
        return None

    def get_stdout(self) -> typing.Optional[str]:
        return self._stdout

    def get_stderr(self) -> typing.Optional[str]:
        return self._stderr

    def get_root_scope(self) -> typing.Optional[inmanta.ast.Namespace]:
        return self._root_scope

    def add_mock_file(self, subdir: str, name: str, content: str) -> None:
        """
        This method can be used to register mock templates or files in the virtual "unittest" module.
        """
        dir_name = os.path.join(self._test_project_dir, "libs", "unittest", subdir)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        with open(os.path.join(dir_name, name), "w+") as fd:
            fd.write(content)

    def _load_plugins(self) -> typing.Dict[str, FunctionType]:
        _, module_name = get_module_info()
        submodules: typing.Optional[
            typing.Dict[str, ModuleType]
        ] = InmantaPluginsImporter(self).get_submodules(module_name)
        return (
            {}
            if submodules is None
            else {
                k: v
                for submod in submodules.values()
                for k, v in submod.__dict__.items()
                if isinstance(v, FunctionType)
            }
        )

    def get_plugin_function(self, function_name: str) -> FunctionType:
        if self._plugins is None:
            raise Exception(
                "Plugins not loaded, perhaps you should use the `project` fixture or"
                " initialize the Project with load_plugins == True"
            )
        if function_name not in self._plugins:
            raise Exception(f"Plugin function with name {function_name} not found")
        return self._plugins[function_name]

    def get_plugins(self) -> typing.Dict[str, FunctionType]:
        if self._plugins is None:
            raise Exception(
                "Plugins not loaded, perhaps you should use the `project` fixture or"
                " initialize the Project with load_plugins == True"
            )
        return dict(self._plugins)

    def get_instances(self, fortype: str = "std::Entity") -> typing.List[DynamicProxy]:
        if self.types is None:
            raise Exception("No compile has been done")
        if fortype not in self.types:
            raise Exception(f"No entities of type {fortype} found in the model")

        # extract all objects of a specific type from the compiler
        allof = self.types[fortype].get_all_instances()
        # wrap in DynamicProxy to hide internal compiler structure
        # and get inmanta objects as if they were python objects
        return [DynamicProxy.return_value(port) for port in allof]

    def unittest_resource_exists(self, name: str) -> bool:
        """
        Check if a unittest resource with name exists or not
        """
        return name in DATA

    def unittest_resource_get(
        self, name: str
    ) -> typing.Dict[str, typing.Union[str, bool, float, int]]:
        """
        Get the state of the unittest resource
        """
        return DATA[name]

    def unittest_resource_set(
        self, name: str, **kwargs: typing.Union[str, bool, float, int]
    ) -> None:
        """
        Change a value of the unittest resource
        """
        DATA[name].update(kwargs)

    def check_serialization(self, resource: Resource) -> Resource:
        """ Check if the resource is serializable """
        serialized = json.loads(json_encode(resource.serialize()))
        return Resource.deserialize(serialized)

    def clean(self) -> None:
        shutil.rmtree(os.path.join(self._test_project_dir, "libs", "unittest"))
        self.finalize_all_handlers()
        self.create_module(
            "unittest",
            initcf=get_module_data("init.cf"),
            initpy=get_module_data("init.py"),
        )

    def finalize_handler(self, handler: ResourceHandler) -> None:
        handler.cache.close()

    def finalize_all_handlers(self) -> None:
        for handler_instance in self._handlers:
            self.finalize_handler(handler_instance)
