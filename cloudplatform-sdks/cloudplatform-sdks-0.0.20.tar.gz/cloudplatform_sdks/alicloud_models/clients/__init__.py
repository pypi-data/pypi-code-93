import importlib
from .cdn_client import CdnClient
from .nas_client import NasClient
from .dds_client import DdsClient
from proxy_tools import proxy

prod_mapper = {
    'cdn': CdnClient,
    'nas': NasClient,
    'dds': DdsClient
}


def get_current_client(prod):
    module = importlib.import_module('cloudplatform_auth')
    get_access_func = getattr(module, 'get_alicloud_access_info')
    access_key_id, access_key_secret, region = get_access_func()
    return prod_mapper[prod](access_key_id, access_key_secret, region)


@proxy
def cdn_client():
    return get_current_client('cdn')


@proxy
def nas_client():
    return get_current_client('nas')


@proxy
def dds_client():
    return get_current_client('dds')
