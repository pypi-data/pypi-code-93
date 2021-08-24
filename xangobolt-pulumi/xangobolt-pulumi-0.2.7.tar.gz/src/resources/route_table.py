from pulumi import ResourceOptions
from pulumi.resource import CustomTimeouts
import pulumi_azure_native.resources as resources
import pulumi_azure_native.network as network


# Variables that may need to be injected before calling functions:
# vdc.location = props.location
# vdc.resource_group_name = props.resource_group_name
# vdc.s = props.separator
# vdc.self = self
# vdc.suffix = props.suffix
# vdc.tags = props.tags

def route_table(stem, disable_bgp_route_propagation=None, depends_on=None):
    rt = network.RouteTable(
        f'rt-{stem}',
        resource_group_name=resource_group_name,
        disable_bgp_route_propagation=disable_bgp_route_propagation,
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    return rt


def route_to_internet(stem, route_table_name):
    r_i = network.Route(
        f'r-{stem}-i',
        route_name='FirewallDefaultRoute',  # name required
        resource_group_name=resource_group_name,
        address_prefix='0.0.0.0/0',
        next_hop_type=network.RouteNextHopType.INTERNET,
        route_table_name=route_table_name,
        opts=ResourceOptions(parent=self, delete_before_replace=True),
    )
    return r_i


def route_to_virtual_appliance(
        stem,
        route_table_name,
        address_prefix,
        next_hop_ip_address,
):
    r_va = network.Route(
        f'r-{stem}-va',
        resource_group_name=resource_group_name,
        address_prefix=address_prefix,
        next_hop_type=network.RouteNextHopType.VIRTUAL_APPLIANCE,
        next_hop_ip_address=next_hop_ip_address,
        route_table_name=route_table_name,
        opts=ResourceOptions(parent=self),
    )
    return r_va


def route_to_virtual_network(stem, route_table_name, address_prefix):
    r_vn = network.Route(
        f'r-{stem}-vn',
        resource_group_name=resource_group_name,
        address_prefix=address_prefix,
        next_hop_type=network.RouteNextHopType.VNET_LOCAL,
        route_table_name=route_table_name,
        opts=ResourceOptions(parent=self),
    )
    return r_vn