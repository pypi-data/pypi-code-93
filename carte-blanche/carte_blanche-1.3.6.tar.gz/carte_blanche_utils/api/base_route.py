'''
============================================================================
BOILERPLATE Falcon Route Class
----------------------------------------------------------------------------
'''
import json
import falcon


class BaseRoute(object):
    """A base template class for API routes"""

    def __init__(self, args={}):
        self.name = args.get('name', 'BaseRoute')
        self.version = args.get('version', 'v1')
        self.functions = {}

    def endpoint(self):
        '''create the superclassing route's endpoint'''
        return '/api/%s/%s' % (self.version, self.name)

    @staticmethod
    def send_response(resp, body, data=None, status=falcon.HTTP_200):
        '''
        Build's reply object for route
        '''

        resp.status = status
        if data is not None:
            resp.data = data

        resp.body = json.dumps(body)

    def response_template(self, endpoint=None, status=falcon.HTTP_200):
        '''genereates response object'''
        endpoint = endpoint if endpoint is not None else self.endpoint()
        response_data = {
            'meta': {
                'errors': [],
                'status': status,
                'endpoint': endpoint
            },
            'data': {}
        }
        return response_data
