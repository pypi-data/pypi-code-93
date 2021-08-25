from typing import Dict, List

from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class EnsureSqlServerAuditEnabledRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_sql_servers_auditing_enabled'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for sql_server in env_context.sql_servers:
            if not sql_server.extended_auditing_policy or not sql_server.extended_auditing_policy.log_monitoring_enabled:
                issues.append(
                    Issue(
                        f'The {sql_server.get_type()} `{sql_server.get_friendly_name()}` does not have auditing enabled',
                        sql_server,
                        sql_server))
            elif sql_server.extended_auditing_policy and sql_server.extended_auditing_policy.log_monitoring_enabled \
                and 0 < sql_server.extended_auditing_policy.retention_in_days <= 90:
                issues.append(
                Issue(
                    f'The {sql_server.get_type()} `{sql_server.get_friendly_name()}` has auditing enabled, but for less than 90 days of retention',
                    sql_server,
                    sql_server))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.sql_servers)
