from urllib.parse import quote_plus

from work_wechat_sdk.base_request import BaseRequest
from work_wechat_sdk import url_settings


class AccessTokenRequest(BaseRequest):
    """
    Description: The access token is globally valid within 7200 seconds. To get
    the token, two url parameters are necessary: corpid and corpsecret, by
    default, those should be contained in module url_settings.py

    parameter_R: <corpid>, <corpsecret>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: the access_token of work-wechat api.
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/91039
    """

    request_url = url_settings.GET_TOKEN

    def get_access_token(self):
        access_token = self.json_response.get("access_token")
        return access_token


class LoginUrl:
    """
    Description: Constructing the login link

    Return: the oauth2_url of work-qr_url api.
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/91022
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/91019
    """
    def __init__(self, appid=None, agentid=None, redirect_uri=None,
                 response_type="code", scope="snsapi_base", state=None, lang="zh"):
        self.appid = appid
        self.agentid = agentid
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.scope = scope
        self.state = state
        self.lang = lang

    def get_oauth2_url(self):
        if not all((self.appid, self.redirect_uri, self.response_type, self.scope)):
            raise BaseException("appid or redirect_uri or response_type or scope is None")
        params = {
            "appid": self.appid,
            "redirect_uri": quote_plus(self.redirect_uri),
            "response_type": self.response_type,
            "scope": self.scope
        }
        if self.state:
            params.update({"state": self.state})
        params_list = ["k=v".format(k, v) for k, v in params.items()]
        params_str = "&".join(params_list)

        oauth2_url = url_settings.OAUTH2_URL_ROOT + "?" + params_str + "#wechat_redirect"
        return oauth2_url

    def get_qr_url(self):
        if not all((self.appid, self.agentid, self.redirect_uri)):
            raise BaseException("appid or redirect_uri or agentid is None")

        params = {
            "appid": self.appid,
            "agentid": self.agentid,
            "redirect_uri": quote_plus(self.redirect_uri),
            "lang": self.lang
        }
        if self.state:
            params.update({"state": self.state})
        params_list = ["{k}={v}".format(k=k, v=v) for k, v in params.items()]
        params_str = "&".join(params_list)

        qr_url = url_settings.QR_URL_ROOT + "?" + params_str
        return qr_url


class UserInfoRequest(BaseRequest):
    """
    Description: The code provided by the login callback gets the
    userID or OpenID of the user

    parameter_R: <access_token>, <code>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: userID or OpenID.
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/91437
    """
    request_url = url_settings.USERINFO

    def get_userid(self):
        userid = self.json_response.get("UserId")
        return userid

    def get_openid(self):
        openid = self.json_response.get("OpenId")
        return openid
