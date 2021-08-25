from abc import abstractmethod

from whizbang.domain.manager.az.az_manager_base import AzManagerBase, IAzManager
from whizbang.domain.models.firewall_rule import FirewallRule
from whizbang.domain.models.sql.sql_server_resource import SqlServerResource
from whizbang.domain.repository.az.az_sql_server_firewall_repository import IAzSqlServerFirewallRepository


class IAzSqlServerFirewallManager(IAzManager):
    """"""

    @abstractmethod
    def save(self, sql_server: SqlServerResource,
             firewall_rule: FirewallRule):
        """"""

    @abstractmethod
    def remove(self, sql_server: SqlServerResource,
               firewall_rule_name: str):
        """"""


class AzSqlServerFirewallManager(AzManagerBase, IAzSqlServerFirewallManager):
    def __init__(self, repository: IAzSqlServerFirewallRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: IAzSqlServerFirewallRepository = self._repository

    def save(self, sql_server: SqlServerResource, firewall_rule: FirewallRule):
        # todo: do we ignore if already exist
        if self._repository.show(sql_server) is not None:
            result = self._repository.delete(sql_server, firewall_rule_name=firewall_rule.name)
        result = self._repository.create(sql_server, firewall_rule)

    def remove(self, sql_server: SqlServerResource, firewall_rule_name: str):
        result = self._repository.delete(sql_server, firewall_rule_name=firewall_rule_name)
