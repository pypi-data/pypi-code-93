"""
Algorithm的操作模块
"""
import requests
from munch import Munch

from api.exceptions import ServiceInnerException, AuthException
from client import check_instance_avaliable, do_service

def get(code, actor_name):
    """
    获取Algorithm
    :param code:
    :param actor_name:
    :return: 如果这个Algorithm存在,返回Algorithm对象.否则返回空
    """
    check_instance_avaliable()

    try:
        r = do_service(f"/v1/algorithm/search", params = {"code" : code, "actorName": actor_name}, return_type="json")

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

def exists(code, actor_name):
    """
    获取Algorithm
    :param code:
    :param actor_name:
    :return: 如果这个Algorithm存在,返回True.否则返回False
    """
    check_instance_avaliable()

    try:
        r = do_service(f"/v1/algorithm/exists", params = {"code" : code, "actorName": actor_name})

        if r is not None:
            return r
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

def add(algoithm):
    """
    新增Algorithma
    :param algoithm对象
    :return: 如果添加失败,就抛出异常,否则无返回
    """
    if algoithm is None:
        return

    check_instance_avaliable()

    request = algoithm
    if isinstance(algoithm, Munch):
        # 说明是munch的,那么就转成Dict的
        request = algoithm.toDict()

    try:
        r = do_service(f"/v1/algorithm", method="post", data=request, return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e

def update(algoithm):
    """
    更新Algorithma
    :param algoithm对象
    :return: 如果添加失败,就抛出异常,否则无返回
    """
    if algoithm is None:
        return

    check_instance_avaliable()

    request = algoithm
    if isinstance(algoithm, Munch):
        # 说明是munch的,那么就转成Dict的
        request = algoithm.toDict()

    try:
        r = do_service(f"/v1/algorithm/update", method="put", data=request, return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
