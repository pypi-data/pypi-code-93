from .base import BaseAPIClient


class EntityAPI(BaseAPIClient):

    def get_offers(self, entity_id=None, **kwargs):
        return self._get('offers', entity_id=entity_id, **kwargs)

    def get_advertisers(self, entity_id=None, **kwargs):
        return self._get('advertisers', entity_id=entity_id, **kwargs)

    def get_affiliates(self, entity_id=None, **kwargs):
        return self._get('affiliates', entity_id=entity_id, **kwargs)

    def get_products(self, entity_id=None, **kwargs):
        params = {'advertiser_id': entity_id} if entity_id else {}
        return self._get('products', params=params, **kwargs)

    def get_request(self, request_id, **kwargs):
        return self._get('requests', entity_id=request_id, **kwargs)

    def get_past_changes(self, **kwargs):
        """ Return executed changes recorded in Changelog. """
        return self._post('audit/search/', **kwargs)

    def get_scheduled_changes(self, **kwargs):
        """ Return scheduled changes that have yet to be executed. """
        return self._post('schedule/search', **kwargs)
