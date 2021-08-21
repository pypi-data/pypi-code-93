from ipaddress import ip_network, ip_address
from pulumi import ComponentResource, ResourceOptions, StackReference
from .hub import Hub
from ..resources import route_table, vnet, firewall, vpn_gateway, bastion_hosts

class SpokeProps:
    def __init__(
            self,
            azure_bastion: bool,
            fw_rt_name: str,
            hub: Hub,
            location: str,
            peer: str,
            reference: StackReference,
            resource_group_name: str,
            separator: str,
            spoke_address_space: str,
            subnets: [str, str, str],
            suffix: str,
            tags: [str, str],
            clientName: str,
            local_gw_ip: str,
            local_gw_space: str,
            env: str
    ):
        self.azure_bastion = azure_bastion
        self.fw_rt_name = fw_rt_name
        self.hub = hub
        self.location = location
        self.peer = peer
        self.reference = reference
        self.resource_group_name = resource_group_name
        self.separator = separator
        self.spoke_address_space = spoke_address_space
        self.subnets = subnets
        self.suffix = suffix
        self.tags = tags
        self.clientName = clientName
        self.local_gw_ip = local_gw_ip
        self.local_gw_space = local_gw_space
        self.env = env


class Spoke(ComponentResource):
    def __init__(self, name: str, props: SpokeProps,
                 opts: ResourceOptions = None):
        super().__init__('vdc:network:Spoke', name, {}, opts)

        spokeResources = [route_table, vnet, firewall, vpn_gateway, bastion_hosts]

        for resource in spokeResources:
            resource.location = props.location
            resource.resource_group_name = props.resource_group_name
            resource.s = props.separator
            resource.self = self
            resource.suffix = props.suffix
            resource.tags = props.tags
            resource.env = props.env

        # calculate the subnets in spoke_address_space
        spoke_nw = ip_network(props.spoke_address_space)
        if spoke_nw.prefixlen < 24:  # split evenly between subnets and hosts
            sub_diff = int((spoke_nw.max_prefixlen - spoke_nw.prefixlen) / 2)
        else:
            sub_diff = 27 - spoke_nw.prefixlen  # minimum /27 subnet
        subnets = spoke_nw.subnets(prefixlen_diff=sub_diff)
        next_sn = next(subnets)  # first subnet reserved for special uses
        first_sn = next_sn.subnets(new_prefix=27)  # subdivide if possible
        abs_nw = next(first_sn)  # AzureBastionSubnet /27 or greater

        # set the separator to be used in resource names
        s = props.separator

        # Azure Virtual Network to be peered to the hub
        spoke = vnet.virtual_network(name, [props.spoke_address_space])

        # VNet Peering from the hub to spoke
        hub_spoke = vnet.vnet_peering(
            stem=props.hub.stem,
            rg=props.hub.resource_group_name,
            virtual_network_name=props.hub.name,
            peer=name,
            remote_virtual_network_id=spoke.id,
            allow_gateway_transit=True,
            depends_on=[spoke, props.hub.vpn_gw],
        )

        # VNet Peering from spoke to the hub
        spoke_hub = vnet.vnet_peering(
            stem=name,
            rg=props.resource_group_name,
            virtual_network_name=spoke.name,
            peer=props.hub.stem,
            remote_virtual_network_id=props.hub.id,
            allow_forwarded_traffic=True,
            use_remote_gateways=True,  # requires at least one gateway
            depends_on=[spoke, props.hub.vpn_gw],
        )

        # Route Table to be associated with all ordinary spoke subnets
        spoke_rt = route_table.route_table(
            stem=f'{name}',
            disable_bgp_route_propagation=True,
        )
        # it is very important to ensure that there is never a route with an
        # address_prefix which covers the AzureFirewallSubnet, and as VNet
        # Peering may not be specified as next_hop_type, a separate address
        # space for the firewall in the hub makes for simpler routes
        for route in [
            (f'{name}{s}{props.env}{s}to-firewall', spoke_rt.name, props.local_gw_space),
            # (f'ss{s}{name}', props.hub.ss_rt_name, props.spoke_address_space),
            (f'{name}{s}dg', spoke_rt.name, '0.0.0.0/0'),
            (f'{name}{s}hub', spoke_rt.name, props.hub.address_space),
        ]:
            route_table.route_to_virtual_appliance(
                stem=route[0],
                route_table_name=route[1],
                address_prefix=route[2],
                next_hop_ip_address=props.hub.fw_ip,
            )
        # ordinary spoke subnets starting with the second subnet
        for subnet in props.subnets:
            next_sn = next(subnets)
            spoke_sn = vnet.subnet(
                stem=f'{name}{s}{subnet[0]}',
                virtual_network_name=spoke.name,
                address_prefix=str(next_sn),
                route_table_id=spoke_rt.id,
                depends_on=[spoke_rt, hub_spoke, spoke_hub],
            )

        # add route from firewall to corresponding spoke in peered stack
        if props.peer:
            peer_fw_ip = props.reference.get_output('fw_ip')
            peer_spoke_as = props.reference.get_output(f'{name}_as')
            fw_peer_spoke = route_table.route_to_virtual_appliance(
                stem=f'fw{s}{props.peer}{s}{name}',
                route_table_name=props.fw_rt_name,
                address_prefix=peer_spoke_as,
                next_hop_ip_address=peer_fw_ip,
            )

        # Create Local Gateway
        local_gw = vpn_gateway.local_gateway(
            stem=props.clientName,
            onprem_gw_ip=props.local_gw_ip,
            addr_space=props.local_gw_space,
            depends_on=[props.hub.vpn_gw],
        )

        # assign properties to spoke including from child resources
        self.address_space = props.spoke_address_space
        self.hub = props.hub.id
        self.id = spoke.id
        self.location = spoke.location
        self.name = spoke.name
        self.resource_group_name = props.resource_group_name
        self.subnets = spoke.subnets
        self.stem = name
        self.tags = props.tags
        self.register_outputs({})