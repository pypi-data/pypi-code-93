import json

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from munch import Munch
# from py_eureka_client import eureka_client
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission


class CustomIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if request.user == 'INVALIDO':
            raise TokenNotFoundException
        if request.user == 'EXPIRADO':
            raise TokenExpiredException

        # if type(request.user) is AnonymousUser:
        #     EUREKA = settings.EUREKA_SERVER
        #     user_test = request.headers.get('User', None)
        #     if user_test is not None:
        #         request.user = Munch(json.loads(user_test))
        #         return True
        #
        #     ip_requester = f'http://{request.headers._store["host"][1]}/'
        #     clients = eureka_client.get_applications(eureka_server=EUREKA).applications
        #     for client in clients:
        #         if client.instances[0].homePageUrl == ip_requester and client.name == 'MPOS-SECURITY':
        #             return True

        return bool(type(request.user) is not AnonymousUser)


class TokenNotFoundException(APIException):
    status_code = 401
    default_detail = 'Token inválido.'
    default_code = 'token_not_found_exception'


class TokenExpiredException(APIException):
    status_code = 401
    default_detail = 'Token expirado.'
    default_code = 'token_expired_exception'
