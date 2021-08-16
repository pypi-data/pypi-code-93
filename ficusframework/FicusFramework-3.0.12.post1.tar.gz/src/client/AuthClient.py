"""
认证模块操作
"""
import requests
from munch import Munch

from api.exceptions import IllegalArgumentException
from client import do_service, check_instance_avaliable


def get_authorization_header(client_id, client_secret):
    import base64
    return 'Basic ' + str(base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')), encoding='utf-8')


def oauth_access_token(server, grant_type, client_id, client_secret, username, password):
    """
    获取oauth系统认证的accessToken
    :param client_id:
    :param client_secret:
    :return:
    """
    check_instance_avaliable()

    try:
        from urllib.parse import quote
        # url 中需要编码处理下，避免其中有特殊字符
        url = f"{server}/oauth/token?grant_type={quote(grant_type)}&scope=all&username={quote(str(username))}&password={quote(str(password))}"
        authorization = get_authorization_header(client_id, client_secret)

        r = requests.post(url, headers={"Authorization": authorization})

        if r is not None and r.status_code == 200:
            entity = Munch(r.json())

            from datetime import datetime
            import time
            return entity["access_token"], datetime.fromtimestamp(time.time() + entity["expires_in"])
        else:
            return None, None
    except requests.exceptions.HTTPError as ee:
        raise IllegalArgumentException(f"从ficus获取oauth签名失败,{ee.response.status_code}")


def oauth_jwt_token(user_name, user_password):
    """
    获取jwt的用户内容权限的jwtToken
    :param user_name:
    :param user_password:
    :return:
    """

    check_instance_avaliable()

    try:
        r = do_service("/user/login", method="POST", return_type="str",
                       data={"username": user_name, "password": user_password}, auth=None)

        if r is not None:
            jwt_token = r
            return (jwt_token, _find_expiration(jwt_token))
        else:
            return (None, None)
    except requests.exceptions.HTTPError as ee:
        raise IllegalArgumentException(f"从ficus获取用户认证失败,{ee.response.status_code}")


def _find_expiration(jwt_token: str):
    """
    解析jwtToken的过期时间
    :param jwt_token:
    :return:
    """

    # jwt有三部分,每个部分用逗号分隔.
    if jwt_token is None:
        return None

    splits = jwt_token.split(".")

    # 取第二部分
    s = splits[1]

    # 把第二部分用base64解码.
    import base64
    s1 = base64.b64decode(s)

    # 出来是一个map,取exp字段
    import json
    json_object = json.loads(s1)

    exp = json_object["exp"]

    from datetime import datetime
    return datetime.fromtimestamp(exp)
