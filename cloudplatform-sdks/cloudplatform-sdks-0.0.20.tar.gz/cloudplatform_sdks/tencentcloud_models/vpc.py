from .clients import vpc_client


class TencentRouteTable:
    """
    {
        "VpcId": "vpc-7aurquzs",
        "RouteTableId": "rtb-rn9i0rcz",
        "RouteTableName": "route table test",
        "AssociationSet": [
          {
            "SubnetId": "subnet-b4sd9dkv",
            "RouteTableId": "rtb-bfnosqct"
          },
          {
            "SubnetId": "subnet-6g345d0x",
            "RouteTableId": "rtb-bfnosqct"
          }],
        "Main": false,
        "CreatedTime": "2021-06-30 10:04:41",
        "TagSet": [],
        "LocalCidrBlocks": [
          "192.168.12.0/24"
        ],
        "LocalCidrForCcn": [
          {
            "Cidr": "192.168.12.0/24",
            "PublishedToVbc": false
          }
        ],
        "RouteSet": [
          {
            "RouteId": 530604,
            "RouteItemId": "rti-rccr24d2",
            "RouteType": "USER",
            "DestinationCidrBlock": "11.0.0.0/24",
            "GatewayType": "EIP",
            "GatewayId": "0",
            "RouteDescription": "",
            "Enabled": true,
            "PublishedToVbc": false
          }
        ]
    }
    """

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def get(cls, id):
        lb_set = vpc_client.describe_route_table(RouteTableIds=[id]).get('RouteTableSet')
        if len(lb_set) == 0:
            return None
        else:
            return cls(lb_set[0])

    def fresh(self):
        self.obj = self.get(self.external_id).obj

    @classmethod
    def list(cls, ids=None):
        params = {}
        if ids:
            params['RouteTableIds'] = ids
        lb_set = vpc_client.describe_route_table(**params).get('RouteTableSet')
        return [cls(lb) for lb in lb_set]

    @classmethod
    def create(cls, **params):
        route_table_id = vpc_client.create_route_table(**params)
        return route_table_id

    def delete(self):
        vpc_client.delete_route_table(RouteTableId=self.external_id)

    def replace_subnet(self, subnet_id):
        return vpc_client.replace_route_table_associated_subnet(RouteTableId=self.external_id, SubnetId=subnet_id)

    @property
    def external_id(self):
        return self.obj.get('RouteTableId')

    @property
    def external_name(self):
        return self.obj.get('RouteTableName')

    @property
    def associated_subnets(self):
        res = []
        for association in self.obj.get('AssociationSet'):
            subnet = TencentSubnet.get(association['SubnetId'])
            res.append(subnet.attributes)
        return res

    @property
    def is_main(self):
        return self.obj.get('Main')

    @property
    def vpc_id(self):
        return self.obj.get('VpcId')

    @property
    def cidr(self):
        return self.obj.get('LocalCidrBlocks')

    @property
    def cidr_ror_ccn(self):
        return self.obj.get('LocalCidrForCcn')

    @property
    def route_entrys(self):
        res = []
        for _route_entry in self.obj.get('RouteSet'):
            route_entry = TencentRouteEntry(self.external_id, _route_entry)
            res.append(route_entry.attributes)
        return res

    @property
    def attributes(self):
        return {
            "status": "available",
            "external_id": self.external_id,
            "vpc_id": self.vpc_id,
            "vswitch_ids": self.associated_subnets,
            "route_entrys": self.route_entrys,
            "external_name": self.external_name,
        }

    def __repr__(self):
        return "<TencentRouteTable object:{}>".format(self.external_id)


class TencentRouteEntry:
    """
    {
        "RouteId": 530604, # route entry id
        "RouteItemId": "rti-rccr24d2", # route entry name
        "RouteType": "USER",
        "DestinationCidrBlock": "11.0.0.0/24",
        "GatewayType": "EIP",
        "GatewayId": "0",
        "RouteDescription": "",
        "Enabled": true,
        "PublishedToVbc": false
    }
    """

    def __init__(self, route_table_id, obj):
        self.obj = obj
        self.route_table_id = route_table_id

    @classmethod
    def list(cls, route_table_id):
        res = vpc_client.describe_route_entry(RouteTableIds=[route_table_id]).get('RouteTableSet')
        if not res:
            return None
        else:
            route_entrys = []
            for route_table in res:
                for route_entry in route_table.get('RouteSet'):
                    route_entrys.append(cls(route_table_id, route_entry))
            return route_entrys

    @classmethod
    def get(cls, route_table_id, route_entry_id):
        route_entries = cls.list(route_table_id)
        for route_entry in route_entries:
            if str(route_entry.external_id) == str(route_entry_id):
                return route_entry

    @classmethod
    def create(cls, **params):
        res = vpc_client.create_route_entry(**params)
        return res

    def delete(self, **kwargs):
        vpc_client.delete_route_entry(RouteTableId=self.route_table_id, Routes=[{"RouteId": self.external_id}])

    @property
    def external_id(self):
        return self.obj.get('RouteId')

    @property
    def external_name(self):
        return self.obj.get('RouteItemId')

    @property
    def type(self):
        return self.obj.get('RouteType')

    @property
    def cidr(self):
        return self.obj.get('DestinationCidrBlock')

    @property
    def next_hop_type(self):
        return self.obj.get('GatewayType')

    @property
    def next_hop_id(self):
        return self.obj.get('GatewayId')

    @property
    def description(self):
        return self.obj.get('RouteDescription')

    @property
    def is_enabled(self):
        return self.obj.get('Enabled')

    @property
    def attributes(self):
        return {
            'external_id': self.external_id,
            'type': self.type,
            'route_table_id': self.route_table_id,
            'description': self.description,
            'external_name': self.external_name,
            'next_hops': [
                {
                    "next_hop_type": self.next_hop_type,
                    "next_hop_id": self.next_hop_id
                }
            ],
            'destination_cidr_block': self.cidr,
            'status': 'available'
        }

    def __repr__(self):
        return "<TencentRouteEntry object:{}>".format(self.external_id)


class TencentSubnet:
    """
    {
        "NetworkAclId": "",
        "RouteTableId": "rtb-n0yr460a",
        "VpcId": "vpc-n0yr460a",
        "EnableBroadcast": false,
        "Zone": "ap-guangzhou",
        "Ipv6CidrBlock": "",
        "AvailableIpAddressCount": 1,
        "IsRemoteVpcSnat": false,
        "SubnetName": "子网1",
        "TotalIpAddressCount": 1,
        "IsCdcSubnet": 0,
        "CdcId": "cluster-1234dert",
        "TagSet": [
          {
            "Value": "ck",
            "Key": "kc"
          }
        ],
        "CreatedTime": "2020-05-25 20:09:07",
        "SubnetId": "subnet-bthucmmy",
        "CidrBlock": "10.0.0.0/16",
        "IsDefault": true
    }
    """

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def list(cls):
        res = vpc_client.describe_subnet().get('SubnetSet')
        if not res:
            return None
        else:
            return [cls(subnet) for subnet in res]

    @classmethod
    def get(cls, subnet_id):
        res = vpc_client.describe_subnet(SubnetIds=[subnet_id]).get('SubnetSet')
        if not res:
            return None
        else:
            return cls(res[0])

    @property
    def external_id(self):
        return self.obj.get("SubnetId")

    @property
    def external_name(self):
        return self.obj.get("SubnetName")

    @property
    def cidr(self):
        return self.obj.get("CidrBlock")

    @property
    def vpc_id(self):
        return self.obj.get("VpcId")

    @property
    def attributes(self):
        return {
            'external_id': self.external_id,
            'external_name': self.external_name,
            'cidr': self.cidr,
            'vpc_id': self.vpc_id,
            'status': 'available'
        }

    def __repr__(self):
        return "<TencentSubnet object: {}, attributes: {}>".format(self.external_id, self.attributes)
