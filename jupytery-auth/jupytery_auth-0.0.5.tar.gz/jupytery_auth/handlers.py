import json

from jupyter_server.base.handlers import JupyterHandler, APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin

import tornado
from tornado.websocket import WebSocketHandler, websocket_connect
from tornado.ioloop import IOLoop

class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):

    def get(self):
        # The name of the extension to which this handler is linked.
        self.log.info("Extension Name in {} default handler: {}".format(self.name, self.name))
        # A method for getting the url to static files (prefixed with /static/<name>).
        self.write('<h1>Jupytery Auth Extension</h1>')
        self.write('Configuration in {} default handler: {}'.format(self.name, self.config))


class MeHandler(APIHandler):

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            'session_id': self.get_session_id(),
            'me': self.get_current_user(),
        }))

class UsersHandler(APIHandler):

    @tornado.web.authenticated
    def get(self):
        if len(self.get_sessions()) == 0:
            self.finish(json.dumps({}))
        else:
            users = [s['user'] for s in self.get_sessions().values()]
            self.finish(json.dumps({
                'session_id': self.get_session_id(),
                'me': self.get_current_user(),
                'sessions_count': self.get_sessions_count(),
                'users': users
            }))
