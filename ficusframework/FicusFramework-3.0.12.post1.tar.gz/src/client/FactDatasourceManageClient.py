import requests
from munch import Munch
from api.exceptions import ServiceInnerException, IllegalArgumentException, AuthException
from client import check_instance_avaliable, do_service


def get(site, project_code, code):
    """
    获取事实库的定义
    :param site:
    :param project_code:
    :param code:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"/remote/fd-service-manage/{site}/{project_code}/{code}")

        if r is not None:
            return Munch(r)
        else:
            return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500 and e.response.status_code != 404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
