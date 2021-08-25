from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.models.bicep_deployment import BicepDeployment
from whizbang.domain.workflow.bicep.bicep_tasks import BicepTaskNames
from whizbang.domain.workflow.bicep.deploy_bicep_workflow import DeployBicepWorkflow
from whizbang.util import path_defaults


class IBicepHandler(IHandler):
    """"""

    def deploy_bicep_template(self, solution_name: str, parameters, env_config: EnvironmentConfig):
        """"""


class BicepHandler(HandlerBase, IBicepHandler):
    def __init__(self, app_config: AppConfig, deploy_bicep_workflow: DeployBicepWorkflow):
        HandlerBase.__init__(self, app_config=app_config)
        self.__deploy_bicep_workflow = deploy_bicep_workflow

    def deploy_bicep_template(self, solution_name: str, parameters, env_config: EnvironmentConfig):
        template_path = path_defaults.get_bicep_template_path(app_config=self._app_config, solution_name=solution_name)
        parameters_path = path_defaults.get_bicep_parameters_path(app_config=self._app_config,
                                                                  solution_name=solution_name)

        deployment_name = "test"

        deployment = BicepDeployment(
            parameters=parameters,
            solution_name=solution_name,
            template_path=template_path,
            parameters_path=parameters_path,
            resource_group_name=env_config.resource_group_name,
            resource_group_location=env_config.resource_group_location,
            deployment_name=deployment_name
        )

        result = self.__deploy_bicep_workflow.run(deployment)
        return result[BicepTaskNames.deploy_bicep_template]
