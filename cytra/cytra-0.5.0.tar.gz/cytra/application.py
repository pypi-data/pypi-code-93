from gongish import Application as GongishApp
from cytra.db import DatabaseAppMixin
from cytra.auth import AuthAppMixin
from cytra.cors import CORS


class CytraAppBase(GongishApp):
    # Reserved CORS config
    cors: CORS = None

    @staticmethod
    def format_json(request, response, indent=None):
        if hasattr(response.body, "to_dict"):
            response.body = response.body.to_dict()
        elif hasattr(response.body, "expose"):
            response.body = response.body.expose()
        GongishApp.format_json(request, response, indent)

    __default_formatter__ = format_json

    def __init__(self):
        super().__init__()
        self.cors = CORS()
        self.cors.allow_headers.add("content-type")
        self.cors.expose_headers.add("content-type")

    def setup(self):
        pass

    def shutdown(self):
        pass


class Application(AuthAppMixin, DatabaseAppMixin, CytraAppBase):
    pass
