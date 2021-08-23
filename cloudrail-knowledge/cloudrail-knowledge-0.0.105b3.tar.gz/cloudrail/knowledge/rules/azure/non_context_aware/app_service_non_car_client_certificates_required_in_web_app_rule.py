from typing import List, Dict
from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class AppServiceClientCertificatesRequiredRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_client_certificates_required_in_web_app'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for app_service in env_context.app_services:
            if not app_service.client_cert_required:
                issues.append(
                    Issue(
                        f'The {app_service.get_type()} `{app_service.get_friendly_name()}` does not have client certificates enabled.',
                        app_service,
                        app_service))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.app_services)
