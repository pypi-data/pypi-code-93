import json

from work_wechat_sdk import url_settings
from work_wechat_sdk.base_request import BaseRequest
from work_wechat_sdk.mixin import SendMessageMixin


class SendAppMessageRequest(BaseRequest, SendMessageMixin):
    """
    Description: The SendAppMessageRequest response contains information about the recipient

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: details of SendMessageMixin
    post_data_O: details of SendMessageMixin

    Return: a department list briefed

    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/90236
    """
    request_url = url_settings.SEND_MESSAGE_URL

    def __init__(self, touser=None, toparty=None, totag=None, agentid=None,
                 **kwargs):
        """
        :param touser: "UserID1|UserID2|UserID3"
        :param toparty: "PartyID1|PartyID2"
        :param totag: "TagID1 | TagID2"
        :param agentid: Enterprise application agentid
        Parameters touser, toparty, and totag cannot be empty at the same time
        """
        super().__init__(**kwargs)
        self.touser = touser
        self.toparty = toparty
        self.totag = totag
        self.agentid = agentid
        self.message_extra = {}
        self._message = None

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method

    @property
    def message(self):
        self._message = {"agentid": self.agentid}
        if self.touser is not None:
            self._message.update({"touser": self.touser})
        if self.toparty is not None:
            self._message.update({"toparty": self.toparty})
        if self.totag is not None:
            self._message.update({"totag": self.totag})
        if isinstance(self.message_extra, dict) and self.message_extra:
            self._message.update(self.message_extra)
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def send_message(self, msgtype, word):
        message = self.get_message(msgtype, word, **self.message)
        self.data = json.dumps(message)
        self.get_json_response()

    def get_msgid(self):
        msgid = self.json_response.get("msgid")
        return msgid

    def get_invalid(self):
        invaliduser = self.json_response.get("invaliduser")
        invalidparty = self.json_response.get("invalidparty")
        invalidtag = self.json_response.get("invalidtag")
        errcode = self.json_response.get("errcode")
        if invaliduser or invalidparty or invalidtag:
            return {
                "invaliduser": invaliduser,
                "invalidparty": invalidparty,
                "invalidtag": invalidtag,
                "errmsg": self.errmsg
            }
        elif errcode != 0:
            return {"errmsg": self.errmsg}


class RecallAppMessageRequest(BaseRequest):
    """
    Description: The RecallAppMessageRequest Withdraw the message of msgid

    parameter_R: <access_token>
    parameter_O: None

    post_data_R: <msgid>
    post_data_O: None

    Return:

    doc_links: https://work.weixin.qq.com/api/doc/90000/90135/94867
    """
    request_url = url_settings.RECALL_MESSAGE_URL

    @property
    def request_method(self):
        self._request_method = "post"
        return self._request_method
