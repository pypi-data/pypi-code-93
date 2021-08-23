from .client import HuaweiClient
from huaweicloudsdkevs.v2 import EvsClient, CreateVolumeRequest, ListVolumesRequest, ShowJobRequest, \
    DeleteVolumeRequest, ResizeVolumeRequest, ShowVolumeRequest
from huaweicloudsdkevs.v2.region.evs_region import EvsRegion


class HuaweiEvsClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiEvsClient, self).__init__(*args, **kwargs)

    @property
    def evs_client(self):
        return self.generate_client(EvsClient, EvsRegion)

    def create_volume(self, body_params=None):
        request = CreateVolumeRequest(body=body_params)
        return self.evs_client.create_volume(request)

    def delete_volume(self, volume_id=None):
        request = DeleteVolumeRequest(volume_id=volume_id)
        return self.evs_client.delete_volume(request)

    def describe_volume(self, volume_id=None):
        request = ListVolumesRequest(id=volume_id)
        return self.evs_client.list_volumes(request).volumes

    def show_volume(self, volume_id=None):
        request = ShowVolumeRequest(volume_id=volume_id)
        return self.evs_client.show_volume(request).volume

    def resize_volume(self, volume_id=None, body_params=None):
        request = ResizeVolumeRequest(volume_id=volume_id, body=body_params)
        return self.evs_client.resize_volume(request)

    def show_job(self, job_id=None):
        request = ShowJobRequest(job_id=job_id)
        return self.evs_client.show_job(request)
