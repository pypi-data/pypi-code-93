"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/3/31 16:21
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    authentication.py
    文件说明
@ChangeHistory:
    datetime action why
    example:
    2021/3/31 16:21 change 'Fix bug'
        
"""
from srf.views import APIView
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError

from srf.exceptions import AuthenticationDenied
from srf.request import SRFRequest
from srf.status import HttpStatus
from srf.constant import ALL_METHOD


class BaseAuthenticate:
    def authenticate(self, request: SRFRequest, view: APIView, **kwargs):
        """验证权限并返回User对象"""
        pass

class BaseTokenAuthenticate(BaseAuthenticate):
    """基于Token的基础验证 JWT """
    token_key = 'X-Token'

    async def authenticate(self, request: SRFRequest, view: APIView, **kwargs):
        """验证逻辑"""
        token = request.headers.get(self.token_key)
        if token is None:
            raise AuthenticationDenied('身份验证错误:请求头{}不存在'.format(self.token_key))
        token_secret = request.app.config.TOKEN_SECRET
        try:
            token_info = self.authentication_token(token, token_secret)
        except ExpiredSignatureError:
            raise AuthenticationDenied('登录已过期')
        except DecodeError:
            raise AuthenticationDenied('错误的Token')
            
        await self._authenticate(request, view, token_info, **kwargs)

    async def _authenticate(self, request: SRFRequest, view: APIView, token_info: dict, **kwargs):
        """主要处理逻辑"""
        pass

    def authentication_token(self, token, token_secret):
        """
        解包Token
        :param token: 口令
        :param token_secret: 解密秘钥
        :return:
        """
        token_info = jwt.decode(token, token_secret, algorithms=['HS256'])
        return token_info
