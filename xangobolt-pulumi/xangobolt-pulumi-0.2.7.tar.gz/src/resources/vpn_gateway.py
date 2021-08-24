from pulumi import ResourceOptions
from pulumi.resource import CustomTimeouts
import pulumi_azure_native.network as network

def vpn_gateway(stem, subnet_id, depends_on=None):
    vpn_gw_pip = network.PublicIPAddress(
        f'vpngwpip-{stem}',
        resource_group_name=resource_group_name,
        sku=network.PublicIPAddressSkuArgs(
            name=network.PublicIPAddressSkuName.BASIC,
        ),
        public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    vpn_gw = network.VirtualNetworkGateway(
        f'vpngw-{stem}',
        resource_group_name=resource_group_name,
        sku=network.VirtualNetworkGatewaySkuArgs(
            name=network.VirtualNetworkGatewaySkuName.VPN_GW2,
            tier=network.VirtualNetworkGatewaySkuTier.VPN_GW2,
        ),
        gateway_type=network.VirtualNetworkGatewayType.VPN,
        vpn_type=network.VpnType.ROUTE_BASED,
        enable_bgp=True,
        ip_configurations=[network.VirtualNetworkGatewayIPConfigurationArgs(
            name=f'vpngwipcfg-{stem}',
            public_ip_address=network.PublicIPAddressArgs(
                id=vpn_gw_pip.id,
            ),
            subnet=network.SubnetArgs(
                id=subnet_id,
            ),
        )],
        tags=tags,
        opts=ResourceOptions(
            parent=self,
            depends_on=depends_on,
            custom_timeouts=CustomTimeouts(
                create='1h',
                update='1h',
                delete='1h',
            ),
        ),
    )
    return vpn_gw


def local_gateway(stem, onprem_gw_ip, addr_space, depends_on=None):
    local_gw = network.LocalNetworkGateway(
        f'lngw-{stem}',
        local_network_gateway_name = f'lngw-{stem}',
        gateway_ip_address = onprem_gw_ip,
        resource_group_name = resource_group_name,
        local_network_address_space=network.AddressSpaceArgs(
            address_prefixes=[addr_space],
        ),
        tags=tags,
        opts=ResourceOptions(
            parent=self,
            depends_on=depends_on,
        ),
    )
    return local_gw