from whizbang.domain.menu.deploy_command import DeployCommand
from whizbang.domain.menu.command_base import CommandBase


class CommandList:
    def __init__(self,
                 deploy_command: DeployCommand):
        self.command_list: 'list[CommandBase]' = []
        self.command_list.append(deploy_command)