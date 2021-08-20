from gongish import Application as GongishApp
from cytra.db import DatabaseAppMixin
from cytra.auth import AuthAppMixin


class CytraAppBase(GongishApp):
    # Reserved CORS config
    __cors_allow_methods__: set = set()
    __cors_allow_headers__: set = set(("content-type",))
    __cors_expose_headers__: set = set(("content-type",))

    @staticmethod
    def format_json(request, response, indent=None):
        if hasattr(response.body, "to_dict"):
            response.body = response.body.to_dict()
        elif hasattr(response.body, "expose"):
            response.body = response.body.expose()
        GongishApp.format_json(request, response, indent)

    __default_formatter__ = format_json

    def setup(self):
        pass

    def shutdown(self):
        pass


class Application(AuthAppMixin, DatabaseAppMixin, CytraAppBase):
    pass
