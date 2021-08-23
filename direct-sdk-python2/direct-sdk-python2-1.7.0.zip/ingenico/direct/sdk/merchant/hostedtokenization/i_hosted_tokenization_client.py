#
# This class was auto-generated from the API references found at
# https://support.direct.ingenico.com/documentation/api/reference/
#
from abc import ABCMeta, abstractmethod


class IHostedTokenizationClient:
    """
    HostedTokenization client interface. Thread-safe.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_hosted_tokenization(self, body, context=None):
        """
        Resource /v2/{merchantId}/hostedtokenizations - Create hosted tokenization session

        See also https://support.direct.ingenico.com/documentation/api/reference#operation/CreateHostedTokenizationApi

        :param body: :class:`ingenico.direct.sdk.domain.create_hosted_tokenization_request.CreateHostedTokenizationRequest`
        :param context: :class:`ingenico.direct.sdk.call_context.CallContext`
        :return: :class:`ingenico.direct.sdk.domain.create_hosted_tokenization_response.CreateHostedTokenizationResponse`
        :raise: ValidationException if the request was not correct and couldn't be processed (HTTP status code 400)
        :raise: AuthorizationException if the request was not allowed (HTTP status code 403)
        :raise: ReferenceException if an object was attempted to be referenced that doesn't exist or has been removed,
                   or there was a conflict (HTTP status code 404, 409 or 410)
        :raise: DirectException if something went wrong at the Ingenico ePayments platform,
                   the Ingenico ePayments platform was unable to process a message from a downstream partner/acquirer,
                   or the service that you're trying to reach is temporary unavailable (HTTP status code 500, 502 or 503)
        :raise: ApiException if the Ingenico ePayments platform returned any other error
        """
        pass

    @abstractmethod
    def get_hosted_tokenization(self, hosted_tokenization_id, context=None):
        """
        Resource /v2/{merchantId}/hostedtokenizations/{hostedTokenizationId} - Get hosted tokenization session

        See also https://support.direct.ingenico.com/documentation/api/reference#operation/GetHostedTokenizationApi

        :param hosted_tokenization_id: str
        :param context: :class:`ingenico.direct.sdk.call_context.CallContext`
        :return: :class:`ingenico.direct.sdk.domain.get_hosted_tokenization_response.GetHostedTokenizationResponse`
        :raise: ValidationException if the request was not correct and couldn't be processed (HTTP status code 400)
        :raise: AuthorizationException if the request was not allowed (HTTP status code 403)
        :raise: ReferenceException if an object was attempted to be referenced that doesn't exist or has been removed,
                   or there was a conflict (HTTP status code 404, 409 or 410)
        :raise: DirectException if something went wrong at the Ingenico ePayments platform,
                   the Ingenico ePayments platform was unable to process a message from a downstream partner/acquirer,
                   or the service that you're trying to reach is temporary unavailable (HTTP status code 500, 502 or 503)
        :raise: ApiException if the Ingenico ePayments platform returned any other error
        """
        pass
