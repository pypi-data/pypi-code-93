import importlib
from proxy_tools import proxy
from .ecs_client import HuaweiEcsClient
from .eip_client import HuaweiEipClient
from .evs_client import HuaweiEvsClient
from .iam_client import HuaweiIamClient
from .ims_client import HuaweiImsClient
from .vpc_client import HuaweiVpcClient
from .bss_client import HuaweiBssClient
prod_mapper = {
    'ecs': HuaweiEcsClient,
    'eip': HuaweiEipClient,
    'evs': HuaweiEvsClient,
    'iam': HuaweiIamClient,
    'ims': HuaweiImsClient,
    'vpc': HuaweiVpcClient,
    'bss': HuaweiBssClient
}


def get_current_client(prod):
    module = importlib.import_module('cloudplatform_auth')
    get_access_func = getattr(module, 'get_huaweicloud_access_info')
    access_key_id, access_key_secret, region = get_access_func()
    return prod_mapper[prod](access_key_id, access_key_secret, region)


@proxy
def hw_ecs_client():
    return get_current_client('ecs')


@proxy
def hw_eip_client():
    return get_current_client('eip')


@proxy
def hw_evs_client():
    return get_current_client('evs')


@proxy
def hw_iam_client():
    return get_current_client('iam')


@proxy
def hw_ims_client():
    return get_current_client('ims')


@proxy
def hw_vpc_client():
    return get_current_client('vpc')


@proxy
def hw_bss_client():
    return get_current_client('bss')
