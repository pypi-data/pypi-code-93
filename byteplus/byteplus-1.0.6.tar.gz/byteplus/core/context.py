from byteplus.core.constant import _CN_HOSTS, _SG_HOSTS, _US_HOSTS, _AIR_HOSTS
from byteplus.core.region import Region


class Param(object):
    def __init__(self):
        self.tenant: str = ""
        self.tenant_id: str = ""
        self.token: str = ""
        self.retry_times: int = 0
        self.schema: str = "https"
        self.hosts: list = []
        self.headers: dict = {}
        self.region: Region = Region.UNKNOWN


class Context(object):
    def __init__(self, param: Param):
        self._check_required_field(param)
        self.tenant: str = param.tenant
        self.tenant_id: str = param.tenant_id
        self.token: str = param.token
        self.customer_headers: dict = param.headers
        self.schema: str = param.schema
        self.hosts: list = []
        self._adjust_hosts(param)

    @staticmethod
    def _check_required_field(param: Param) -> None:
        if len(param.tenant) == 0:
            raise Exception("Tenant is empty")
        if len(param.tenant_id) == 0:
            raise Exception("Tenant id is emtpy")
        if len(param.token) == 0:
            raise Exception("Token is empty")
        if param.region == Region.UNKNOWN:
            raise Exception("Region is empty")

    def _adjust_hosts(self, param: Param) -> None:
        if len(param.hosts) > 0:
            self.hosts = param.hosts
            return
        if param.region == Region.CN:
            self.hosts = _CN_HOSTS
            return
        if param.region == Region.US:
            self.hosts = _US_HOSTS
            return
        if param.region == Region.AIR:
            self.hosts = _AIR_HOSTS
