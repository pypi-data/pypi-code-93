
from whizbang.domain.commandline.commandline_invoker import CommandLineInvoker
from whizbang.domain.models.commandline.commandline_command_list import CommandLineCommandList
from dependency_injector import containers, providers

from whizbang.domain.commandline.deploy_command import DeployCommand
from whizbang.domain.shared_types.named_solutions import NamedSolutions


class CommandlineContainer(containers.DeclarativeContainer):
    solution_factory = providers.Dependency()
    environment_config = providers.Dependency()

    named_solutions = providers.Factory(
        NamedSolutions
    )

    deploy_command = providers.Factory(
        DeployCommand,
        solution_factory=solution_factory,
        environment_config=environment_config
    )
    
    commandline_command_list = providers.Factory(
        CommandLineCommandList,
        deploy_command=deploy_command
    )
    
    commandline_invoker = providers.Singleton(
        CommandLineInvoker,
        commandline_command_list=commandline_command_list
    )
