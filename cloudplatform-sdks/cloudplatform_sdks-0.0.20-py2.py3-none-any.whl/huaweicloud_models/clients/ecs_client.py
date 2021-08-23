from .client import HuaweiClient
from huaweicloudsdkecs.v2 import EcsClient, ListServersDetailsRequest, CreateServersRequest, BatchStopServersRequest, \
    BatchStartServersRequest, BatchRebootServersRequest, DeleteServersRequest, ShowJobRequest, \
    AttachServerVolumeRequest, DetachServerVolumeRequest, ResizeServerRequest, ListServerInterfacesRequest, \
    ShowServerRequest
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion


class HuaweiEcsClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiEcsClient, self).__init__(*args, **kwargs)

    @property
    def ecs_client(self):
        return self.generate_client(EcsClient, EcsRegion)

    def create_server(self, body_params=None):
        request = CreateServersRequest(body=body_params)
        return self.ecs_client.create_servers(request)

    def delete_server(self, body_params=None):
        request = DeleteServersRequest(body=body_params)
        return self.ecs_client.delete_servers(request)

    def start_server(self, body_params=None):
        request = BatchStartServersRequest(body=body_params)
        return self.ecs_client.batch_start_servers(request)

    def stop_server(self, body_params=None):
        request = BatchStopServersRequest(body=body_params)
        return self.ecs_client.batch_stop_servers(request)

    def reboot_server(self, body_params=None):
        request = BatchRebootServersRequest(body=body_params)
        return self.ecs_client.batch_reboot_servers(request)

    def resize_server(self, server_id, body_params=None):
        request = ResizeServerRequest(server_id=server_id, body=body_params)
        return self.ecs_client.resize_server(request)

    def describe_server(self, params={}):
        request = ListServersDetailsRequest(**params)
        return self.ecs_client.list_servers_details(request).servers

    def show_server(self, server_id=None):
        request = ShowServerRequest(server_id=server_id)
        return self.ecs_client.show_server(request).server

    def show_job(self, job_id=None):
        request = ShowJobRequest(job_id=job_id)
        return self.ecs_client.show_job(request)

    def attach_volume(self, server_id, body_params=None):
        request = AttachServerVolumeRequest(server_id=server_id, body=body_params)
        return self.ecs_client.attach_server_volume(request)

    def detach_volume(self, server_id, volume_id):
        request = DetachServerVolumeRequest(server_id=server_id, volume_id=volume_id)
        return self.ecs_client.detach_server_volume(request)

    def list_interfaces(self, server_id):
        request = ListServerInterfacesRequest(server_id=server_id)
        return self.ecs_client.list_server_interfaces(request)

