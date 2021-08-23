from pulumi import ResourceOptions
import pulumi_azure_native.network as network


def bastion_host(stem, virtual_network_name, address_prefix, depends_on=None):

    # This subnet config needs to be moved over to the Vnet resource
    ab_sn = network.Subnet(
        f'bhpi-{stem}',
        resource_group_name=resource_group_name,
        name='AzureBastionSubnet',
        virtual_network_name=virtual_network_name,
        address_prefix=address_prefix,
        opts=ResourceOptions(
            parent=self,
            delete_before_replace=True,
            depends_on=depends_on,
        ),
    )
    ab_pip = network.PublicIPAddress(
        f'bhpip-{stem}',
        resource_group_name=resource_group_name,
        sku=network.PublicIPAddressSkuArgs(
            name=network.PublicIPAddressSkuName.STANDARD,
        ),
        public_ip_allocation_method=network.IPAllocationMethod.STATIC,
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    ab = network.BastionHost(
        f'bh-{stem}',
        resource_group_name=resource_group_name,
        ip_configurations=[network.BastionHostIPConfigurationArgs(
            name=f'bhipcfg{stem}',
            public_ip_address=network.PublicIPAddressArgs(
                id=ab_pip.id,
            ),
            subnet=network.SubnetArgs(
                id=ab_sn.id,
            ),
        )],
        tags=tags,
        opts=ResourceOptions(parent=self, depends_on=depends_on),
    )
    return ab