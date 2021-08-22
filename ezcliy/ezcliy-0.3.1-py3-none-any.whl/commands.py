import asyncio
import inspect
import os
import sys
from functools import cache
from typing import Optional, Any

from sty import ef, fg
from ezcliy.exceptions import MessageableException, UnexceptedNumberOfValues
from ezcliy.helpman import Helpman
from ezcliy.parameters import Parameter
from ezcliy.positional import Positional


class Command:
    """Base class for creating commands. You probably will override this class"""

    name: str = None
    """Name of command"""

    description: str = None
    """Description for help"""

    values: list[str] = []
    """Cleaned values from cmd"""

    _legacy: dict[str, Parameter] = {}
    """Parameters inherited after previous command"""

    require_all_defined_positionals = False
    """If true, allow only values referenced as positionals"""

    none_args_will_not_trigger_help = True
    """If true, will not print help when command is issued without parameters"""

    _helpman: Helpman = None
    """Object that handles --help, it's just a god tier flag instance"""

    def __init__(self):
        if self.name is None:
            self.name = self.__class__.__name__.lower()
        self._helpman = Helpman()

        if self.none_args_will_not_trigger_help:
            self._helpman.description = 'Shows help.'
        else:
            self._helpman.description = 'Shows help even when no arguments are passed.'

        self.__subcommand_issued = None

    def __repr__(self):
        return f'<Command {self.name}>'

    @property
    @cache
    def commands(self) -> dict[str, type]:
        """

        :return: Subcommands
        """
        cmds = dict()
        for pair in [{o().name: o} for o in self.__class__.__dict__.values() if isinstance(o, type) if
                     issubclass(o, Command)]:
            cmds.update(pair)
        return cmds

    @property
    def is_subcommand_issued(self):
        """

        :return: True if subcommand has been issued
        :rtype: bool
        """
        if self.__subcommand_issued is not None:
            return self.__subcommand_issued

        if len(self.values) > 0:
            self.__subcommand_issued = self.values[0] in self.commands.keys()
        else:
            self.__subcommand_issued = False
        return self.is_subcommand_issued

    @property
    @cache
    def parameters(self) -> dict[str, Parameter]:
        """

        :return: All declared parameters as name-parameter dict
        :rtype: dict[str, Parameter]
        """
        parameters = {'_helpman': self._helpman}
        for name, param in [(n, p) for n, p in (self.__class__.__dict__ | self.__dict__).items() if
                            isinstance(p, Parameter)]:
            parameters.update({name: param})
        return parameters

    @property
    @cache
    def positionals(self):
        """

        :return: All declared positionals
        :rtype: list[Positional]
        """
        return [p for p in self.__class__.__dict__.values() if isinstance(p, Positional)]

    def __help_check(self):
        if self._helpman:
            print(self._helpman.render_help(self))
            sys.exit()

        if len([p for p in self.positionals if p is not None]):
            return

    def __restriction_check(self):
        if len(self.values) != len(self.positionals) and self.require_all_defined_positionals:
            raise UnexceptedNumberOfValues(self.values, len(self.positionals))

    def __load_predecessors_params(self):
        if self._legacy.get('_helpman', False):
            # noinspection PyTypeChecker
            self._helpman = self._legacy['_helpman']
        for n, param in self._legacy.items():
            if n in self.__annotations__ | self.__class__.__annotations__:
                self.__setattr__(n, param)

    def __pass_values_to_positionals(self):
        for i, p in enumerate(self.positionals):
            p.pass_values(self.values, i)

    def dispatch(self, args: list[str]):
        """
        The magic spaghetti of framework.

        :param args: list of arguments to process
        """
        # Loading predecessor's parameters
        self.__load_predecessors_params()

        # Special help check
        if not len(args) and not self.none_args_will_not_trigger_help:
            print(self._helpman.render_help(self))
            sys.exit()

        # Shrink requested parameters
        for argument in [p for p in self.parameters.values() if not p.lock]:
            args = argument.pass_args(args)

        # Save cleaned values
        self.values = [arg for arg in args if not arg.startswith('-') and arg != '']

        # Check is first arg an command
        if len(self.values) > 0:
            if self.is_subcommand_issued:
                # Shrink values
                cmd_name, self.values = self.values[0], self.values[1:]
                # Checks
                self.__restriction_check()
                # Invoke, has args, first is subcommand
                if not self._helpman:
                    self.__invoke_handler()
                # Prepare subcommand
                cmd: Command = self.commands.get(cmd_name)()
                cmd._legacy = self.parameters.copy()  # Passing aquired flags
                cmd.dispatch(args[args.index(cmd_name) + 1:])  # Passing only args after command
                return

        self.__help_check()
        self.__restriction_check()
        self.__pass_values_to_positionals()  # This should raise an error
        return self.__invoke_handler()  # Has no args

    def __invoke_handler(self):
        if inspect.iscoroutinefunction(self.invoke):
            # noinspection PyTypeChecker
            return asyncio.run(self.invoke())
        else:
            return self.invoke()

    # Invocation
    def invoke(self) -> Optional[Any]:
        """
        The entry point for your command. Can return values while being called by ``entry`` or ``cli_entry``.
        """
        ...

    # Entry points
    def entry(self, *args: str):
        """
        Handles errors caused by dispatch method. Used also for testing. Use it on dev env.

        :param str args: list of passed arguments
        """
        return self.dispatch(list(args))

    def cli_entry(self):
        """
        This method grabs args from terminal. You should put it into ``if main``. This should be used in production.
        """
        self.entry(*sys.argv[1:])
