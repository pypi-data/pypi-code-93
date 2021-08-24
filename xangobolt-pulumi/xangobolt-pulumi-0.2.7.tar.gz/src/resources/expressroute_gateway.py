from pulumi import ResourceOptions
from pulumi.resource import CustomTimeouts
import pulumi_azure_native.network as network

def expressroute_gateway(stem, subnet_id, depends_on=None):
    er_gw_pip = network.PublicIPAddress(
        f'ergwpip-{stem}',
        resource_group_name=resource_group_name,
        public_ip_allocation_method=network.IPAllocationMethod.DYNAMIC,
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    er_gw = network.VirtualNetworkGateway(
        f'ergw-{stem}',
        resource_group_name=resource_group_name,
        sku=network.VirtualNetworkGatewaySkuArgs(
            name=network.VirtualNetworkGatewaySkuName.STANDARD,
            tier=network.VirtualNetworkGatewaySkuTier.STANDARD,
        ),
        gateway_type=network.VirtualNetworkGatewayType.EXPRESS_ROUTE,
        vpn_type=network.VpnType.ROUTE_BASED,
        enable_bgp=True,
        ip_configurations=[network.VirtualNetworkGatewayIPConfigurationArgs(
            name=f'ergwipcfg-{stem}',
            public_ip_address=network.PublicIPAddressArgs(
                id=er_gw_pip.id,
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
    return er_gw