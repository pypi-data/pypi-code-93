import ipaddress
from typing import List, Union
from typing_extensions import Literal
from net_templates.filters import BaseFilter
from net_models.models import models_map
import json
import jmespath


class AnsibleFilters(BaseFilter):
    """
    Helper class that mimics some of the Ansible built in filters.

    """

    def ipaddr(self, ip_address: Union[ipaddress.IPv4Address, ipaddress.IPv4Interface, ipaddress.IPv4Network, ipaddress.IPv6Address, ipaddress.IPv6Interface, ipaddress.IPv6Network], operation: str = None):
        address = None
        for func in [ipaddress.ip_address, ipaddress.ip_interface, ipaddress.ip_network]:
            if address is None:
                try:
                    address = func(ip_address)
                    print(func)
                except Exception as e:
                    pass
        if operation is None:
            if address:
                return True
            else:
                return False
        if operation == "address":
            if isinstance(address, (ipaddress.IPv4Interface, ipaddress.IPv6Interface)):
                return str(address.ip)
            elif isinstance(address, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
                return str(address)
        elif operation == "netmask":
            if isinstance(address, (ipaddress.IPv4Interface, ipaddress.IPv6Interface)):
                return str(address.with_netmask).split("/")[1]
        raise ValueError("Invalid IP Given")

    def json_query(self, data: Union[list, dict], query: str):
        return jmespath.search(query, data)

    def str_to_obj(self, string: str):
        return eval(string)

    def to_json(self, data: Union[list, dict]) -> str:
        return json.dumps(data)

    def type_debug(self, var) -> str:
        return str(type(var))
