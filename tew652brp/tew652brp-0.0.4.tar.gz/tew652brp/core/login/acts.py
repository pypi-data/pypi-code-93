from tew652brp.core.base import BaseAct


class LoginAct(BaseAct):
    def __init__(self, request_method, url, username, password):
        super().__init__(request_method, url)

        self._params = {
            'username': username,
            'password': password,
        }

    def submit(self):
        return 'status.htm' in super().submit().text
