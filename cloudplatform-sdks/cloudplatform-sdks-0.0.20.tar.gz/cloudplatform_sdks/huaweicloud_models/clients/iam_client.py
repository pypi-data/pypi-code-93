from .client import HuaweiClient
from huaweicloudsdkiam.v3 import IamClient
from huaweicloudsdkiam.v3.region.iam_region import IamRegion


class HuaweiIamClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiIamClient, self).__init__(*args, **kwargs)

    @property
    def iam_client(self):
        return self.generate_client(IamClient, IamRegion)
