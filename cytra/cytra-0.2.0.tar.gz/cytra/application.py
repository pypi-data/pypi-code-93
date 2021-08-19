from gongish import Application as GongishApp
from cytra.db import DatabaseAppMixin
from cytra.auth import AuthAppMixin


class CytraAppBase(GongishApp):
    # Reserved CORS config
    _cors_allow_methods: set = None
    _cors_allow_headers: set = None
    _cors_expose_headers: set = None

    @staticmethod
    def format_json(request, response, indent=None):
        if hasattr(response.body, "to_dict"):
            response.body = response.body.to_dict()
        elif hasattr(response.body, "expose"):
            response.body = response.body.expose()
        GongishApp.format_json(request, response, indent)

    __default_formatter__ = format_json

    def setup(self):
        self._cors_allow_methods = set()
        self._cors_allow_headers = set(("content-type",))
        self._cors_expose_headers = set(("content-type",))

    def shutdown(self):
        pass


class Application(AuthAppMixin, DatabaseAppMixin, CytraAppBase):
    pass
