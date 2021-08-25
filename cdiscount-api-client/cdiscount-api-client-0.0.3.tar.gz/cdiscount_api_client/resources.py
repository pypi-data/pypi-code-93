import json

from cdiscount_api_client.utils import urljoin

class ResourcePool:
    def __init__(self, endpoint, session, subscription_key):
        """Initialize the ResourcePool to the given endpoint. Eg: products"""
        self._endpoint = endpoint
        self._session = session
        self._subscription_key = subscription_key
        self._session.headers['Ocp-Apim-Subscription-Key'] = self._subscription_key

    def get_url(self):
        return self._endpoint

class CreatableResource:
    def create_item(self, item, files=None):
        if files:
            self._session.headers.pop('Content-Type')
            self._session.headers.pop('Accept')
            print(self._session.headers)
            res = self._session.post(self._endpoint, files=files, data=item)
        else:
            res = self._session.post(self._endpoint, data=json.dumps(item))
        return res

class GettableResource:
    def fetch_item(self, code):
        url = urljoin(self._endpoint, code)
        res = self._session.get(url)
        return res

class ListableResource:
    def fetch_list(self, args=None):
        res = self._session.get(self._endpoint, params=args)
        return res

class SearchableResource:
    def search(self, query):
        params = {
            'query': query
        }
        res = self._session.get(self._endpoint, params=params)
        return res

class UpdatableResource:
    def update_create_item(self, item, code=None):
        if code is None:
            code = item.get('id')
        url = urljoin(self._endpoint, code)
        res = self._session.put(url, data=json.dumps(item))
        return res

class DeletableResource:
    def delete_item(self, code):
        url = urljoin(self._endpoint, code)
        res = self._session.delete(url)
        return res

# Pools

# Product
class ProductManagementPool(ResourcePool):

    @property
    def categories(self):
        return ProductManagementCatgoriesPool(
            urljoin(self._endpoint, 'categories'), self._session, self._subscription_key
        )
    
    @property
    def models(self):
        return ProductManagementModelsPool(
            urljoin(self._endpoint, 'models'), self._session, self._subscription_key
        )

    @property
    def search_products(self):
        return ProductManagementProductSearchPool(
            urljoin(self._endpoint, 'products/search',), self._session, self._subscription_key
        )

    @property
    def product_integration_packages(self):
        return ProductManagementProductIntegrationPool(
            urljoin(self._endpoint, 'product-integration-packages',), self._session, self._subscription_key
        )

class ProductManagementCatgoriesPool(
    ResourcePool,
    ListableResource):
    pass

class ProductManagementModelsPool(
    ResourcePool,
    ListableResource):
    pass

class ProductManagementProductSearchPool(
    ResourcePool, 
    CreatableResource):
    pass

class ProductManagementProductIntegrationPool(
    ResourcePool,
    GettableResource,
    CreatableResource):
    pass
    
# Offer

class OfferManagementPool(ResourcePool):
    
    @property
    def competing_offer_changes(self):
        return OfferManagementCompetingOfferChangesPool(
            urljoin(self._endpoint, 'competing-offer-changes'), self._session, self._subscription_key
        )

    @property
    def offers(self):
        return OfferManagementOffersPool(
            urljoin(self._endpoint, 'offers'), self._session, self._subscription_key
        )

    @property
    def offer_integration_packages(self):
        return OfferManagementOfferIntegrationPackagesPool(
            urljoin(self._endpoint, 'offer-integration-packages'), self._session, self._subscription_key
        )

    @property
    def seller_deals_search(self):
        return OfferManagementSellerDealsSearchPool(
            urljoin(self._endpoint, 'seller-deals/search'), self._session, self._subscription_key
        )        

class OfferManagementCompetingOfferChangesPool(
    ResourcePool,
    ListableResource):
    pass

class OfferManagementOffersPool(
    ResourcePool,
    CreatableResource):
    
    @property
    def search(self):
        return OfferManagementOffersSearchPool(
            urljoin(self._endpoint, 'search'), self._session, self._subscription_key
        )

class OfferManagementOffersSearchPool(
    ResourcePool,
    CreatableResource):
    pass

class OfferManagementOfferIntegrationPackagesPool(
    ResourcePool,
    GettableResource,
    CreatableResource):
    pass

class OfferManagementSellerDealsSearchPool(
    ResourcePool,
    CreatableResource):
    pass

# Order

class OrderManagementPool(ResourcePool):

    @property
    def search_orders(self):
        return OrderManagementSearchOrdersPool(
            urljoin(self._endpoint, 'search'), self._session, self._subscription_key
        )    
    
    def commercial_gestures(self, order_number):
        return OrderManagementCommercialGesturesPool(
            urljoin(self._endpoint, order_number, 'commercial-gestures'), self._session, self._subscription_key
        )

    def commercial_gesture_eligibilities(self, order_number):
        return OrderManagementCommercialGestureEligibilitiesPool(
            urljoin(self._endpoint, order_number, 'commercial-gesture-eligibilities'), self._session, self._subscription_key
        )

    def validate_order(self, order_number):
        return OrderManagementValidateOrdersPool(
            urljoin(self._endpoint, order_number, 'validate'), self._session, self._subscription_key
        )

class OrderManagementCommercialGesturesPool(
    ResourcePool, 
    CreatableResource,
    ListableResource):
    pass

class OrderManagementCommercialGestureEligibilitiesPool(
    ResourcePool,
    ListableResource):
    pass

class OrderManagementSearchOrdersPool(
    ResourcePool,
    CreatableResource):
    pass

class OrderManagementValidateOrdersPool(
    ResourcePool,
    UpdatableResource):
    pass