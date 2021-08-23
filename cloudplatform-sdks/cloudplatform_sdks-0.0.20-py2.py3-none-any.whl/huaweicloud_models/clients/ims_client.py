from .client import HuaweiClient
from huaweicloudsdkims.v2.region.ims_region import ImsRegion
from huaweicloudsdkims.v2 import ImsClient


class HuaweiImsClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiImsClient, self).__init__(*args, **kwargs)

    @property
    def ims_client(self):
        return self.generate_client(ImsClient, ImsRegion)
