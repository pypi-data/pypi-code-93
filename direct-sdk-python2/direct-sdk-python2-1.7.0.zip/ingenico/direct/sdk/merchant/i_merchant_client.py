#
# This class was auto-generated from the API references found at
# https://support.direct.ingenico.com/documentation/api/reference/
#
from abc import ABCMeta, abstractmethod


class IMerchantClient:
    """
    Merchant client interface. Thread-safe.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def products(self):
        """
        Resource /v2/{merchantId}/products

        :return: :class:`ingenico.direct.sdk.merchant.products.i_products_client.IProductsClient`
        """
        pass

    @abstractmethod
    def sessions(self):
        """
        Resource /v2/{merchantId}/sessions

        :return: :class:`ingenico.direct.sdk.merchant.sessions.i_sessions_client.ISessionsClient`
        """
        pass

    @abstractmethod
    def payouts(self):
        """
        Resource /v2/{merchantId}/payouts

        :return: :class:`ingenico.direct.sdk.merchant.payouts.i_payouts_client.IPayoutsClient`
        """
        pass

    @abstractmethod
    def payments(self):
        """
        Resource /v2/{merchantId}/payments

        :return: :class:`ingenico.direct.sdk.merchant.payments.i_payments_client.IPaymentsClient`
        """
        pass

    @abstractmethod
    def services(self):
        """
        Resource /v2/{merchantId}/services

        :return: :class:`ingenico.direct.sdk.merchant.services.i_services_client.IServicesClient`
        """
        pass

    @abstractmethod
    def product_groups(self):
        """
        Resource /v2/{merchantId}/productgroups

        :return: :class:`ingenico.direct.sdk.merchant.productgroups.i_product_groups_client.IProductGroupsClient`
        """
        pass

    @abstractmethod
    def hosted_tokenization(self):
        """
        Resource /v2/{merchantId}/hostedtokenizations

        :return: :class:`ingenico.direct.sdk.merchant.hostedtokenization.i_hosted_tokenization_client.IHostedTokenizationClient`
        """
        pass

    @abstractmethod
    def tokens(self):
        """
        Resource /v2/{merchantId}/tokens

        :return: :class:`ingenico.direct.sdk.merchant.tokens.i_tokens_client.ITokensClient`
        """
        pass

    @abstractmethod
    def hosted_checkout(self):
        """
        Resource /v2/{merchantId}/hostedcheckouts

        :return: :class:`ingenico.direct.sdk.merchant.hostedcheckout.i_hosted_checkout_client.IHostedCheckoutClient`
        """
        pass
