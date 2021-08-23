import time
from .clients import hw_evs_client


class HuaweiEvs:
    STATE_AVAILABLE = 'available'
    STATE_INUSE = 'in-use'
    JOB_STATE_SUCCESS = 'SUCCESS'
    JOB_STATE_FAIL = 'FAIL'

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
        return self.object.status

    @property
    def volume_type(self):
        return self.object.volume_type

    @property
    def availability_zone(self):
        return self.object.availability_zone

    @property
    def size(self):
        return self.object.size

    @property
    def attach_instance(self):
        attachments = self.object.attachments
        if not attachments:
            return
        return attachments[0].server_id

    @classmethod
    def get(cls, volume_id=None):
        volume = hw_evs_client.show_volume(volume_id)
        if not volume:
            return
        return cls(volume)

    @classmethod
    def create(cls, params=None):
        create_response = hw_evs_client.create_volume(body_params=params)
        if not create_response:
            return
        return create_response.job_id

    def delete(self):
        delete_response = hw_evs_client.delete_volume(volume_id=self.id)
        if not delete_response:
            return
        return delete_response.job_id

    def resize(self, new_size=None):
        params = {
            "os-extend": {
                "new_size": new_size
            }
        }
        resize_response = hw_evs_client.resize_volume(volume_id=self.id, body_params=params)
        if not resize_response:
            return
        return resize_response.job_id

    @classmethod
    def show_job(cls, job_id):
        return hw_evs_client.show_job(job_id=job_id)

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
                    return job_info
            time.sleep(sleep_interval)
        raise Exception("Waiting for server to be target state failed! the current state is {0}, "
                        "the target state is {1}".format(job_state, target_state))
