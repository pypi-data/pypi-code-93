"""
针对FD的一些操作, 现已重构到 FactDatasourceProxyService.py 中
2020-09-16 16:21:26 sun 不得行, 还是需要
"""
import requests
from munch import Munch

from api.exceptions import ServiceInnerException, IllegalArgumentException, AuthException
from client import check_instance_avaliable, do_service


def fd(fd_code):
    """
    获取某一个FD对象
    :param fd_code: fd的唯一code
    :return: FD对象
    """
    check_instance_avaliable()

    try:
        r = do_service(f"/remote/fd-service/{fd_code}")

        if r is not None:
            return Munch(r)
        else:
            return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def exists_fds(fds):
    """
    判断fd是否存在
    :param fds:
    :return:
    """
    if fds is None:
        return False

    if not isinstance(fds, list):
        raise IllegalArgumentException("检测fd是否存在失败,输入参数不是一个list")

    check_instance_avaliable()

    try:
        r = do_service(f"/remote/fd-service/exists", method="post", data=fds,return_type = "bool")
        if r is not None:
            return bool(r)
        else:
            return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
