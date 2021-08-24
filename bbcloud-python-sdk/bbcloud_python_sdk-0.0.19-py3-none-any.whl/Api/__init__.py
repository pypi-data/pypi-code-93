from bbcloud_python_sdk.Api.Models.Http import Http


class Client():
    def __init__(self):
        self.api_prefix = 'api'

        self._auth_team = None
        self._auth_application = None
        self._auth_namespace = None


    def config(self, host, token):
        self.token = token
        self.host = host
        self.base_url = '%s/%s' % (self.host, self.api_prefix)
        self.protocol = Http(client=self)

    def auth_team(self, auth_team):
        self._auth_team = auth_team

    def auth_application(self, auth_application):
        self._auth_application = auth_application

    def auth_namespace(self, auth_namespace):
        self._auth_namespace = auth_namespace



BBCloud = Client()
