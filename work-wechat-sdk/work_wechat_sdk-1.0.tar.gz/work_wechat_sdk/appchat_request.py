import json

from work_wechat_sdk import url_settings
from work_wechat_sdk.base_request import BaseRequest
from work_wechat_sdk.mixin import SendMessageMixin


class CreateAppChatRequest(BaseRequest):
    """
    Description: The response of CreateAppChatRequest contains a AppChat chatid
    detail information specified by name, owner, userlist

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: <userlist>
    post_data_O: <name>, <owner>, <chatid>

    Return: the chatid of app create json response

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90208
    """
    request_url = url_settings.CREATE_CHAT_URL

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    def create_chatid(self):
        chat = self.json_response.get("chatid", None)
        return chat


class UpdateAppChatRequest(BaseRequest):
    """
    Description: The response of UpdateAppChatRequest contains a AppChat chatid
    detail information specified by chatid

    parameter_R: <access_token>, <chatid>
    parameter_O: None

    post_data_R: <chatid>
    post_data_O: <name>, <owner>, <add_user_list>, <del_user_list>

    Return: the status of app update json response

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90246
    """
    request_url = url_settings.UPDATE_CHAT_URL

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method


class GetAppChatRequest(BaseRequest):
    """
    Description: The response of GetAppChatRequest contains a AppChat chatid
    detail information specified by chatid

    parameter_R: <access_token>, <chatid>
    parameter_O: None

    post_data_R: None
    post_data_O: None

    Return: the chat_info of app get json response

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90247
    """
    request_url = url_settings.GET_CHAT_URL

    def get_chat(self):
        chat = self.json_response.get("chat_info", None)
        return chat


class SendAppChatRequest(BaseRequest, SendMessageMixin):
    """
    Description: The response of GetAppChatRequest contains a AppChat chatid
    detail information specified by chatid

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: SendMessageMixin
    post_data_O: SendMessageMixin

    Return: the message status of app chat

    doc_links: https://open.work.weixin.qq.com/api/doc/90000/90135/90248
    """
    request_url = url_settings.SEND_CHAT_URL

    def __init__(self, chatid, **kwargs):
        """
        :param chatid: Group chat id
        """
        super().__init__(**kwargs)
        self.chatid = chatid
        self.message_extra = {}
        self._message = None

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    @property
    def message(self):
        self._message = {"chatid": self.chatid}
        if isinstance(self.message_extra, dict) and self.message_extra:
            self._message.update(self.message_extra)
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def send_message(self, msgtype, work):
        message = self.get_message(msgtype, work, **self.message)
        self.data = json.dumps(message)
        self.get_json_response()
