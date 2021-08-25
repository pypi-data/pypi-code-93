from .core import Session
from .responses import PagedResponse
from . import exceptions
from . import models

import logging

log = logging.getLogger(__name__)


class Client(Session):
    limit = -1

    def request(self, method, url, *args, **kwargs):
        self.limit = kwargs.pop('limit', -1)
        return super(Session, self).request(method, url, *args, **kwargs)

    def _handle_warnings(self, data):
        warnings = data.pop('uuAppErrorMap', {})
        try:
            for key, message in warnings.items():
                log.warning('{key}: {message}'.format(key=key, message=message))
        except AttributeError:
            # it's a string like:
            #   'uuAppErrorMap': '#<UuApp::Oidc::Session:0x00561d53890118>'
            log.warning('{message}'.format(message=warnings))

    def send(self, request, **kwargs):
        response = super(Client, self).send(request, **kwargs)

        if response.headers.get('content-length') == '0':
            return {}

        if response.headers.get('content-type').startswith('application/json'):
            try:
                data = response.json()
                self._handle_warnings(data)
            except ValueError:
                raise exceptions.BadJSON(response)

            limit = self.limit
            self.limit = -1  # reset the limit again
            if 'pageItemList' in data:
                return PagedResponse(
                    super(Client, self), response, limit=limit, key='pageItemList'
                )
            elif 'itemList' in data:
                pageInfo = data.get('pageInfo', None)
                if pageInfo and (
                    pageInfo['pageIndex'] * pageInfo['pageSize'] < pageInfo['total']
                ):
                    return PagedResponse(
                        super(Client, self), response, limit=limit, key='itemList'
                    )
                return data['itemList']
            elif 'testRunList' in data:
                return data['testRunList']
            elif 'dtoSample' in data:
                return data['dtoSample']
            else:
                return data
        elif response.headers.get('content-type').startswith('image/'):
            return models.Image.from_response(response)
        elif response.headers.get('content-type').startswith('text/'):
            return models.Text.from_response(response)
        else:
            log.warning(
                'Do not know how to handle Content-Type: {0:s}.'.format(
                    response.headers.get('content-type')
                )
            )
            return response
