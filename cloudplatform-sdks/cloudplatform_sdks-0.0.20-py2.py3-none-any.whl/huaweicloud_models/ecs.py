import time
from .clients import hw_ecs_client


class HuaweiEcs:
    STATE_AVAILABLE = 'ACTIVE'
    STATE_STARTED = 'started'
    STATE_STOPPED = 'SHUTOFF'
    JOB_STATE_SUCCESS = 'SUCCESS'
    JOB_STATE_FAIL = 'FAIL'
    PORT_STATE_AVAILABLE = 'ACTIVE'

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def name(self):
        return self.object.name

    @property
    def status(self):
        return self.object.status.lower()

    @property
    def flavor(self):
        return self.object.flavor

    @property
    def availability_zone(self):
        return self.object.os_ext_a_zavailability_zone

    @property
    def metadata(self):
        return self.object.metadata

    @property
    def addresses(self):
        return self.object.addresses

    @property
    def volumes(self):
        return self.object.os_extended_volumesvolumes_attached

    @classmethod
    def list(cls, params={}):
        instances = hw_ecs_client.describe_server(params)
        return [cls(instance) for instance in instances]

    @classmethod
    def get(cls, instance_id=None):
        instances = hw_ecs_client.describe_server()
        if not instances:
            return
        for instance in instances:
            if instance.id == instance_id:
                return cls(instance)

    @classmethod
    def create(cls, params=None):
        create_response = hw_ecs_client.create_server(body_params=params)
        if not create_response:
            return
        return create_response.server_ids[0]

    def delete(self):
        params = {
            "servers": [{
                "id": self.id
            }]
        }
        return hw_ecs_client.delete_server(body_params=params)

    @classmethod
    def start(cls, params=None):
        return hw_ecs_client.start_server(body_params=params).job_id

    @classmethod
    def stop(cls, params=None):
        return hw_ecs_client.stop_server(body_params=params).job_id

    @classmethod
    def reboot(cls, params=None):
        return hw_ecs_client.reboot_server(body_params=params).job_id

    @classmethod
    def resize(cls, server_id=None, params=None):
        return hw_ecs_client.resize_server(server_id=server_id, body_params=params).job_id

    @classmethod
    def show_job(cls, job_id):
        return hw_ecs_client.show_job(job_id=job_id)

    @classmethod
    def attach(cls, instance_id=None, params=None):
        return hw_ecs_client.attach_volume(instance_id, body_params=params).job_id

    @classmethod
    def detach(cls, server_id=None, volume_id=None):
        return hw_ecs_client.detach_volume(server_id, volume_id).job_id

    @classmethod
    def wait_job_complete(cls, job_id, target_state=(JOB_STATE_SUCCESS, JOB_STATE_FAIL),
                          timeout=600, sleep_interval=10):
        timeout = time.time() + timeout
        job_state = ""
        while time.time() < timeout:
            job_info = cls.show_job(job_id)
            job_state = job_info.status
            if isinstance(target_state, tuple):
                if job_state in target_state:
                    if job_state == cls.JOB_STATE_FAIL:
                        raise Exception("fail job")
                    return
            time.sleep(sleep_interval)
        raise Exception("Waiting for server to be target state failed! the current state is {0}, "
                        "the target state is {1}".format(job_state, target_state))

    def interfaces(self):
        return hw_ecs_client.list_interfaces(self.id).interface_attachments

    def available_port(self):
        interfaces = hw_ecs_client.list_interfaces(self.id).interface_attachments
        for interface in interfaces:
            if interface.port_state == self.PORT_STATE_AVAILABLE:
                return interface.port_id
        return
