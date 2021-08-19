"""
This module contain the global settings for the python sdk of work-wechat
"""
# The login url
OAUTH2_URL_ROOT = "https://open.weixin.qq.com/connect/oauth2/authorize"

QR_URL_ROOT = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

# The root url of work-wechat api
URL_ROOT = "https://qyapi.weixin.qq.com/"

# The access token should be got from the url below
# Attention: be care the limits of this api

GET_TOKEN = URL_ROOT + "cgi-bin/gettoken"


# User management

USER_ROOT = URL_ROOT + "cgi-bin/user/"

USERINFO = USER_ROOT + "getuserinfo"

GET_USER = USER_ROOT + "get"

GET_DEPT_USERS = USER_ROOT + "list"

GET_DEPT_USERS_SIMPLE = USER_ROOT + "simplelist"

USERID_TO_OPENID = USER_ROOT + "convert_to_openid"

OPENID_TO_USERID = USER_ROOT + "convert_to_userid"


# Department management

DEPT_ROOT = URL_ROOT + "cgi-bin/department/"

GET_DEPT = DEPT_ROOT + "list"


# Tag management

TAG_ROOT = URL_ROOT + "cgi-bin/tag/"

CREATE_TAG_URL = TAG_ROOT + "create"

UPDATE_TAG_URL = TAG_ROOT + "update"

DELETE_TAG_URL = TAG_ROOT + "delete"

GET_TAG_URL = TAG_ROOT + "get"

ADD_TAG_USERS_URL = TAG_ROOT + "addtagusers"

DEL_TAG_USERS_URL = TAG_ROOT + "deltagusers"

TAG_LIST_URL = TAG_ROOT + "list"


# AppChat management

CHAT_ROOT = URL_ROOT + "cgi-bin/appchat/"

CREATE_CHAT_URL = CHAT_ROOT + "create"

UPDATE_CHAT_URL = CHAT_ROOT + "update"

GET_CHAT_URL = CHAT_ROOT + "get"

SEND_CHAT_URL = CHAT_ROOT + "send"


# Message management

MESSAGE_ROOT = URL_ROOT + "cgi-bin/message/"

SEND_MESSAGE_URL = MESSAGE_ROOT + "send"

RECALL_MESSAGE_URL = MESSAGE_ROOT + "recall"
