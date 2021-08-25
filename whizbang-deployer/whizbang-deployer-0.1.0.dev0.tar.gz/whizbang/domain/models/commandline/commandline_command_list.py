from whizbang.domain.models.commandline.command_list import CommandList
from whizbang.domain.menu.deploy_command import DeployCommand



class CommandLineCommandList(CommandList):
    def __init__(self,
                 deploy_command: DeployCommand):
        CommandList.__init__(self,
                             deploy_command=deploy_command)
