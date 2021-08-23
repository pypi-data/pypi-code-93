import os
import requests
from urllib.parse import urljoin


class BaseAPIClient(object):
    staging = False

    def __init__(self, api_key=None):
        self.session = requests.Session()

        if not self.staging:
            self.base_url = 'https://go-api.leadnomics.com/'
            environ_key = 'EDGE_API_KEY'
        else:
            self.base_url = 'https://edge-staging.com/'
            environ_key = 'EDGE_STAGING_API_KEY'

        try:
            self.session.headers.update({
                'X-Edge-Key': api_key if api_key else os.environ[environ_key]
            })
        except KeyError:
            raise KeyError('`{}` environment variable not found and no api_key specified.'.format(environ_key))

    def _get(self, entity_type, entity_id=None, append_url=True, **kwargs):
        endpoint = 'api/{}/{}'.format(entity_type, entity_id if entity_id else '')
        return self._request('get', endpoint, append_url=append_url, **kwargs)

    def _post(self, endpoint='', append_url=True, **kwargs):
        return self._request('post', endpoint, append_url=append_url, **kwargs)

    def _request(self, method, endpoint, params=None, data=None, append_url=True, **kwargs):
        url = self._build_url(endpoint) if append_url else self.base_url
        params = params or {}
        data = data or {}

        response = self.session.request(method, url, params=params, data=data, **kwargs)

        return response

    def _build_url(self, endpoint):
        return urljoin(self.base_url, endpoint) if endpoint else self.base_url
