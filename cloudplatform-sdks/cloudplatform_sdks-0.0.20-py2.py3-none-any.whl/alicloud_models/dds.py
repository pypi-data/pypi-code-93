from .clients import dds_client


class AliMongoDB:
    """
    {
        "ResourceGroupId": "rg-acfm3pn7sq4lmbi",
        "CapacityUnit": "",
        "DBInstanceType": "replicate",
        "ReplicaSetName": "mgset-53918086",
        "StorageEngine": "WiredTiger",
        "ReplicaSets": {
            "ReplicaSet": [
                {
                    "ReplicaSetRole": "Primary",
                    "ConnectionDomain": "dds-uf6c4138204c35741.mongodb.rds.aliyuncs.com",
                    "VPCCloudInstanceId": "dds-uf6c4138204c3574-1",
                    "ConnectionPort": "3717",
                    "VPCId": "vpc-uf61k6rtpscoyyvgnm790",
                    "NetworkType": "VPC",
                    "VSwitchId": "vsw-uf66i29mnlov86tk29kem"
                },
                {
                    "ReplicaSetRole": "Secondary",
                    "ConnectionDomain": "dds-uf6c4138204c35742.mongodb.rds.aliyuncs.com",
                    "VPCCloudInstanceId": "dds-uf6c4138204c3574-2",
                    "ConnectionPort": "3717",
                    "VPCId": "vpc-uf61k6rtpscoyyvgnm790",
                    "NetworkType": "VPC",
                    "VSwitchId": "vsw-uf66i29mnlov86tk29kem"
                }
            ]
        },
        "MaintainEndTime": "22:00Z",
        "DBInstanceId": "dds-uf6c4138204c3574",
        "MongosList": {
            "MongosAttribute": []
        },
        "NetworkType": "VPC",
        "DBInstanceStorage": 10,
        "DBInstanceDescription": "mongodbname",
        "MaintainStartTime": "18:00Z",
        "Engine": "MongoDB",
        "Tags": {
            "Tag": []
        },
        "DBInstanceReleaseProtection": false,
        "EngineVersion": "4.2",
        "DBInstanceStatus": "NET_CREATING",
        "ZoneId": "cn-shanghai-b",
        "MaxConnections": 500,
        "ReadonlyReplicas": "0",
        "ReplicationFactor": "3",
        "VPCId": "vpc-uf61k6rtpscoyyvgnm790",
        "DBInstanceClass": "dds.mongo.mid",
        "VSwitchId": "vsw-uf66i29mnlov86tk29kem",
        "ShardList": {
            "ShardAttribute": []
        },
        "LockMode": "Unlock",
        "MaxIOPS": 8000,
        "ChargeType": "PostPaid",
        "VpcAuthMode": "Close",
        "ProtocolType": "mongodb",
        "CurrentKernelVersion": "mongodb_20210625_4.0.18",
        "CreationTime": "2021-07-15T01:18:01Z",
        "ConfigserverList": {
            "ConfigserverAttribute": []
        },
        "RegionId": "cn-shanghai",
        "KindCode": 0
    }
    """

    def __init__(self, object):
        self.object = object

    @classmethod
    def get(cls, db_id):
        res = dds_client.get_DB_instance_attribute({"DBInstanceId": db_id})
        dbs = res['DBInstances'].get('DBInstance')
        if dbs:
            return cls(dbs[0])
        return None

    def fresh(self):
        self.object = self.get(self.external_id).object

    @classmethod
    def list(cls, params):
        res = dds_client.list_DB_instance(params)
        dbs = res['DBInstances'].get('DBInstance') or []
        return [cls.get(db['DBInstanceId']) for db in dbs]

    @classmethod
    def create(cls, params):
        res = dds_client.create(params)
        return res.get("DBInstanceId")

    def delete(self):
        return dds_client.delete({"DBInstanceId": self.external_id})

    def get_netwokr_address(self):
        res = dds_client.describe_sharding_network_address({"DBInstanceId": self.external_id})
        return res['NetworkAddresses'].get('NetworkAddress')

    def get_available_resource(self, params):
        res = dds_client.get_available_resource(params)
        db_type = res.get('SupportedDBTypes', {}).get('SupportedDBType') or []
        return db_type

    def allocate_public_network_address(self):
        return dds_client.allocate_public_network_address({"DBInstanceId": self.external_id})

    def release_public_network_address(self):
        return dds_client.release_public_network_address({"DBInstanceId": self.external_id})

    def modify_security_ips(self, ip):
        res = dds_client.get_security_ips({"DBInstanceId": self.external_id})
        groups = res['SecurityIpGroups'].get('SecurityIpGroup') or []
        ips = ""
        for group in groups:
            if group['SecurityIpGroupName'] == 'default':
                ips = group['SecurityIpList']
                break
        params = {
            "DBInstanceId": self.external_id,
            "SecurityIps": ips + ',' + ip
        }
        return dds_client.modify_security_ips(params)

    @property
    def connection_info(self):
        res = dds_client.get_sharding_network_address({"DBInstanceId": self.external_id})
        cons = res['NetworkAddresses'].get('NetworkAddress') or []
        return [AliMongoDBAddress(con).attributes for con in cons]

    @property
    def public_address(self):
        connection_info = self.connection_info
        for connection in connection_info:
            if connection.get("network_type") == "Public" and connection.get("role") == "Primary":
                return connection.get("network_address")

    @property
    def security_ips(self):
        res = dds_client.get_security_ips({"DBInstanceId": self.external_id})
        groups = res['SecurityIpGroups'].get('SecurityIpGroup') or []
        ips = []
        for group in groups:
            ips.append(group['SecurityIpList'])
        return ",".join(ips)

    @property
    def external_id(self):
        return self.object.get('DBInstanceId')

    @property
    def external_name(self):
        return self.object.get('DBInstanceDescription')

    @property
    def resource_group_id(self):
        return self.object.get('ResourceGroupId')

    @property
    def db_instance_type(self):
        return self.object.get('DBInstanceType')

    @property
    def replica_set_name(self):
        return self.object.get('ReplicaSetName')

    @property
    def storage_engine(self):
        return self.object.get('StorageEngine')

    @property
    def replica_sets(self):
        res = self.object.get('ReplicaSets', {}).get('ReplicaSet') or []
        return [AliMongoDBReplica(replicas).attributes for replicas in res]

    @property
    def network_type(self):
        return self.object.get('NetworkType')

    @property
    def storage(self):
        return self.object.get('DBInstanceStorage')

    @property
    def engine(self):
        return self.object.get('Engine')

    @property
    def protection(self):
        return self.object.get('DBInstanceReleaseProtection')

    @property
    def engine_version(self):
        return self.object.get('EngineVersion')

    @property
    def status(self):
        """
        Creating, Running, NET_CREATING
        """
        return str(self.object.get('DBInstanceStatus', 'lost')).lower()

    @property
    def zone_id(self):
        return self.object.get('ZoneId')

    @property
    def max_connections(self):
        return self.object.get('MaxConnections')

    @property
    def readonly_replicas(self):
        return self.object.get('ReadonlyReplicas')

    @property
    def replication_factor(self):
        return self.object.get('ReplicationFactor')

    @property
    def vpc_id(self):
        return self.object.get('VPCId')

    @property
    def db_instance_class(self):
        return self.object.get('DBInstanceClass')

    @property
    def vswitch_id(self):
        return self.object.get('VSwitchId')

    @property
    def lock_mode(self):
        return self.object.get('LockMode')

    @property
    def max_IOPS(self):
        return self.object.get('MaxIOPS')

    @property
    def charge_type(self):
        return self.object.get('ChargeType')

    @property
    def vpc_auth_mode(self):
        return self.object.get('VpcAuthMode')

    @property
    def protocol_type(self):
        return self.object.get('ProtocolType')

    @property
    def current_kernel_version(self):
        return self.object.get('CurrentKernelVersion')

    @property
    def region_id(self):
        return self.object.get('RegionId')

    @property
    def kind_code(self):
        return self.object.get('KindCode')

    @property
    def attributes(self):
        return {
            "external_id": self.external_id,
            "external_name": self.external_name,
            "resource_group_id": self.resource_group_id,
            "db_instance_type": self.db_instance_type,
            "replica_set_name": self.replica_set_name,
            "storage_engine": self.storage_engine,
            "replica_sets": self.replica_sets,
            "storage": self.storage,
            "network_type": self.network_type,
            "engine": self.engine,
            "protection": self.protection,
            "engine_version": self.engine_version,
            "status": self.status,
            "zone_id": self.zone_id,
            "max_connections": self.max_connections,
            "readonly_replicas": self.readonly_replicas,
            "replication_factor": self.replication_factor,
            "vpc_id": self.vpc_id,
            "db_instance_class": self.db_instance_class,
            "vswitch_id": self.vswitch_id,
            "lock_mode": self.lock_mode,
            "max_IOPS": self.max_IOPS,
            "charge_type": self.charge_type,
            "vpc_auth_mode": self.vpc_auth_mode,
            "protocol_type": self.protocol_type,
            "current_kernel_version": self.current_kernel_version,
            "region_id": self.region_id,
            "kind_code": self.kind_code,
            "connection_info": self.connection_info,
            "public_address": self.public_address,
            "security_ips": self.security_ips
        }

    def __repr__(self):
        return "<AliMongoDB object:{}>".format(self.external_id)


class AliMongoDBReplica:
    """
    {
        "ReplicaSetRole": "Primary",
        "ConnectionDomain": "dds-uf6c4138204c35741.mongodb.rds.aliyuncs.com",
        "VPCCloudInstanceId": "dds-uf6c4138204c3574-1",
        "ConnectionPort": "3717",
        "VPCId": "vpc-uf61k6rtpscoyyvgnm790",
        "NetworkType": "VPC",
        "VSwitchId": "vsw-uf66i29mnlov86tk29kem"
    }
    """

    def __init__(self, object):
        self.object = object

    @property
    def replica_set_role(self):
        return self.object.get('ReplicaSetRole')

    @property
    def connection_domain(self):
        return self.object.get('ConnectionDomain')

    @property
    def kind_code(self):
        return self.object.get('KindCode')

    @property
    def vpc_cloud_instance_id(self):
        return self.object.get('VPCCloudInstanceId')

    @property
    def external_id(self):
        return self.object.get('VPCCloudInstanceId')

    @property
    def external_name(self):
        return self.object.get('VPCCloudInstanceId')

    @property
    def connection_port(self):
        return self.object.get('ConnectionPort')

    @property
    def vpc_id(self):
        return self.object.get('VPCId')

    @property
    def network_type(self):
        return self.object.get('NetworkType')

    @property
    def vswitch_id(self):
        return self.object.get('VSwitchId')

    @property
    def attributes(self):
        return {
            "replica_set_role": self.replica_set_role,
            "connection_domain": self.connection_domain,
            "kind_code": self.kind_code,
            "vpc_cloud_instance_id": self.vpc_cloud_instance_id,
            "external_id": self.external_id,
            "external_name": self.external_name,
            "connection_port": self.connection_port,
            "vpc_id": self.vpc_id,
            "network_type": self.network_type,
            "vswitch_id": self.vswitch_id,
        }

    def __repr__(self):
        return "<AliMongoDBReplica object:{}>".format(self.external_id)


class AliMongoDBAddress:
    """
    {
        "Role": "Primary",
        "NetworkAddress": "dds-uf6c4138204c35741.mongodb.rds.aliyuncs.com",
        "VPCId": "vpc-uf61k6rtpscoyyvgnm790",
        "NetworkType": "VPC",
        "Port": "3717",
        "IPAddress": "192.168.100.138",
        "VswitchId": "vsw-uf66i29mnlov86tk29kem"
    }
    """

    def __init__(self, object):
        self.object = object

    @property
    def role(self):
        return self.object.get('Role')

    @property
    def network_address(self):
        return self.object.get('NetworkAddress')

    @property
    def vpc_id(self):
        return self.object.get('VPCId')

    @property
    def network_type(self):
        return self.object.get('NetworkType')

    @property
    def port(self):
        return self.object.get('Port')

    @property
    def ip_address(self):
        return self.object.get('IPAddress')

    @property
    def vswitch_id(self):
        return self.object.get('VswitchId')

    @property
    def attributes(self):
        return {
            "role": self.role,
            "network_address": self.network_address,
            "vpc_id": self.vpc_id,
            "network_type": self.network_type,
            "port": self.port,
            "ip_address": self.ip_address,
            "vswitch_id": self.vswitch_id,
        }

    def __repr__(self):
        return "<AliMongoDB object:{}>".format(self.object)
