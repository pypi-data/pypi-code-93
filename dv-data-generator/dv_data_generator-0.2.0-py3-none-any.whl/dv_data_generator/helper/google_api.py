import httplib2
from oauth2client.client import Credentials
from oauth2client.file import Storage
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

API_SCOPES = [
    "https://www.googleapis.com/auth/doubleclickbidmanager",
    "https://www.googleapis.com/auth/display-video",
]


class GoogleApi():

    def __init__(self, credentials: str, token: dict = None, service_account: bool = False, debug=False):
        self.credentials = credentials
        self.token = token
        self._debug = debug
        self.service_account = service_account
        self.init_services()
        self.http = self.authenticate()

    def get_service(self, name):
        """Abstract function to get the API service
        :param name: Name of the API service
        :return: Service that has been requested
        """
        if name.upper() == "CM":
            api_service, api_version = self.cm_service, self.cm_version
        elif name.upper() == "DV360":
            api_service, api_version = self.dv360_service, self.dv360_version
        elif name.upper() == "DBM":
            api_service, api_version = self.dbm_service, self.dbm_version
        elif name.upper() == "SA360":
            api_service, api_version = self.sa360_service, self.sa360_version
        elif name.upper() == "SHEETS":
            api_service, api_version = self.sheets_service, self.sheets_version
        else:
            raise ValueError('We could not determine the service ' + name)

        if self.service_account:
            return discovery.build(
                api_service, api_version, http=self.http)

        return self.__get_concrete_service(api_service, api_version)

    def __get_concrete_service(self, api_service, api_version):

        return discovery.build(
            api_service,
            api_version,
            http=self.http,
        )

    def __authenticate_using_service_account(self):
        """Authorizes an httplib2.Http instance using service account credentials json dict."""
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            self.token,
            scopes=API_SCOPES)

        http = credentials.authorize(httplib2.Http())

        return http

    def authenticate(self):
        """
        Authorizes an httplib2.Http instance using user account credentials.
        Check whether credentials exist in the credential store. Using a credential
        store allows auth credentials to be cached, so they survive multiple runs
        of the application. This avoids prompting the user for authorization every
        time the access token expires, by remembering the refresh token.
        :return: an authorized httplib2.Http instance
        """
        credentials = None

        if self._debug:
            return httplib2.Http()

        if self.service_account:
            return self.__authenticate_using_service_account()

        if self.token:
            credentials = Credentials.from_authorized_user_info(self.token)

        if not credentials:
            storage = Storage(self.credentials)
            credentials = storage.get()
        # If no credentials were found, go through the authorization process and
        # persist credentials to the credential store.
        credentials_invalid = credentials is None or credentials.invalid

        if credentials_invalid:
            raise AuthorizatonError(
                "The credentials in file {} are not valid".format(self.credentials))

        # Use the credentials to authorize an httplib2.Http instance.
        http = credentials.authorize(httplib2.Http())

        return http

    def init_services(self):
        """
        Set the name and version of the supported APIS
        :return: void
        """
        self.dv360_service = 'displayvideo'
        self.dv360_version = 'v1'

        self.dbm_service = 'doubleclickbidmanager'
        self.dbm_version = 'v1.1'

        self.cm_service = 'dfareporting'
        self.cm_version = 'v3.3'

        self.sa360_service = 'doubleclicksearch'
        self.sa360_version = 'v2'

        self.sheets_service = 'sheets'
        self.sheets_version = 'v4'


class AuthorizatonError(Exception):
    pass
