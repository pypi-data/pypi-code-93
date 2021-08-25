from typing import List, Dict
from packaging import version
from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class FunctionAppUseLatestTlsVersionRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_function_app_using_latest_tls_version'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for func_app in env_context.function_apps:
            if func_app.app_service_config is not None:
                tls_version = version.parse(func_app.app_service_config.minimum_tls_version)
                if tls_version < version.parse('1.2'):
                    issues.append(
                        Issue(
                            f'The {func_app.get_type()} `{func_app.get_friendly_name()}` uses `{tls_version}` for '
                            f'the minimum TLS version, instead of 1.2.', func_app, func_app))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.function_apps)
