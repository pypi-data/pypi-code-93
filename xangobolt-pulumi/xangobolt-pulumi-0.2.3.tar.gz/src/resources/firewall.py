from pulumi import ResourceOptions
from pulumi.resource import CustomTimeouts
import pulumi_azure_native.network as network

def firewall(stem, fw_sn_id, fwm_sn_id, private_ranges, depends_on=None):
    fw_pip = network.PublicIPAddress(
        f'fwpip-{stem}',
        public_ip_address_name=f'fwpubip-{stem}',
        resource_group_name=resource_group_name,
        sku=network.PublicIPAddressSkuArgs(
            name=network.PublicIPAddressSkuName.STANDARD,
        ),
        public_ip_allocation_method='Static',
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    fwm_pip = network.PublicIPAddress(
        f'fwmpip-{stem}',
        public_ip_address_name=f'fwmpip-{stem}',
        resource_group_name=resource_group_name,
        sku=network.PublicIPAddressSkuArgs(
            name=network.PublicIPAddressSkuName.STANDARD,
        ),
        public_ip_allocation_method=network.IPAllocationMethod.STATIC,
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    fw = network.AzureFirewall(
        f'fw-{stem}',
        azure_firewall_name=f'fw-{stem}',
        resource_group_name=resource_group_name,
        additional_properties={
            "Network.SNAT.PrivateRanges": private_ranges,
        },
        sku=network.AzureFirewallSkuArgs(
            name='AZFW_VNet',  # TODO: this enum name is busted
            tier=network.AzureFirewallSkuTier.STANDARD,
        ),
        ip_configurations=[network.AzureFirewallIPConfigurationArgs(
            name=f'fwipcfg-{stem}',
            public_ip_address=network.PublicIPAddressArgs(
                id=fw_pip.id,
            ),
            subnet=network.SubnetArgs(
                id=fw_sn_id,
            ),
        )],
        management_ip_configuration=network.AzureFirewallIPConfigurationArgs(
            name=f'fwmipcfg-{stem}',
            public_ip_address=network.PublicIPAddressArgs(
                id=fwm_pip.id,
            ),
            subnet=network.SubnetArgs(
                id=fwm_sn_id,
            ),
        ),
        tags=tags,
        network_rule_collections=[network.AzureFirewallNetworkRuleCollectionArgs(
        action=network.AzureFirewallRCActionArgs(
            type="Allow",
        ),
        name="Client01_Firewall_Rules",
        priority=112,
        rules=[
            network.AzureFirewallNetworkRuleArgs(
                description="Permit RDP traffic based on source IPs and ports to VM",
                destination_addresses=["*"],
                destination_ports=[
                    "3389",
                ],
                name="Permit-RDP",
                protocols=["TCP"],
                source_addresses=["*"],
            ),
            network.AzureFirewallNetworkRuleArgs(
                description="Permit Unifi traffic based on source IPs and ports to onprem",
                destination_addresses=["*"],
                destination_ports=[
                    "443","8443","80",
                ],
                name="Permit-Unifi",
                protocols=["TCP"],
                source_addresses=["*"],
            ),
        ],
    )],
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
    return fw


