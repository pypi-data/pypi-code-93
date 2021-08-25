from typing import List, Dict
from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class EnsureManagedDisksEncryptedRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_unattached_managed_disks_encrypted'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for managed_disk in env_context.managed_disks:
            if not managed_disk.is_encrypted:
                issues.append(
                    Issue(
                        f'The {managed_disk.get_type()} `{managed_disk.get_friendly_name()}` does not have encryption enabled',
                        managed_disk,
                        managed_disk))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.managed_disks)
