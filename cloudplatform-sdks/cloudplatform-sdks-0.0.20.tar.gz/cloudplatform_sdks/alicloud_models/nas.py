from .clients import nas_client


class AliNas:
    STATUS_MAPPER = {
        'Running': 'started',
        'Stopped': 'stopped',
        'Extending': 'configuring',
        'Stopping': 'stopping',
        'Deleting': 'deleting',
    }

    def __init__(self, nas_info):
        self.nas_info = nas_info

    @classmethod
    def create(cls, query_params=None):
        return nas_client.create_file_system(query_params).get('FileSystemId')

    @classmethod
    def get(cls, id):
        response = nas_client.describe_file_systems({"FileSystemId": id})
        if response:
            return cls(response['FileSystems']['FileSystem'][0])
        else:
            return None

    @classmethod
    def list(cls):
        response = nas_client.describe_file_systems()['FileSystems']['FileSystem']
        return [cls(nas_info) for nas_info in response]

    def delete(self):
        return nas_client.delete_file_system({"FileSystemId": self.external_id})

    @property
    def external_id(self):
        return self.nas_info.get('FileSystemId')

    @property
    def status(self):
        raw_status = self.nas_info.get('Status')
        return self.STATUS_MAPPER.get(self.nas_info.get('Status'), raw_status)

    @property
    def zone(self):
        return self.nas_info.get('ZoneId')

    @property
    def file_system_type(self):
        return self.nas_info.get('FileSystemType')

    @property
    def storage_type(self):
        return self.nas_info.get('StorageType')

    @property
    def protocol_type(self):
        return self.nas_info.get('ProtocolType')

    @property
    def charge_type(self):
        return self.nas_info.get('ChargeType')

    @property
    def capacity(self):
        return '{}(GB)'.format(self.nas_info.get('Capacity'))

    @property
    def mount_targets(self):
        response = nas_client.describe_mount_target({"FileSystemId": self.external_id})['MountTargets']['MountTarget']
        return [MountTarget(info, self.external_id) for info in response]

    @property
    def lifecycle_policies(self):
        response = nas_client.describe_lifecycle_policies({"FileSystemId": self.external_id})['LifecyclePolicies']
        return [LifeCyclePolicy(info) for info in response]

    @property
    def created_time(self):
        return self.nas_info.get('CreateTime').replace('CST', ' ').replace('T', ' ')

    def create_mount_target(self, query_params):
        query_params.update({
            "FileSystemId": self.external_id
        })
        return nas_client.create_mount_target(query_params)

    def delete_mount_target(self, query_params):
        query_params.update({
            "FileSystemId": self.external_id
        })
        return nas_client.delete_mount_target(query_params)

    def create_lifecycle_policy(self, query_params):
        query_params.update({
            "FileSystemId": self.external_id
        })
        return nas_client.create_lifecycle_policy(query_params)


class MountTarget:
    def __init__(self, target_info, nas_id):
        self.target_info = target_info
        self.nas_id = nas_id

    @property
    def status(self):
        return self.target_info.get('Status')

    @property
    def vpc_id(self):
        return self.target_info.get('VpcId')

    @property
    def vswitch_id(self):
        return self.target_info.get('VswId')

    @property
    def filesystem_id(self):
        return self.nas_id

    @property
    def mount_target_domain(self):
        return self.target_info.get('MountTargetDomain')

    @property
    def access_group(self):
        return self.target_info.get('DEFAULT_VPC_GROUP_NAME')

    def delete(self):
        return nas_client.delete_mount_target(
            {"MountTargetDomain": self.mount_target_domain, "FileSystemId": self.nas_id})


class LifeCyclePolicy:
    def __init__(self, raw_info):
        self.raw_info = raw_info

    @property
    def path(self):
        return self.raw_info.get('Path')

    @property
    def paths(self):
        return self.raw_info.get('Paths')

    @property
    def lifecycle_policy_name(self):
        return self.raw_info.get('LifecyclePolicyName')

    @property
    def lifecycle_rule_name(self):
        return self.raw_info.get('LifecycleRuleName')

    @property
    def created_time(self):
        return self.raw_info.get('CreateTime')

    @property
    def storage_type(self):
        return self.raw_info.get('StorageType')

    @property
    def filesystem_id(self):
        return self.raw_info.get('FileSystemId')

    def delete(self):
        nas_client.delete_lifecycle_policy(
            {'LifecyclePolicyName': self.lifecycle_policy_name, 'FileSystemId': self.filesystem_id})
