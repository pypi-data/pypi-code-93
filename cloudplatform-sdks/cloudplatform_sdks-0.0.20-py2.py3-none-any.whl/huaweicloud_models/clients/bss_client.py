from .client import HuaweiClient
from huaweicloudsdkbss.v2 import BssClient
from huaweicloudsdkbss.v2.region.bss_region import BssRegion


class HuaweiBssClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiBssClient, self).__init__(*args, **kwargs)
        self.region = 'cn-north-1'

    @property
    def bss_client(self):
        return self.generate_global_client(BssClient, BssRegion)
