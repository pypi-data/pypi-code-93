import abc
from whizbang.domain.models.commandline.commandline_command_list import CommandLineCommandList
from whizbang.domain.shared_types.named_solutions import NamedSolutions
 

class ICommandLineInvoker(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __execute(self):
        """"""
        

class CommandLineInvoker:
    def __init__(self, commandline_command_list: CommandLineCommandList):
        self._commandline_command_list = commandline_command_list.command_list

    def execute(self):
        for option in self._commandline_command_list:
            if option.display_name == "deploy":
                option.command(NamedSolutions.cortex_accelerator)
                return