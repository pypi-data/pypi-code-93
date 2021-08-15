from enum import Enum
from typing import List, Optional

from cloudrail.knowledge.context.azure.constants.azure_resource_type import AzureResourceType
from cloudrail.knowledge.context.azure.network_resource import NetworkResource


class OperatingSystemType(Enum):
    WINDOWS = 'Windows'
    LINUX = 'Linux'


class AzureVirtualMachine(NetworkResource):
    """
        Attributes:
            name: The name of this Public IP.
            network_interface_ids: A list of Network Interface ID's which are associated with the Virtual Machine.
            os_type: The VM's operating system. Either Windows or Linux.
    """
    def __init__(self, name: str, network_interface_ids: List[str], os_type: OperatingSystemType):
        super().__init__(AzureResourceType.AZURERM_VIRTUAL_MACHINE)
        self.name: str = name
        self.network_interface_ids: List[str] = network_interface_ids
        self.os_type: OperatingSystemType = os_type

    def get_keys(self) -> List[str]:
        return [self.get_id()]

    def get_cloud_resource_url(self) -> Optional[str]:
        return f'https://portal.azure.com/#@{self.tenant_id}/resource/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group_name}' \
               f'/providers/Microsoft.Compute/virtualMachines/{self.name}/overview'

    @property
    def is_tagable(self) -> bool:
        return True

    def get_type(self, is_plural: bool = False) -> str:
        return 'Virtual Machine' + ('s' if is_plural else '')
