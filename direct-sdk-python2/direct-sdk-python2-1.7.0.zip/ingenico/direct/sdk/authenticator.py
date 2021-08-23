from abc import ABCMeta, abstractmethod


class Authenticator(object):
    """
    Used to sign requests to the Ingenico ePayments platform.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_simple_authentication_signature(self, http_method, resource_uri, request_headers):
        """
        Creates a signature for the simple security model.

        :param http_method: The HTTP method.
        :param resource_uri: The URI of the resource.
        :param request_headers:  A list of RequestHeaders. This list may not be
         modified and may not contain headers with the same name.
        """
