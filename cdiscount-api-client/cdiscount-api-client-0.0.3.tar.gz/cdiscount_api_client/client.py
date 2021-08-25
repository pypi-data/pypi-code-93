import requests as rq

from cdiscount_api_client import (
    resources,
    utils
)

class AuthError:
    pass

class CdiscountClient:
    BASE_URL = 'https://marketplaceapi.cdiscount.com'

    def __init__(self, client_id, client_secret, seller_id, subscription_keys={}):
        self._session = rq.Session()

        self._client_id = client_id
        self._client_secret = client_secret
        self._seller_id = seller_id
        self._subscription_keys = subscription_keys

        self._urls = {
            'token': "https://oauth2.cdiscount.com/auth/realms/maas-international-sellers/protocol/openid-connect/token"
        }
        self._resources = {
            'product_management': resources.ProductManagementPool(
                utils.urljoin(self.BASE_URL, 'productManagement'), self._session, self._subscription_keys.get('product')
            ),
            'order_management': resources.OrderManagementPool(
                utils.urljoin(self.BASE_URL, 'OrderManagement/orders'), self._session, self._subscription_keys.get('order')
            ),
            'offer_management': resources.OfferManagementPool(
                utils.urljoin(self.BASE_URL, 'offerManagement'), self._session, self._subscription_keys.get('offer')
            )
        }

        self._authenticate()

    def _authenticate(self):
        auth_data = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'client_credentials'
        }
        res = self._session.post(self._urls['token'], data=auth_data)
        if res.status_code != 200:
            raise AuthError('Error {}: {}'.format(res.status_code, res.text))

        access_token = res.json()['access_token']
        self._session.headers.update({
            'Authorization': 'Bearer {}'.format(access_token),
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json-patch+json',
            'SellerId': self._seller_id
        })

    @property
    def resources(self):
        return self._resources

    @property
    def product_management(self):
        return self._resources['product_management']

    @property
    def order_management(self):
        return self._resources['order_management']

    @property
    def offer_management(self):
        return self._resources['offer_management']                