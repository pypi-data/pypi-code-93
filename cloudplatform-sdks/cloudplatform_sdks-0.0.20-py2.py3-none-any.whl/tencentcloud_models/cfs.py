from .clients import cfs_client


class TencentCfs:
    STATUS_MAPPER = {
        "available": "started"
    }

    def __init__(self, object):
        self.object = object
        self.mount_targets_list = None

    @classmethod
    def list(cls, **kwargs):
        resp = cfs_client.describe_cfs_file_systems(**kwargs)['FileSystems']
        return [cls(cfs_object) for cfs_object in resp]

    @classmethod
    def get(cls, id):
        resp = cfs_client.describe_cfs_file_systems(FileSystemId=id)['FileSystems']
        if len(resp) > 0:
            return cls(resp[0])
        else:
            return None

    @classmethod
    def create(cls, **kwargs):
        resp = cfs_client.create_cfs_file_system(**kwargs)
        return cls(resp)

    def fresh(self):
        self.object = self.get(self.external_id).object
        self.mount_targets_list = None

    def delete(self):
        return cfs_client.delete_cfs_file_system(FileSystemId=self.external_id)

    @property
    def external_id(self):
        return self.object.get('FileSystemId')

    @property
    def external_name(self):
        return self.object.get('FsName')

    @property
    def storage_type(self):
        return self.object.get('StorageType')

    @property
    def status(self):
        status = self.object.get('LifeCycleState')
        return self.STATUS_MAPPER.get(status, status)

    @property
    def storage_protocol(self):
        return self.object.get('Protocol')

    @property
    def zone(self):
        return self.object.get('Zone')

    @property
    def created_time(self):
        return self.object.get('CreationTime')

    @property
    def mount_targets(self):
        if self.mount_targets_list is None:
            mount_targets = cfs_client.describe_mount_targets(FileSystemId=self.external_id)['MountTargets']
            self.mount_targets_list = [CfsMountTarget(mount_target) for mount_target in mount_targets]
        return self.mount_targets_list

    def __repr__(self):
        return "<TencentCfs object:{}>".format(self.external_id)


class CfsMountTarget:
    def __init__(self, object_info):
        self.object_info = object_info

    @property
    def ip(self):
        return self.object_info.get('IpAddress')
