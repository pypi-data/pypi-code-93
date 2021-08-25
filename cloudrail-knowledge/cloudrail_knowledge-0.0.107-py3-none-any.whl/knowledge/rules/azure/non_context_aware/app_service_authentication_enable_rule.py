from typing import List, Dict

from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class AppServiceAuthenticationEnableRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_authentication_enabled_in_web_app'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for app_service in env_context.app_services:
            if app_service.app_service_config is not None and \
                    app_service.app_service_config.auth_settings is not None and \
                    not app_service.app_service_config.auth_settings.enabled:
                issues.append(
                    Issue(
                        f'The web app `{app_service.get_friendly_name()}` does not have authentication enabled.',
                        app_service,
                        app_service))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.app_services)
