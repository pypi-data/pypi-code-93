import json as jsonlib
import functools
import webtest

from urllib.parse import urlencode

from cytra import Application
from cytra.db import DatabaseManager, metadata


class TestingApp:
    __test__ = False  # Disable pytest collector

    def __init__(self, app: Application, config_filename: str):
        self.app = app
        app.configure(config_filename)

    def __enter__(self):
        with DatabaseManager(
            engine_kwargs=self.app.config.sqlalchemy_test.engine,
            admin_engine_kwargs=self.app.config.sqlalchemy_admin.engine,
        ) as dbm:
            if dbm.database_exists():
                dbm.drop_database()
            dbm.create_database()

        self.app.setup()
        self.testapp = webtest.TestApp(self.app)
        self.testapp.extra_environ["HTTP_ACCEPT"] = "application/json"
        self.testapp.extra_environ["REMOTE_ADDR"] = "127.0.0.1"
        self.testapp.extra_environ["HTTP_APP_CLIENT"] = "MapleWeb-1.2.3-beta"
        self.testapp.extra_environ["HTTP_USER_AGENT"] = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) "
            "AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 "
            "Mobile/9B179 Safari/7534.48.3; fa-IR; some; extra; info)"
        )

        metadata.drop_all(bind=self.app.db.get_bind())
        metadata.create_all(bind=self.app.db.get_bind())
        return self

    def __exit__(self, *args):
        self.app.shutdown()

    def get_access_token(self, as_):  # pragma: nocover
        raise NotImplementedError

    def authorize(self, as_: str = None):
        auth_key = "HTTP_AUTHORIZATION"
        if auth_key in self.testapp.extra_environ:
            del self.testapp.extra_environ[auth_key]

        if as_ is None or as_ == "visitor":
            return

        self.testapp.extra_environ[auth_key] = self.get_access_token(as_)

    def __call__(self, as_, path, method="get", json=None, qs=None, **kwargs):
        self.authorize(as_)

        if qs:
            path = "%s?%s" % (path, urlencode(qs))

        if json:
            kwargs.update(
                params=jsonlib.dumps(json),
                upload_files=None,
                content_type="application/json",
            )

        return self.testapp._gen_request(
            method.upper(), path, expect_errors=False, **kwargs
        )

    def __getattr__(self, key):
        if key not in self.app.verbs:
            return super().__getattribute__(key)

        return functools.partial(self.__call__, method=key)
