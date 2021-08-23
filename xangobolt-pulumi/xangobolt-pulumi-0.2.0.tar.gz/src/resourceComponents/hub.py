from ipaddress import ip_network, ip_address
from pulumi import ComponentResource, ResourceOptions, StackReference
from resources import route_table, vnet, firewall, vpn_gateway, bastion_hosts


class Hub(ComponentResource):
    def __init__(self, name: str, props: None, opts: ResourceOptions = None):
        super().__init__('vdc:network:Hub', name, {}, opts)

        hubResources = [route_table, vnet, firewall, vpn_gateway, bastion_hosts]

        for resource in hubResources:
            resource.location = props.location
            resource.resource_group_name = props.resource_group_name
            resource.self = self
            resource.tags = props.tags

            
        # # calculate the subnets in the firewall_address_space
        fwz_nw = ip_network(props.firewall_address_space)
        fwz_sn = fwz_nw.subnets(new_prefix=25)  # two /26 subnets required
        fwx_nw = next(fwz_sn)  # for Azure Firewall and Management subnets
        fwz_sn = fwz_nw.address_exclude(fwx_nw)  # consolidate remainder
        dmz_nw = next(fwz_sn)  # largest remaining subnet for DMZ
        fwx_sn = fwx_nw.subnets(new_prefix=26)  # split the /25 into two /26
        fws_nw = next(fwx_sn)  # AzureFirewallSubnet
        fwm_nw = next(fwx_sn)  # AzureFirewallManagementSubnet

        # # calculate the subnets in the hub_address_space
        hub_nw = ip_network(props.hub_address_space)
        if hub_nw.prefixlen < 20:  # split evenly between subnets and hosts
            sub_diff = int((hub_nw.max_prefixlen - hub_nw.prefixlen) / 2)
        else:
            sub_diff = 25 - hub_nw.prefixlen  # minimum /25 subnet
        subnets = hub_nw.subnets(prefixlen_diff=sub_diff)
        next_sn = next(subnets)  # first subnet reserved for special uses
        first_sn = next_sn.subnets(new_prefix=26)  # split it into /26 subnets
        gws_nw = next(first_sn)  # GatewaySubnet /26
        rem_nw = next(first_sn)  # at least one more /26 subnet, perhaps more
        rem_sn = rem_nw.subnets(new_prefix=27)  # only need /27 save the rest
        abs_nw = next(rem_sn)  # AzureBastionSubnet /27 or greater

        # cast repeatedly referenced networks to strings
        dmz_ar = str(dmz_nw)
        gws_ar = str(gws_nw)

        # set the separator to be used in resource names
        s = props.separator

        # Azure Virtual Network to which spokes will be peered
        # separate address spaces to simplify custom routing
        hub = vnet.virtual_network(
            f'Hub', 
            [
                #props.firewall_address_space,
                props.hub_address_space,
            ],)

        # AzureFirewallManagementSubnet and Route Table
        # https://docs.microsoft.com/en-us/azure/firewall/forced-tunneling
        hub_fwm_rt = route_table.route_table(
            stem=f'firewall-mgmt',
            disable_bgp_route_propagation=True,  # required
        )

        # only a default route to the Internet is permitted
        hub_fwm_dg = route_table.route_to_internet(
            stem=f'firewall_mgmt-internet',
            route_table_name=hub_fwm_rt.name,
        )

        hub_fwm_sn = vnet.subnet_special(
            stem=f'firewall-mgmt',
            name='AzureFirewallManagementSubnet',  # name required
            virtual_network_name=hub.name,
            address_prefix='172.16.1.0/24',
            route_table_id=hub_fwm_rt.id,
            depends_on=[hub, hub_fwm_rt, hub_fwm_dg],
        )

        # AzureFirewallSubnet Route Table 
        hub_fw_rt = route_table.route_table(
            stem=f'firewall',
            disable_bgp_route_propagation=False,
        )

        # default route either direct to Internet or forced tunnel
        # turn off SNAT if the next_hop_ip_address is public
        # https://docs.microsoft.com/en-us/azure/firewall/snat-private-range
        private_ranges = 'IANAPrivateRanges'
        if not props.forced_tunnel:
            hub_fw_dg = route_table.route_to_internet(
                stem=f'firewall-internet',
                route_table_name=hub_fw_rt.name,
            )
        else:
            hub_fw_dg = route_table.route_to_virtual_appliance(
                stem=f'firewall-tunnel',
                route_table_name=hub_fw_rt.name,
                address_prefix='0.0.0.0/0',
                next_hop_ip_address=props.forced_tunnel,
            )
            ft_ip = ip_address(props.forced_tunnel)
            if not ft_ip.is_private:
                private_ranges = '0.0.0.0/0'

        
        hub_fw_sn = vnet.subnet_special(
            stem=f'firewall',
            name='AzureFirewallSubnet',  # name required
            virtual_network_name=hub.name,
            address_prefix='172.16.2.0/24',
            route_table_id=hub_fw_rt.id,
            depends_on=[hub, hub_fw_rt, hub_fw_dg],
        )

        # Azure Firewall
        hub_fw = firewall.firewall(
            stem=f'Hub',
            fw_sn_id=hub_fw_sn.id,
            fwm_sn_id=hub_fwm_sn.id,
            private_ranges=private_ranges,
            depends_on=[hub_fw_sn, hub_fwm_sn],
        )

        # wait for the private ip address of the firewall to become available
        hub_fw_ip = hub_fw.ip_configurations.apply(
            lambda ipc: ipc[0].private_ip_address
        )

        # It is very important to ensure that there is never a route with an
        # address_prefix which covers the AzureFirewallSubnet.


        # GatewaySubnet and Route Table
        hub_gw_rt = route_table.route_table(
            stem=f'Hub',
            disable_bgp_route_propagation=False,
            depends_on=None,
        )

        # protect intra-GatewaySubnet traffic from being redirected:
        hub_gw_gw = route_table.route_to_virtual_network(
            stem=f'Hub',
            route_table_name=hub_gw_rt.name,
            address_prefix=gws_ar,
        )

        # redirect traffic from gateways to hub via firewall
        hub_gw_hub = route_table.route_to_virtual_appliance(
            stem=f'Hub',
            route_table_name=hub_gw_rt.name,
            address_prefix=props.hub_address_space,
            next_hop_ip_address=hub_fw_ip,
        )

        # Create gateway Subnet
        hub_gw_sn = vnet.subnet_special(
            stem=f'gateway',
            name='GatewaySubnet',  # name required
            virtual_network_name=hub.name,
            address_prefix='172.16.3.0/24',
            route_table_id=hub_gw_rt.id,
            depends_on=[hub_gw_rt, hub_gw_gw, hub_gw_hub],
        )

        # Create VPN Gateway
        hub_vpn_gw = vpn_gateway.vpn_gateway(
            stem='Hub',
            subnet_id=hub_gw_sn.id,
            depends_on=[hub_gw_sn],
        )

         # Route Table to be associated with all hub shared services subnets
        hub_ss_rt = route_table.route_table(
            stem=f'shared-services',
            disable_bgp_route_propagation=True,
            depends_on=[hub_vpn_gw],
        )

        # default route from hub via the firewall
        hub_ss_dg = route_table.route_to_virtual_appliance(
            stem=f'shared-srv-inet',
            route_table_name=hub_ss_rt.name,
            address_prefix='0.0.0.0/0',
            next_hop_ip_address=hub_fw_ip,
        )

        # redirect traffic from hub to gateways via the firewall
        hub_ss_gw = route_table.route_to_virtual_appliance(
            stem=f'shared-srv-gw',
            route_table_name=hub_ss_rt.name,
            address_prefix=gws_ar,
            next_hop_ip_address=hub_fw_ip,
        )
        # shared services subnets starting with the second subnet
        for subnet in props.subnets:
            next_sn = next(subnets)
            hub_sn = vnet.subnet(  # ToDo add NSG
                stem=f'{name}{s}{subnet[0]}',
                virtual_network_name=hub.name,
                address_prefix=str(next_sn),
                route_table_id=hub_ss_rt.id,
                depends_on=[hub_ss_rt, hub_ss_dg, hub_ss_gw],
            )


        # Azure Bastion subnet and host (optional)
        if props.azure_bastion:
            hub_ab = bastion_hosts.bastion_host(
                stem='Hub',
                virtual_network_name=hub.name,
                address_prefix='172.16.4.0/24',
                depends_on=[hub_vpn_gw],
            )


        # VNet Peering between stacks using StackReference (optional)
        if props.peer:
            peer_hub_id = props.reference.get_output('hub_id')
            # VNet Peering (Global) in one direction from stack to peer
            hub_hub = vnet.vnet_peering(
                stem=props.stack,
                virtual_network_name=hub.name,
                peer=props.peer,
                remote_virtual_network_id=peer_hub_id,
                allow_forwarded_traffic=True,
                allow_gateway_transit=False,  # as both hubs have gateways
            )
            # need to invalidate system routes created by VNet Peering
            peer_fw_ip = props.reference.get_output('fw_ip')
            peer_hub_as = props.reference.get_output('hub_as')

            for route in [
                (f'gw{s}{props.peer}{s}hub', hub_gw_rt.name, peer_hub_as),
                (f'ss{s}{props.peer}{s}hub', hub_ss_rt.name, peer_hub_as),
            ]:
                vnet.route_to_virtual_appliance(
                    stem=route[0],
                    route_table_name=route[1],
                    address_prefix=route[2],
                    next_hop_ip_address=peer_fw_ip,
                )

                

        
        # assign properties to hub including from child resources
        self.address_space = props.hub_address_space  # used for routes to the hub
        self.dmz_ar = dmz_ar  # used for routes to the hub
        #self.dmz_rt_name = hub_dmz_rt.name  # used to add routes to spokes
        #self.er_gw = hub_er_gw  # needed prior to VNet Peering from spokes
        self.fw = hub_fw  # needed prior to VNet Peering from spokes
        self.fw_ip = hub_fw_ip  # used for routes to the hub
        self.fw_rt_name = hub_fw_rt.name  # used for route to the peered spokes
        self.gw_rt_name = hub_gw_rt.name  # used to add routes to spokes
        self.id = hub.id  # exported and used for stack and spoke peering
        self.location = hub.location  # informational
        self.name = hub.name  # exported and used for spoke peering
        self.peer = props.peer  # informational
        self.resource_group_name = props.resource_group_name  # informational
        self.subnets = hub.subnets  # informational
        self.stack = props.stack  # informational
        self.stem = name  # used for VNet Peering from spokes
        self.ss_rt_name = hub_ss_rt.name  # used to add routes to spokes
        self.tags = props.tags  # informational
        self.vpn_gw = hub_vpn_gw  # needed prior to VNet Peering from spokes
        self.register_outputs({})