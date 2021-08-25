from whizbang.domain.solution.solution_factory import ISolutionFactory
from whizbang.domain.commandline.command_base import CommandBase, ICommandBase

class IDeployCommand(ICommandBase):
    """"""


class DeployCommand(CommandBase, IDeployCommand):
    def __init__(self, environment_config, solution_factory: ISolutionFactory):
        self.environment_config = environment_config
        self.__solution_factory = solution_factory

    @property
    def display_name(self) -> str:
        return 'deploy'

    @property
    def command_abbreviation(self) -> str:
        return 'd'

    @property
    def command_description(self) -> str:
        return 'deploy a solution by name'

    def command(self, name):
        # solution = self.__solution_factory.get_solution(name)
        # solution.deploy()
        print("deploy command was kicked off")



