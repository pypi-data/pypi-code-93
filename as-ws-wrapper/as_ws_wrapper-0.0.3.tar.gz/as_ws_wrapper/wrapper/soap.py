from zeep import Client
from zeep.wsse import UsernameToken

from ..constants import PASSWORD, USERNAME


class BaseSoapWrapper:
    def __init__(self, username=None, password=None):
        if username is None:
            username = USERNAME

        self.__username = username

        if password is None:
            password = PASSWORD

        self.__password = password

    def get_client(self, wsdl):
        return Client(wsdl=wsdl, wsse=self.wsse)

    @property
    def wsse(self):
        return UsernameToken(self.__username, self.__password)
