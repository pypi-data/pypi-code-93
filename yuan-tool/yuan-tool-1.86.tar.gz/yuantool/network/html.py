import requests
import logging
from requests.models import Response

logger = logging.getLogger(__name__)


class BaseMSG:
    @classmethod
    def msg(cls, res, **kwargs):
        """
        新修改判断逻辑，对于已有字段若更新为None则不更新
        :keyword enforce_update: bool 是否强制更新
               e.g. MSG.Success(code=None)
                    <<< {'code': 0, 'msg': '成功'}
                    MSG.Success(code=None,enforce_update=True)
                    <<< {'code': None, 'msg': '成功'}
        """
        # 修改写法，不接受更新参数为None的值
        if 'enforce_update' in kwargs and kwargs['enforce_update']:
            kwargs.pop('enforce_update')
            res.update(kwargs)
        else:
            res.update((k, v) for k, v in kwargs.items() if (k not in res) or v)
        return res


# def change_user_agent():
#     from fake_useragent import UserAgent
#     ua = UserAgent()
#     session.headers['User-Agent'] = ua.random
#     session.headers['X-forwarded-for'] = '49.49.49.49'


def safe_requests(url, method, session=None, **kwargs):
    # change_user_agent()
    try:
        if session:
            res = session.request(url=url, method=method, **kwargs)
        else:
            res = requests.request(url=url, method=method, **kwargs)
        return res
    except Exception as e:
        if 'Failed to establish a new connection:' in str(e):
            logger.warning(e)
        else:
            logger.warning(e, exc_info=True)
        return str(e)


def _check_whos_guo(url, res):
    """去识别谁的锅"""
    if isinstance(res, str):
        if 'Failed to establish a new connection:' in res:
            logger.warning('无法访问url: {}'.format(url))
        else:
            logger.warning('访问 {} 发生意外错误 {}'.format(url, res))
    else:
        logger.warning("访问 {} 返回状态码 {}\n文本内容为 {}".format(res.url, res.status_code, res.text))


def get_html(url, session=None):
    res = safe_requests(url, session=session, method='GET')
    if isinstance(res, Response):
        if res.status_code == 200:
            return res.text
    return False


def get_cookie(url, session=None):
    res = safe_requests(url, session=None, method='GET')
    return res.cookies


def post_data(url, data, session=None, encode='utf-8', check_whos_guo=False):
    """以字符串形式发送数据"""
    res = safe_requests(url, session=session, method='POST', data=str(data).encode(encode))
    if isinstance(res, Response):
        if res.status_code == 200:
            return res

    if check_whos_guo:
        _check_whos_guo(url, res)
    return False


def post_json_data(url, data, session=None, check_whos_guo=False):
    """以json形式发送数据"""
    if isinstance(data, dict):
        pass
    else:
        if not isinstance(data, list):
            data = [data]
        data = dict(enumerate(data))

    res = safe_requests(url, session=session, method='POST', json=data)
    if isinstance(res, Response):
        if res.status_code == 200:
            return res

    if check_whos_guo:
        _check_whos_guo(url, res)
    return False


def post_body_json_data(url, data, session=None, check_whos_guo=False):
    """以json形式发送数据,数据会放在body中,这是漏扫后台可以接收的数据格式"""
    import json
    res = safe_requests(url, session=session, method='POST',
                        data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                        headers={'Content-Type': 'application/json'})
    if isinstance(res, Response):
        if res.status_code == 200:
            return res
    if check_whos_guo:
        _check_whos_guo(url, res)
    return False


def get(url, session=None, **kwargs):
    return safe_requests(url, session=session, method='GET', **kwargs)


def post(url, session=None, **kwargs):
    return safe_requests(url, session=session, method='POST', **kwargs)


def get_title(body):
    """
    根据页面源码返回标题
    :param body: <title>sss</title>
    :return: sss
    """
    import re
    result = ''
    title_patten = re.compile(rb'<title>([^<]{1,200})</title>', re.I)
    title = title_patten.findall(body)
    if len(title) > 0:
        try:
            result = title[0].decode("utf-8")
        except Exception as e:
            result = title[0].decode("gbk", errors="replace")
    return result.strip()


def get_headers(conn: requests.Response):
    # version 字段目前只能是10或者11
    raw = conn.raw
    version = "1.1"
    if raw.version == 10:
        version = "1.0"

    first_line = "HTTP/{} {} {}\n".format(version, raw.status, raw.reason)

    headers = str(raw._fp.headers)

    headers = headers.strip()
    if not conn.headers.get("Content-Length"):
        headers = "{}\nContent-Length: {}".format(headers, len(conn.content))

    return first_line + headers
