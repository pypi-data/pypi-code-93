# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: Contém os métodos para autenticação
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.:

    Author:           @diego.yosiura
    Last Update:      21/07/2021 14:56
    Created:          21/07/2021 14:56
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
import os

from json import loads
from json import dumps
from datetime import datetime
from datetime import timedelta

from .. import Configuration
from .. import RequestManager


class User:
    request = None

    def __init__(self, username='', password='', token=''):
        try:
            self.username = username
            self.password = password
            self.token = token
            self.access_token = None
            self.request = RequestManager(self.token, None)
            self.__get_auth_code()
        except Exception as e:
            error = "[EE Auth] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {} | Token: {}".format(str(e), username, password, token)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def __get_auth_code(self):
        try:
            if self.__check_auth():
                return

            response = self.request.request_json('auth.get_auth_code', dumps({
                "username": self.username,
                "password": self.password
            }))

            if response['status']:
                self.access_token = response['data']['access_token']
                self.request.set_access_token(self.access_token)
                self.access_token_timeout = datetime.now() + timedelta(0, response['data']['timeout'])
                self.__save_auth()
                return
            else:
                raise Exception("Auth Error: " + response['message'])
        except Exception as e:
            error = "[EE Auth] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def __save_auth(self):
        try:
            if os.path.isfile('./auth.txt'):
                os.remove('./auth.txt')

            with open('./auth.txt', 'w') as f:
                f.write('{token}|{timeout}'.format(token=self.access_token, timeout=self.access_token_timeout))
        except Exception as e:
            error = "[EE Auth] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def __check_auth(self):
        try:
            if not os.path.exists('./auth.txt'):
                return False

            with open('./auth.txt', 'r') as f:
                info = str(f.read()).split('|')
                self.access_token = info[0]
                self.request.set_access_token(self.access_token)
                self.access_token_timeout = datetime.strptime(str(info[1]), '%Y-%m-%d %H:%M:%S.%f')
                if datetime.now() > self.access_token_timeout:
                    return False
                return True
        except Exception as e:
            error = "[EE Auth] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
