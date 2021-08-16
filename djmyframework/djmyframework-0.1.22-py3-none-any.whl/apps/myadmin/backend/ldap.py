# -*- coding: utf-8 -*-
# @Time    : 2020-09-16 16:38
# @Author  : xzr
# @File    : ldap
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

import logging

import ldap
import ldapurl

from framework.utils import trace_msg
from .. import settings


class LDAPBackend(object):
    """
    Authenticates with ldap.
    """
    _connection = None
    _connection_bound = False

    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd

        self.use_tls = False
        self.ldap_url = ldapurl.LDAPUrl(settings.LDAP_HOST)
        if self.ldap_url.urlscheme == 'ldaps':
            self.use_tls = True
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

    @property
    def connection(self):
        if not self._connection_bound:
            self._bind()
        return self._get_connection()

    def _bind(self):
        self._bind_as(
                settings.LDAP_BIND_DN, settings.LDAP_BIND_PASSWORD, True
        )

    def _bind_as(self, bind_dn, bind_password, sticky=False):
        try:
            self._get_connection().simple_bind_s(
                    bind_dn, bind_password
            )
            self._connection_bound = sticky
        except Exception as e:
            logging.error('%s,%s' % (bind_dn, e.args[0]))
            raise e

    def _get_connection(self):
        if not self._connection:
            self._connection = ldap.initialize(settings.LDAP_HOST)
            if self.use_tls:
                pass
                self._connection.set_option(ldap.OPT_REFERRALS, 0)

        return self._connection

    def _authenticate_user_dn(self):
        bind_dn = 'cn=%s,%s' % (self.username, settings.LDAP_USER_BASE_DN)
        try:
            self.connection.simple_bind_s(bind_dn, self.passwd)
            return True
        except ldap.INVALID_CREDENTIALS:
            return False

    def get_user_attr(self):
        ldap_results = self.connection.search_s(settings.LDAP_USER_BASE_DN, ldap.SCOPE_SUBTREE,
                                                '(cn=%s)' % self.username,
                                                settings.LDAP_USER_ATTR_MAP.keys())
        res = {}
        if len(ldap_results) > 0:
            for k, v in ldap_results[0][1].items():
                res[k] = v[0]
        return res

    def authenticate(self):
        try:
            is_auth = self._authenticate_user_dn()
            from myadmin.models.user import User
            if is_auth:
                attr_map = self.get_user_attr()
                user, _ = User.objects.get_or_create(username=self.username)
                for k, v in attr_map.items():
                    setattr(user, k, v.decode())
                setattr(user, 'ldap_attr_map', attr_map)
                return user
        except Exception as e:
            print(trace_msg())
            logging.error(e.args[0])
        return None

    def close(self):
        if self._connection:
            self._connection.unbind()
            self._connection.close()
