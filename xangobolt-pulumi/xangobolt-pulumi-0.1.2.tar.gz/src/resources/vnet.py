from pulumi import ResourceOptions
import pulumi_azure_native.network as network

# Variables that may need to be injected before calling functions:
# vdc.location = props.location
# vdc.resource_group_name = props.resource_group_name
# vdc.s = props.separator
# vdc.self = self
# vdc.suffix = props.suffix
# vdc.tags = props.tags

def virtual_network(stem, address_spaces):
    vn = network.VirtualNetwork(
        f'vn-{stem}',
        virtual_network_name=f'vn-{stem}',
        resource_group_name=resource_group_name,
        address_space=network.AddressSpaceArgs(
            address_prefixes=address_spaces,
        ),
        tags=tags,
        opts=ResourceOptions(parent=self),
    )
    return vn


def vnet_peering(
        stem,
        rg,
        virtual_network_name,
        peer,
        remote_virtual_network_id,
        allow_forwarded_traffic=None,
        allow_gateway_transit=None,
        use_remote_gateways=None,
        depends_on=None,
):
    vnp = network.VirtualNetworkPeering(
        f'vnpr-{stem}',
        name=f'vnpr-{stem}',
        resource_group_name=rg,
        virtual_network_name=virtual_network_name,
        remote_virtual_network=network.SubResourceArgs(
            id=remote_virtual_network_id
        ),
        allow_forwarded_traffic=allow_forwarded_traffic,
        allow_gateway_transit=allow_gateway_transit,
        use_remote_gateways=use_remote_gateways,
        allow_virtual_network_access=True,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    return vnp


def subnet(
        stem,
        virtual_network_name,
        address_prefix,
        route_table_id,
        depends_on=None,
):
    sn = network.Subnet(
        f'sn-{stem}',
        name=f'sn-{stem}',
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=address_prefix,
        route_table=network.RouteTableArgs(
            id=route_table_id,
        ),
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    return sn

def subnet_special(
        stem,
        name,
        virtual_network_name,
        address_prefix,
        route_table_id,
        depends_on=None,
):
    sn = network.Subnet(
        f'sn-{stem}',
        name=name,
        subnet_name=name,
        resource_group_name=resource_group_name,
        virtual_network_name=virtual_network_name,
        address_prefix=address_prefix,
        route_table=network.RouteTableArgs(
            id=route_table_id,
        ),
        opts=ResourceOptions(
            parent=self,
            delete_before_replace=True,
            depends_on=depends_on,
        ),
    )
    return sn