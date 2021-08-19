from work_wechat_sdk import url_settings
from work_wechat_sdk.base_request import BaseRequest


class UserRequest(BaseRequest):
    """
    Description: The response of UserRequest contains a department member's
    detail information specified by userid

    parameter_R: <access_token>, <userid>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: a department member's detail information specified by userid

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90196
    """
    request_url = url_settings.GET_USER

    @property
    def userinfo_want_fields(self):
        wanted_fields = ["name", "mobile", "email", "external_position", "avatar"]
        return wanted_fields

    def get_userinfo(self):
        userinfo = {k: self.json_response.get(k, None) for k in self.userinfo_want_fields}
        return userinfo


class DeptUsersRequest(BaseRequest):
    """
    Description: The response of DeptUsersRequest contains a department member's
    detail information specified by department_id

    parameter_R: <access_token>, <department_id>
    parameter_O: <fetch_child>

    post_data_R: None
    post_data_O: None

    Return: a department member's detail information specified by department_id

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90201
    """
    request_url = url_settings.GET_DEPT_USERS

    def get_users(self):
        users = self.json_response.get("userlist", None)
        return users


class DeptUsersSimpleListRequest(BaseRequest):
    """
    Description: The response of DeptUsersSimpleListRequest contains a department member's
    detail information specified by department_id

    parameter_R: <access_token>, <department_id>
    parameter_O: <fetch_child>

    post_data_R: None
    post_data_O: None

    Return: a department member's detail information by department_id

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90200
    """
    request_url = url_settings.GET_DEPT_USERS_SIMPLE

    def get_users(self):
        users = self.json_response.get("userlist", None)
        return users


class UserIdToOpenIdRequest(BaseRequest):
    """
    Description: Obtain the OpenID from the userID

    parameter_R: <access_token>, <userid>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: openid.
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90202
    """
    request_url = url_settings.USERID_TO_OPENID

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    def get_openid(self):
        openid = self.json_response.get("openid")
        return openid


class OpenIdToUserIdRequest(BaseRequest):
    """
    Description: Obtain the userID from the OpenId

    parameter_R: <access_token>, <openid>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: openid.
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90202
    """
    request_url = url_settings.OPENID_TO_USERID

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    def get_userid(self):
        userid = self.json_response.get("userid")
        return userid
