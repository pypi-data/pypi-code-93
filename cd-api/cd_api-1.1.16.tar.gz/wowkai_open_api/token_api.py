'''
@说明    :草动商城管理端取得token
@时间    :2020/3/8 下午6:25:59
@作者    :任秋锴
@版本    :1.0
'''
import requests
import time
import uuid
from urllib import request
from loguru import logger
import sqlite3


class Token:

    def __init__(self):
        pass

    def get(self, client_id, client_secret,
            grant_type="client_credentials", scope="all"):
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant_type,
            "scope": scope,
        }
        response_json = self.get_info(**data)
        logger.debug(data)
        logger.debug(response_json)
        token = response_json.get("data").get("access_token")
        logger.debug(f"access_token is {token}")
        return token

    def get_info(self, client_id, client_secret,
                 grant_type="client_credentials", scope="all"):
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant_type,
            "scope": scope,
        }
        url = "https://oauth.wowkai.cn/oauth2/token"
        response = requests.post(url, json=data)
        logger.debug(response)
        if response.status_code == 200:
            response_json = response.json()
            status_code = response_json.get('status_code')
            logger.debug(data)
            logger.debug(response_json)
            if status_code == 200:
                return response_json
