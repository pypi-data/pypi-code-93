from abc import ABC, abstractmethod

from whizbang.domain.handler.app_registration_handler import IAppRegistrationHandler
from whizbang.domain.handler.bicep_handler import IBicepHandler
from whizbang.domain.handler.databricks_handler import IDatabricksHandler
from whizbang.domain.handler.keyvault_handler import IKeyVaultHandler
from whizbang.domain.handler.rbac_handler import IRbacHandler
from whizbang.domain.handler.sql_server_handler import ISqlServerHandler
from whizbang.domain.handler.storage_handler import IStorageHandler


class IHandlerFacade(ABC):
    """The HandlerFacade interface"""

    @property
    @abstractmethod
    def databricks_handler(self):
        """"""

    @property
    @abstractmethod
    def sql_server_handler(self) -> ISqlServerHandler:
        """"""

    @property
    @abstractmethod
    def rbac_handler(self):
        """"""

    @property
    @abstractmethod
    def bicep_handler(self):
        """"""

    @property
    @abstractmethod
    def keyvault_handler(self):
        """"""

    @property
    @abstractmethod
    def storage_handler(self):
        """"""

    @property
    @abstractmethod
    def app_registration_handler(self) -> IAppRegistrationHandler:
        """"""

class HandlerFacade(IHandlerFacade):
    def __init__(
            self,
            keyvault_handler: IKeyVaultHandler,
            bicep_handler: IBicepHandler,
            rbac_handler: IRbacHandler,
            sql_server_handler: ISqlServerHandler,
            databricks_handler: IDatabricksHandler,
            storage_handler: IStorageHandler,
            app_registration_handler: IAppRegistrationHandler
    ):
        self.__app_registration_handler = app_registration_handler
        self.__storage_handler = storage_handler
        self.__databricks_handler = databricks_handler
        self.__sql_server_handler = sql_server_handler
        self.__rbac_handler = rbac_handler
        self.__bicep_handler = bicep_handler
        self.__keyvault_handler = keyvault_handler

    @property
    def storage_handler(self): return self.__storage_handler

    @property
    def databricks_handler(self): return self.__databricks_handler

    @property
    def sql_server_handler(self): return self.__sql_server_handler

    @property
    def rbac_handler(self): return self.__rbac_handler

    @property
    def bicep_handler(self): return self.__bicep_handler

    @property
    def keyvault_handler(self): return self.__keyvault_handler

    @property
    def app_registration_handler(self): return self.__app_registration_handler
