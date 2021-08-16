from tew652brp.core.access.virtual.types import VServerInfo
from tew652brp.core.base import BaseHandler
from tew652brp.core.access.virtual.acts import (
    GetServersAct,
    UpdateServerAct,
    DeleteServerAct
)


class VirtualHandler(BaseHandler):
    """
    Virtual server handler. Contains all needed acts. Included in the Client class ( tew652brp.client ).
    """
    def __init__(self, session, url):
        super().__init__(session, url)

    def get_servers(self):
        """ Get all virtual servers """
        return GetServersAct(
            self._session.post, self._routes['get_set']
        ).submit()

    def update_server(self, server_info: VServerInfo):
        """ Update server by VServerInfo """
        return UpdateServerAct(
            self._session.post, self._routes['get_set'], server_info
        ).submit()

    def delete_server(self, server_info: VServerInfo):
        """ Delete server by server instance """
        return DeleteServerAct(
            self._session.post, self._routes['get_set'], server_info
        ).submit()
