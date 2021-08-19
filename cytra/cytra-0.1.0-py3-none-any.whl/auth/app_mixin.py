import functools

from gongish import HTTPUnauthorized, HTTPForbidden

from cytra.auth import Authenticator


class AuthAppMixin:
    __authenticator__ = Authenticator
    auth = None
    identity = None

    def on_begin_request(self):
        if self.auth:
            self.auth.authenticate_request()

        super().on_begin_request()

    def setup(self):
        if "auth" in self.config:
            self.auth = self.__authenticator__(app=self)
        else:
            self.auth = None
        super().setup()

    def shutdown(self):
        if self.auth is not None:
            self.auth = None
            self.identity = None
        super().shutdown()

    def authorize(self, *roles):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):

                if not self.identity:
                    raise HTTPUnauthorized("No identity")

                if len(roles) > 0 and not self.identity.is_in_roles(*roles):
                    raise HTTPForbidden

                return func(*args, **kwargs)

            return wrapper

        if roles and callable(roles[0]):
            f = roles[0]
            roles = []
            return decorator(f)
        else:
            return decorator
