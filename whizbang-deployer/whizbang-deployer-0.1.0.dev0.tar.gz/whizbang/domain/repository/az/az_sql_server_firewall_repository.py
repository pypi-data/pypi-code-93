from abc import abstractmethod
from typing import List
from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.firewall_rule import FirewallRule
from whizbang.domain.models.sql.sql_server_resource import SqlServerResource
from whizbang.domain.repository.az.az_repository_base import IAzRepository, AzRepositoryBase

class IAzSqlServerFirewallRepository(IAzRepository):
    """"""

    @abstractmethod
    def create(self,sql_server: SqlServerResource,
                firewall_rule: FirewallRule):
        """"""

    @abstractmethod
    def delete(self, sql_server: SqlServerResource, firewall_rule_name: str):
        """"""

    @abstractmethod
    def list(self, sql_server: SqlServerResource) -> 'list[FirewallRule]':
        """"""

    @abstractmethod
    def show(self,sql_server: SqlServerResource) -> FirewallRule:
        """"""
class AzSqlServerFirewallRepository(AzRepositoryBase, IAzSqlServerFirewallRepository):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'sql server firewall-rule'

    def create(self, sql_server: SqlServerResource, firewall_rule: FirewallRule):
        # 'server' arg should is sql server resource name, not sql server domain
        result = self._execute(f'create'
                                f' --name {firewall_rule.name}'
                                f' --server {sql_server.resource_name}'
                                f' --resource-group {sql_server.resource_group_name}'
                                f' --end-ip-address {firewall_rule.end_ip_address}'
                                f' --start-ip-address {firewall_rule.start_ip_address}')

    # delete
    def delete(self, sql_server: SqlServerResource, firewall_rule_name: str):
        result = self._execute(f'delete '
                               f'--name {firewall_rule_name} '
                               f'--resource-group {sql_server.resource_group_name} '
                               f'--server {sql_server.resource_name}')

    # list
    def list(self, sql_server: SqlServerResource)->List[FirewallRule]:
        response = self._execute(f'list --name {sql_server.resource_name} --resource-group {sql_server.resource_group_name}')
        firewall_rules = []
        for item in response:
            firewall_rule = FirewallRule(
                name=item['name'],
                start_ip_address=item['startIpAddress'],
                end_ip_address=item['endIpAddress']
            )
            firewall_rules.append(firewall_rule)
        return firewall_rules

    # show
    def show(self, sql_server: SqlServerResource) -> FirewallRule:
        result = self._execute(f'show --name {sql_server.resource_name} --resource-group {sql_server.resource_group_name}')
        if result == None:
            return None
        return FirewallRule(
                name=result['name'],
                start_ip_address=result['startIpAddress'],
                end_ip_address=result['endIpAddress']
            )
