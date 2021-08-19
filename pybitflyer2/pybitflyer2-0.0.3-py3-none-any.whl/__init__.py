
from .http_private import PrivateClient
from .http_public import PublicClient
from .realtimeclient import RealtimeClient

from logging import getLogger, NullHandler
logger = getLogger(__name__).addHandler(NullHandler())


class Bitflyer:
    @staticmethod
    def http_public_client():
        return PublicClient()

    @staticmethod
    def http_private_client(apikey, apisecret):
        return PrivateClient(apikey, apisecret)

    @staticmethod
    def realtime_client(apikey=None, apisecret=None):
        return RealtimeClient(key=apikey, secret=apisecret)
