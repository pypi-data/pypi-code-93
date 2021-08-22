#coding: utf8
import requests
from farbox_bucket.utils.ssdb_utils import auto_cache_by_ssdb
from farbox_bucket.utils.env import get_env
from farbox_bucket.utils.functional import curry

WECHAT_APP_ID = get_env("wechat_app_id")
WECHAT_APP_SECRET = get_env("wechat_app_secret")


WECHAT_APP_ID2 = get_env("wechat_app_id2")
WECHAT_APP_SECRET2 = get_env("wechat_app_secret2")
# 一个微信的open id 看起来可能是这样的: oZ454jpVhF15nHxs3ig-uCq_gqss

API_PREFIX = 'https://api.weixin.qq.com/cgi-bin/'

# 每天最多 2000 次
def _get_access_token(is_chanel_2=False):
    app_id = WECHAT_APP_ID
    app_secret =  WECHAT_APP_SECRET
    if is_chanel_2:
        app_id = WECHAT_APP_ID2
        app_secret = WECHAT_APP_SECRET2
    if not app_id or not app_secret:
        return ""
    url = API_PREFIX + 'token'
    params = {'grant_type': 'client_credential', 'appid': app_id, 'secret': app_secret}
    response = requests.get(url,  params=params, verify=False)
    try:
        token = response.json().get('access_token')
    except:
        try: print(response.json().get("errmsg"))
        except: pass
        token = None
    return token

def get_access_token(force_update=False, is_chanel_2=False):
    # 7200s的有效期
    # # 一个小时更新一次
    key = "wechat_access_token"
    if is_chanel_2:
        key = "wechat_access_token2"
    func = curry(_get_access_token, is_chanel_2)
    return auto_cache_by_ssdb(key, value_func=func, ttl=3600, force_update=force_update)


def check_wechat_errors_and_update_token(json_data, is_chanel_2=False):
    if not json_data:
        return # ignore
    error_code = json_data.get("errcode")
    if error_code == 40001: # access_token失效了
        get_access_token(force_update=True, is_chanel_2=is_chanel_2)
