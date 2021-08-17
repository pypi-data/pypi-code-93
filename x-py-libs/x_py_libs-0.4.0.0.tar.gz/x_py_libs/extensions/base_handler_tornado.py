# -*- coding=utf-8 -*-

import tornado.web

from x_py_libs.helpers import UtilitiesHelper, CryptoHelper


class BaseTornadoHandler(tornado.web.RequestHandler):

    app_config = None

    user_id = None
    ignore_authorization = False
    ignore_sign_in_authorization = False

    authorization_config = None
    authorization_token_key = 'x-api-token'

    env = 'dev'

    cache_helper = None

    def __init__(self, *args, **kwargs):
        # print('__init__ super')
        super().__init__(*args, **kwargs)

    # def initialize(self, *args, **kwargs):
    #     print('initialize super')
    #     super().initialize(**kwargs)

    def __verify_token(self):
        authorization_token = self.request.headers.get(self.authorization_token_key)

        try:
            t = authorization_token.split('|')
            token = CryptoHelper.decrypt_by_aes(t[0]).split('_')
            decrypt_ts = CryptoHelper.decrypt_by_aes(token[2])
            ts = token[0] 
            md5_ts = CryptoHelper.encrypt_by_md5(ts).upper()

            if ts != decrypt_ts or md5_ts != t[1].upper():
                return False

            self.user_id = int(token[1])

            if not self.ignore_sign_in_authorization and self.user_id == 0:
                return False

            return True

        except Exception as e:
            return False

    def set_default_headers(self):
        if self.env == 'dev':
            self.set_header('Access-Control-Allow-Credentials', 'False')
            origin = self.request.headers.get('Origin', '')
            # 设置允许的'origin'，只设置'*'时某些特定情况下会失败故最好优先获取请求的域加入允许组中
            self.set_header('Access-Control-Allow-Origin', origin or '*')
            self.set_header('Access-Control-Allow-Headers', '*')
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE, OPTIONS')
        self.set_header('Content-Type', '*')
        pass

    def prepare(self, *args, **kwargs):
        super().prepare()
        if not self.ignore_authorization:
            if not self.__verify_token():
                self.write_response_base(code=-999999, msg='Access Deined!')

    def head(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def patch(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def write_response(self, data=None, encrypt=False):
        self.write_response_base(data=data, encrypt=encrypt)

    def write_response_base(self, code=1, msg='ok', data=None, encrypt=False, json=1, ext=None):
        if data is not None:
            data = data if type(data) is str else UtilitiesHelper.json_dumps_dict(data)
            data = CryptoHelper.encrypt_by_aes(data) if encrypt else data
        else:
            data = ''

        resp = {
            'code': code,
            'msg': msg,
            'data': data,
            'j': json
        }

        if ext is not None:
            resp[ext.get('key')] = ext.get('value')

        self.write(UtilitiesHelper.json_dumps(resp))
        self.finish()

    # def build_response(self, keys=[], data=None, encrypt=True):
    #     response = ApiConf.get_response(keys)
    #     self.write_response_base(response['code'], response['msg'], data, encrypt=encrypt)

    # def write_auth_invalid_response(self):
    #     self.build_response(['common', 'auth-invalid'])

    def get_request_query_argument(self, arg_name='data'):
        return self.get_query_argument(arg_name) if len(self.request.arguments) > 0 else None

    def get_decrypt_request_query_argument(self):
        sc = self.get_request_query_argument()
        if sc is not None:
            sc = CryptoHelper.decrypt_by_aes(sc)
            if sc is not None:
                return UtilitiesHelper.json_loads(sc)
        return None

    def get_decrypt_request_body_data(self, key='data'):
        try:
            data = UtilitiesHelper.json_loads(self.request.body)
            data = CryptoHelper.decrypt_by_aes(data.get(key))
            data = UtilitiesHelper.json_loads(data)
            return data
        except Exception as e:
            print('get decrypt request body data error:', e)
            return None

    def write_sc_list_response(self, query):
        data = self.get_decrypt_request_query_argument()
        # if data is not None:
        rst, cnt = query(data)
        data = {
            'list': rst,
            'total': cnt
        }

        self.write_response_base(data=data, encrypt=False)

    def write_cache_response(self, cache_key, query, simple=True, keys=[]):
        cache_data = None

        if self.cache_helper is not None:
            cache_data = self.cache_helper.get(cache_key)

        # cache_data = None
        if cache_data is None:

            cache_data = query()

            if simple:
                # data = query()
                if type(cache_data) is tuple:
                    cache_data = dict(map(lambda _key, _data: (_key, _data if _data is not None else 'undefined'), keys, cache_data))

                cache_data = {
                    cache_key: cache_data
                }

            cache_data = UtilitiesHelper.json_dumps(cache_data)
            self.cache_helper.set(cache_key, cache_data)

        self.write_response_base(data=cache_data, encrypt=False)
        super().get()
