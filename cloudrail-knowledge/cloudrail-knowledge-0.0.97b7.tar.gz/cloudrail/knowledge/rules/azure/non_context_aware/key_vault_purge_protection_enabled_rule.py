from typing import List, Dict

from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class KeyVaultPurgeProtectionEnabledRule(AzureBaseRule):
    def get_id(self) -> str:
        return 'non_car_key_vault_purge_protection_enabled'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []

        for key_vault in env_context.key_vaults:
            if not key_vault.purge_protection_enabled:
                issues.append(Issue(f'The {key_vault.get_type()} `{key_vault.get_friendly_name()}` does not have purge protection enabled', key_vault, key_vault))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.key_vaults)
