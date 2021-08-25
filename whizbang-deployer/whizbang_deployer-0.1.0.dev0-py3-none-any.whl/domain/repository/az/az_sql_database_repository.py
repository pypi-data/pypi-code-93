from abc import abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.sql.sql_database_resource import SqlDatabaseResource
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository, AzResourceRepositoryBase
from whizbang.domain.shared_types.sql_connection_client_type import SqlConnectionClientType


class IAzSqlDatabaseRepository(IAzResourceRepository):
    """"""

    @abstractmethod
    def get_connection_string(self,
                              database: SqlDatabaseResource,
                              client_type: str = SqlConnectionClientType.ado_net,
                              auth_type: str = 'SqlPassword'
                              ) -> str:
        """"""


class AzSqlDatabaseRepository(AzResourceRepositoryBase, IAzSqlDatabaseRepository):
    def __init__(self, context: AzCliContext):
        AzResourceRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'sql dw'

    def create(self, resource: SqlDatabaseResource):
        raise NotImplementedError

    def get_connection_string(self,
                              database: SqlDatabaseResource,
                              client_type: str = SqlConnectionClientType.ado_net,
                              auth_type: str = 'SqlPassword'
                              ) -> str:
        result = self._execute(f'--client {client_type}'
                      f' --auth-type {auth_type}'
                      f' --server {database.server}'
                      f' --name {database.resource_name}')
        return result

