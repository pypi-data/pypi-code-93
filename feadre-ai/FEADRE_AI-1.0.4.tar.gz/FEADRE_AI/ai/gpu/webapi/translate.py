import hashlib
import json
import random

import requests

from ftools.FGLOBAL_VAR import GLOBAL

'''
API 翻译
'''

def make_md5(s, encoding='utf-8'):
    # Generate salt and sign
    return hashlib.md5(s.encode(encoding)).hexdigest()


def translate_baidu(query, from_lang='en', to_lang='zh'):
    print('query', query)
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    # query = 'Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'

    salt = random.randint(32768, 65536)
    sign = make_md5(GLOBAL.APPID_BAIDU + query + str(salt) + GLOBAL.APPKEY_BAIDU)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': GLOBAL.APPID_BAIDU, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # dict -> str
    res = json.dumps(result, indent=4, ensure_ascii=False)
    print(res)
    return result['trans_result'][0]['dst']


if __name__ == '__main__':
    print(translate_baidu('猫', from_lang='zh', to_lang='en'))
