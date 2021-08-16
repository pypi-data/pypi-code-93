# -*- coding: utf-8 -*-
# @Time    : 2020-09-16 16:38
# @Author  : xzr
# @File    : ldap
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

import ldap
import ldapurl

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
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
            self.use_tls = True

    def auth(self):
        return self._authenticate_user_dn()

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
        self._get_connection().simple_bind_s(
                bind_dn, bind_password
        )
        self._connection_bound = sticky

    def _get_connection(self):
        if not self._connection:
            self._connection = ldap.initialize(settings.LDAP_HOST)
            if self.use_tls:
                self._connection.start_tls_s()
        return self._connection

    def _authenticate_user_dn(self):
        bind_dn = 'cn=%s,%s' % (self.username, settings.LDAP_USER_BASE_DN)
        try:
            self._bind_as(bind_dn, self.passwd, False)
            return True
        except ldap.INVALID_CREDENTIALS:
            return False

    def get_user_attr(self):
        results = self._connection.search_s(settings.LDAP_USER_BASE_DN, ldap.SCOPE_SUBTREE, '(cn=%s)' % self.username,
                                            settings.LDAP_FILTER_FIELD.keys())
        if len(results) > 0:
            return results[0][1]
        else:
            return {}

    def close(self):
        self._connection.unbind()
