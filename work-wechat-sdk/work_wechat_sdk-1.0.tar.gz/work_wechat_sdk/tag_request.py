from work_wechat_sdk.base_request import BaseRequest
from work_wechat_sdk import url_settings


class CreateTagRequest(BaseRequest):
    """
    Description: Creates the tag and returns the tagID

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: <tagname>
    post_data_O: <tagid>

    Return: tagID
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90210
    """
    request_url = url_settings.CREATE_TAG_URL

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    def get_tagid(self):
        tagid = self.json_response.get("tagid")
        return tagid


class UpdateTagRequest(BaseRequest):
    """
    Description: Update Tag tagname

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: <tagid>, <tagname>
    post_data_O: None

    Return:
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90211
    """
    request_url = url_settings.UPDATE_TAG_URL

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method


class DelTagRequest(BaseRequest):
    """
    Description: Del Tag

    parameter_R: <access_token>, <tagid>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return:
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90212
    """
    request_url = url_settings.DELETE_TAG_URL


class GetTagRequest(BaseRequest):
    """
    Description: The response of GetTagRequest contains a tag
    detail information specified by tagid

    parameter_R: <access_token>, <tagid>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: a tag detail information specified by tagid
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90213
    """
    request_url = url_settings.GET_TAG_URL

    def get_tagname(self):
        tagname = self.json_response.get("tagname")
        return tagname

    def get_tag_partylist(self):
        partylist = self.json_response.get("partylist")
        return partylist

    def get_tag_users(self):
        tag_users = self.json_response.get("userlist")
        return tag_users

    def get_tag_username(self):
        tag_users = self.get_tag_users()
        usernames = [user.get("name") for user in tag_users]
        return usernames

    def get_tag_userid(self):
        tag_users = self.get_tag_users()
        userids = [user.get("userid") for user in tag_users]
        return userids


class AddTagUsersRequest(BaseRequest):
    """
    Description: Add Tag member's

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: <tagid>
    post_data_O: <userlist>, <partylist>

    Return: Failure a failure message is displayed
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90213
    """
    request_url = url_settings.ADD_TAG_USERS_URL

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    def invalid(self):
        invalidlist = self.json_response.get("invalidlist")
        invalidparty = self.json_response.get("invalidparty")
        errmsg = self.errmsg
        if invalidlist or invalidparty or errmsg == "all list invalid ":
            return {
                "invalidlist": invalidlist,
                "invalidparty": invalidparty,
                "errmsg": errmsg
            }
        else:
            return


class DelTagUsersRequest(BaseRequest):
    """
    Description: Del Tag member's

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: <tagid>
    post_data_O: <userlist>, <partylist>

    Return: Failure a failure message is displayed
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90215
    """
    request_url = url_settings.DEL_TAG_USERS_URL

    def request_method(self):
        self._request_method = "post"
        return self._request_method

    def invalid(self):
        invalidlist = self.json_response.get("invalidlist")
        invalidparty = self.json_response.get("invalidparty")
        errcode = self.json_response.get("errcode")
        if invalidlist or invalidparty:
            return {
                "invalidlist": invalidlist,
                "invalidparty": invalidparty,
                "errmsg": self.errmsg
            }
        elif errcode != 0:
            return {"errmsg": self.errmsg}


class TagListRequest(BaseRequest):
    """
    Description: The response of TagListRequest contains a Tag member's detail

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: a tag taglist detail information
    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90216
    """
    request_url = url_settings.TAG_LIST_URL

    def get_taglist(self):
        taglist = self.json_response.get("taglist")
        return taglist
