"""
cmdtools extension

Class:
    Command:
        Parameters:
            - name: command name

    CommandObject:
        Parameters:
            - name: command name
            - object_: command module or object

    CommandDir:
        Parameters:
            - rootdir: root directory of command files

    CommandModule:
        Parameters:
            - filename: filename or module name

    CommandRunner:
        Parameters:
            - command: CommandObject class to run

    CommandRunnerContainer:
        Parameters:
            - commands: list of CommandObject class to run

    CommandWrapperObject:
        -

    CommandWrapper:
        Parameters:
            - commands: list of CommandWrapperObject class to run

"""

import os
import inspect
import logging
import importlib
import cmdtools


class DuplicateCommandNameError(Exception):
    pass


class RunnerError(Exception):
    """
    raised when running an unmatched command name
    or some other exceptions
    """


class CommandWrapperObject:
    def __init__(self):
        self.name = None
        self.aliases = []
        self.callback = None
        self.error_callback = None

    def error(self, func):
        self.error_callback = func

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def __call__(self):
        return self.callback(*self._args, **self._kwargs)

    def _checkfunc(self, func) -> bool:
        """check is object callable"""
        if func is not None and (
            inspect.isfunction(func)
            or inspect.ismethod(func)
            or inspect.iscoroutinefunction(func)
        ):
            return True

        return False

    def is_coroutine(self) -> bool:
        """check whether command is coroutine or not, based by the callbacks"""
        if self.has_callback():
            return inspect.iscoroutinefunction(self.callback)
        elif self.has_callback() and self.has_error_callback():
            return inspect.iscoroutinefunction(
                self.callback
            ) and inspect.iscoroutinefunction(self.error_callback)

        # not a coroutine or object does not have command callback
        return False

    def has_callback(self) -> bool:
        """check whether callback is exist or not"""
        return self._checkfunc(self.callback)

    def has_error_callback(self) -> bool:
        """check whether error callback is exist or not"""
        return self._checkfunc(self.error_callback)


class CommandWrapper:
    """wrapper for commands (?)"""
    def __init__(self, commands: list = None):
        if commands is None:
            commands = []

        self.commands = commands

    def command(self, *args, **kwargs):
        """base decorator for callbacks"""
        def decorator(obj):
            if (inspect.isfunction(obj), inspect.ismethod(obj), inspect.iscoroutinefunction(obj)).count(True) > 0:
                wrapper = CommandWrapperObject()

                for attr in kwargs:
                    setattr(wrapper, attr, kwargs[attr])

                wrapper.name = kwargs.get('name', obj.__name__)
                wrapper.aliases = kwargs.get('aliases', [])
                wrapper.callback = obj
                self.commands.append(wrapper)

                def func_wrapper(*args, **kwargs):
                    setattr(wrapper, "_args", args)
                    setattr(wrapper, "_kwargs", kwargs)
                    return wrapper
                return func_wrapper()
            elif inspect.isclass(obj):
                if isinstance(obj(), CommandObject):
                    self.commands.append(obj())
            else:
                raise TypeError("Cannot assign command for object:", type(obj))
        return decorator

    async def run(self, cmd, attrs: dict = None):
        if attrs is None:
            attrs = {}

        if not isinstance(cmd, cmdtools.Cmd):
            raise TypeError("cmd is not a cmdtools Cmd class")

        for command in self.commands:
            if command.name == cmd.name or cmd.name in command.aliases:
                args = []
                if command.has_callback():
                    args.append(command.callback)
                else:
                    return logging.error(
                        f"Command name '{command.name}' has no callback"
                    )
                if command.has_error_callback():
                    args.append(command.error_callback)

                if command.is_coroutine():
                    return await cmd.aio_process_cmd(*args, attrs=attrs)

                return cmd.process_cmd(*args, attrs=attrs)

        raise RunnerError(f"Couln't find command '{cmd.name}'")


class CommandObject:
    """command object container"""

    def __init__(self, object_, name: str = None):
        self.object = object_

        # try get the command name from the module or class first
        # if no preset name, use command file name as the command name
        self.name = getattr(self.object, "name", name)  # type: str

    @property
    def aliases(self) -> list:
        return getattr(self.object, "_aliases", [])

    @property
    def callback(self):
        return getattr(self.object, self.name, None)

    @property
    def error_callback(self):
        return getattr(self.object, "error_" + self.name, None)

    def _checkfunc(self, func) -> bool:
        """check is object callable"""
        if func is not None and (
            inspect.isfunction(func)
            or inspect.ismethod(func)
            or inspect.iscoroutinefunction(func)
        ):
            return True

        return False

    def is_coroutine(self) -> bool:
        """check whether command is coroutine or not, based by the callbacks"""
        if self.has_callback():
            return inspect.iscoroutinefunction(self.callback)
        elif self.has_callback() and self.has_error_callback():
            return inspect.iscoroutinefunction(
                self.callback
            ) and inspect.iscoroutinefunction(self.error_callback)

        # not a coroutine or object does not have command callback
        return False

    def has_callback(self) -> bool:
        """check whether callback is exist or not"""
        return self._checkfunc(self.callback)

    def has_error_callback(self) -> bool:
        """check whether error callback is exist or not"""
        return self._checkfunc(self.error_callback)


class Command(CommandObject):
    """main command class inheritance"""

    def __init__(self, name):
        super().__init__(name=name, object_=self)


class CommandRunner:
    """command single runner class"""

    def __init__(self, command: CommandObject):
        self.command = command

    async def run(self, cmd: cmdtools.Cmd, attrs: dict = None):
        """run command from parsed command object"""

        if not isinstance(cmd, cmdtools.Cmd):
            raise TypeError("cmd is not a cmdtools Cmd class")

        if attrs is None:
            attrs = {}

        if self.command.name == cmd.name or cmd.name in self.command.aliases:
            args = []
            if self.command.has_callback():
                args.append(self.command.callback)
            else:
                return logging.error(
                    f"Command name '{self.command.name}' has no callback"
                )
            if self.command.has_error_callback():
                args.append(self.command.error_callback)

            if self.command.is_coroutine():
                return await cmd.aio_process_cmd(*args, attrs=attrs)

            return cmd.process_cmd(*args, attrs=attrs)

        raise RunnerError("Command name is invalid")


class CommandRunnerContainer:
    """command runner container class inheritance"""

    def __init__(self, commands: list):
        self.commands = commands

    async def run(self, cmd: cmdtools.Cmd, attrs: dict = None):
        """run command from parsed command object"""

        if not isinstance(cmd, cmdtools.Cmd):
            raise TypeError("cmd is not a cmdtools Cmd class")

        if attrs is None:
            attrs = {}

        for command in self.commands:
            if command.name == cmd.name or cmd.name in command.aliases:
                args = []
                if command.has_callback():
                    args.append(command.callback)
                else:
                    return logging.error(
                        f"Command name '{command.name}' has no callback"
                    )
                if command.has_error_callback():
                    args.append(command.error_callback)

                if command.is_coroutine():
                    return await cmd.aio_process_cmd(*args, attrs=attrs)

                return cmd.process_cmd(*args, attrs=attrs)

        raise RunnerError(f"Couln't find command '{cmd.name}'")


class CommandModule(CommandRunnerContainer):
    """command module container class"""

    def __init__(self, filename: str, **attrs):
        self.filename = filename
        self.commands = []

        self.load_classes = attrs.get("load_classes", True)

        self.load_module(load_classes=self.load_classes)
        super().__init__(commands=self.commands)

    def load_module(self, load_classes):
        """load command classes from a module"""
        if self.filename.endswith(".py"):
            modulestr = (
                self.filename.rsplit(".py", 1)[0].replace(os.sep, ".").strip(".")
            )
            module = importlib.import_module(modulestr)

            if load_classes:
                for obj in dir(module):
                    obj_ = getattr(module, obj, None)

                    if inspect.isclass(obj_) and obj_.__module__ == module.__name__:
                        if isinstance(obj_(), CommandObject):
                            cobj = obj_()

                            if cobj.name not in get_command_names(self.commands):
                                self.commands.append(cobj)
                            else:
                                raise DuplicateCommandNameError(
                                    f"Command with name '{cobj.name}' is already exist in command container"
                                )
            else:
                self.commands.append(CommandObject(module))


class CommandDir(CommandRunnerContainer):
    """command directory container class"""

    def __init__(self, rootdir: str, **attrs):
        self.rootdir = rootdir.replace("/", os.sep).replace("\\", os.sep)
        self.commands = []
        self.search_tree: bool = attrs.get("search_tree", False)
        self.load_classes: bool = attrs.get("load_classes", False)

        self.load_commands(search_tree=self.search_tree, load_classes=self.load_classes)
        super().__init__(commands=self.commands)

    def load_commands(self, search_tree, load_classes):
        """load commands from files inside rootdir"""
        dirs = []
        if search_tree:
            for root in os.walk(self.rootdir):
                dirs.append(root[0])

        if self.rootdir not in dirs:
            dirs.append(self.rootdir)

        for path in dirs:
            for file in os.listdir(path):
                if os.path.isfile(path + os.sep + file) and file.endswith(".py"):
                    module = importlib.import_module(
                        path.replace(os.sep, ".").strip(".")
                        + "."
                        + file.rsplit(".py", 1)[0]
                    )
                    if self.load_classes is False:
                        cobj = CommandObject(module, file.rsplit(".py", 1)[0])
                        if cobj.name not in get_command_names(self.commands):
                            self.commands.append(cobj)
                        else:
                            raise DuplicateCommandNameError(
                                f"Command with name '{cobj.name}' is already exist in command container"
                            )
                    else:
                        for obj in dir(module):
                            obj_ = getattr(module, obj, None)

                            if inspect.isclass(obj_) and obj_.__module__ == module.__name__:
                                if isinstance(obj_(), CommandObject):
                                    cobj = obj_()

                                    if cobj.name not in get_command_names(
                                        self.commands
                                    ):
                                        self.commands.append(cobj)
                                    else:
                                        raise DuplicateCommandNameError(
                                            f"Command with name '{cobj.name}' is already exist in command container"
                                        )


def get_command_names(commands: list, get_aliases=False):
    """get command names from command list of CommandObject"""
    names = []
    for command in commands:
        names.append(command.name)

        if hasattr(command, "aliases") and get_aliases:
            names.extend(command.aliases)

    return names
