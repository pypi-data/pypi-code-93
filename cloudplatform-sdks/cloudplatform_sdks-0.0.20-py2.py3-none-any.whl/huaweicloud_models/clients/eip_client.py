from .client import HuaweiClient
from huaweicloudsdkeip.v2 import EipClient, CreatePublicipRequest, DeletePublicipRequest, ShowPublicipRequest, \
    UpdatePublicipRequest
from huaweicloudsdkeip.v2.region.eip_region import EipRegion


class HuaweiEipClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiEipClient, self).__init__(*args, **kwargs)

    @property
    def eip_client(self):
        return self.generate_client(EipClient, EipRegion)

    def create_eip(self, body_params=None):
        request = CreatePublicipRequest(body=body_params)
        return self.eip_client.create_publicip(request)

    def delete_eip(self, publicip_id=None):
        request = DeletePublicipRequest(publicip_id=publicip_id)
        return self.eip_client.delete_publicip(request)

    def describe_eip(self, publicip_id=None):
        request = ShowPublicipRequest(publicip_id=publicip_id)
        return self.eip_client.show_publicip(request).publicip

    def update_eip(self, publicip_id=None, body_params=None):
        request = UpdatePublicipRequest(publicip_id=publicip_id, body=body_params)
        return self.eip_client.update_publicip(request).publicip



