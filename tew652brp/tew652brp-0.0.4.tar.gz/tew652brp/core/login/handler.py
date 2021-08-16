from tew652brp.core.base import BaseHandler
from tew652brp.core.login.acts import LoginAct


class LoginHandler(BaseHandler):
    def login(self, username, password):
        return LoginAct(
            self._session.post,
            self._routes['login'],
            username, password
        ).submit()
