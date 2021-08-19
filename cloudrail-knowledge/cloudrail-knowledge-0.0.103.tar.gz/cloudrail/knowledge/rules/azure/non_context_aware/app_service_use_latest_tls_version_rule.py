from typing import List, Dict
from packaging import version
from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class AppServiceUseLatestTlsVersionRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_web_app_using_latest_tls_version'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for app_service in env_context.app_services:
            if app_service.app_service_config is not None:
                tls_version = version.parse(app_service.app_service_config.minimum_tls_version)
                if tls_version < version.parse('1.2'):
                    issues.append(
                        Issue(
                            f'The Web App `{app_service.get_friendly_name()}` uses `{tls_version}` for '
                            f'the minimum TLS version, instead of 1.2.', app_service, app_service))
            return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.app_services)
