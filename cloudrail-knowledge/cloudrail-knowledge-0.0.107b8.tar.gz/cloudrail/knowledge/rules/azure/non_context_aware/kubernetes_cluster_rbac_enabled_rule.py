from typing import List, Dict

from cloudrail.knowledge.context.azure.azure_environment_context import AzureEnvironmentContext
from cloudrail.knowledge.rules.azure.azure_base_rule import AzureBaseRule
from cloudrail.knowledge.rules.base_rule import Issue
from cloudrail.knowledge.rules.rule_parameters.base_paramerter import ParameterType


class KubernetesClusterRbacEnabledRule(AzureBaseRule):

    def get_id(self) -> str:
        return 'non_car_kubernetes_cluster_rbac_enabled'

    def execute(self, env_context: AzureEnvironmentContext, parameters: Dict[ParameterType, any]) -> List[Issue]:
        issues: List[Issue] = []
        for kubernetes_cluster in env_context.kubernetes_cluster:
            if not kubernetes_cluster.enable_rbac:
                issues.append(
                    Issue(
                        f'The managed Kubernetes cluster `{kubernetes_cluster.get_friendly_name()}` does not have RBAC enabled.', kubernetes_cluster, kubernetes_cluster))
        return issues

    def should_run_rule(self, environment_context: AzureEnvironmentContext) -> bool:
        return bool(environment_context.kubernetes_cluster)
