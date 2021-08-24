import logging
import time

import jwt
from jwt import DecodeError

from shangqi_cloud_lib.context import config
from shangqi_cloud_lib.utils.MysqlUtil import SqlSession


def generate_session(key):
    headers = {
        'alg': "HS256",
    }
    jwt_token = jwt.encode({"from": key},
                           config.jwt_password,  # key
                           algorithm="HS256",
                           headers=headers
                           )
    if isinstance(jwt_token, bytes):
        jwt_token = jwt_token.decode('utf-8')
    return jwt_token

def generate_token(username, **kwargs):
    # payload
    key = username
    token_dict = {
        "iat": time.time(),  # fixed
        "exp": time.time(),
        "key": key,  # self-defined
    }
    if kwargs:
        token_dict["info"] = kwargs
    # headers
    headers = {
        'alg': "HS256",
    }
    jwt_token = jwt.encode(token_dict,
                           config.jwt_password,  # key
                           algorithm="HS256",
                           headers=headers
                           )
    if isinstance(jwt_token, bytes):
        jwt_token = jwt_token.decode('utf-8')
    logging.debug("generate jwt:{}".format(jwt_token))
    return jwt_token


# 解token
def decode_token(token):
    token_dict = {}
    try:
        token_dict = jwt.decode(token, config.jwt_password, leeway=config.leeway,
                                options={"verify_exp": config.leeway > 0}, algorithms=["HS256"])
    except DecodeError:
        logging.debug("decode jwt failed:{}".format(token))
    logging.debug("decode jwt:{}".format(token_dict.get("key","")))
    return token_dict


def auth(token, username=None):
    try:
        payload = decode_token(token)
        user_name = payload.get("key", "")
        if user_name == "cube":
            return True
        # 验证cookie 中的username
        if user_name != username:
            logging.debug("auth failed, illegal username:{} with payload user_name:{}".format(username, user_name))
            return False
        # 验证数据库
        # if len(config.user_table) > 0:
        #     user_info = SqlSession().query_one(
        #         "SELECT * FROM {} WHERE username = '{}'".format(config.user_table, user_name))
        #     if not user_info:
        #         return False
        return True
    except jwt.ExpiredSignatureError as e:
        logging.debug("auth failed")
    except jwt.exceptions.InvalidSignatureError as e:
        logging.debug("auth failed")
    logging.warning("get token in auth:<{}>".format(token))
    return False
