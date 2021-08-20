# coding: utf-8

from .grant import Grant


class GrantRefreshToken(Grant):
    def __init__(self, *args, **kwargs):
        super(GrantRefreshToken, self).__init__(*args, **kwargs)
        self._refresh_token = kwargs.get("refresh_token")
        self._token_scope = kwargs.get("token_scope", "trapi")

    def get_refresh_token(self):
        return self._refresh_token

    def refresh_token(self, refresh_token):
        self._refresh_token = refresh_token
        return self

    def get_token_scope(self):
        return self._token_scope

    def with_scope(self, token_scope):
        if token_scope:
            self._token_scope = token_scope
        return self
