# -*- coding: utf-8 -*-
    
    
import time
import base64
import hmac

EncryptKey = 'asldkQ)()*(@#'
def generate_token(value, expire=3600):
        r'''
            @Args:
                key: str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key)
                expire: int(最大有效时间，单位为s)
            @Return:
                state: str
        '''
        ts_str = str(time.time() + expire)
        ts_byte = ts_str.encode("utf-8")
        value  = str(value).encode('utf-8')
        encryptStr = value + '-' + ts_byte
        sha1_tshexstr  = hmac.new(EncryptKey.encode("utf-8"),encryptStr,'sha1').hexdigest() 
        token = encryptStr + '-' + sha1_tshexstr 
        b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
        return b64_token.decode("utf-8")


def certify_token( token):
    r'''
        @Args:
            key: str
            token: str
        @Returns:
            boolean
    '''
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split('-')
    if len(token_list) != 3:
        return False
    value, ts_str,known_sha1_tsstr =  token_list
    if float(ts_str) < time.time():
        return False
    encryptStr = value + '-' + ts_str
    sha1 = hmac.new(EncryptKey.encode("utf-8"),encryptStr.encode('utf-8'),'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False 
    # token certification success
    return value 