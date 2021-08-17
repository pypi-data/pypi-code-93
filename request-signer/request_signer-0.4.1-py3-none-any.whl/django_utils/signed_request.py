from django.conf import settings

from ..core.request import SignedRequest
from ..core.exceptions import MissingSettings


class DjangoSignedRequest(SignedRequest):
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or getattr(settings, 'SIGNED_REQUEST_API_KEY')
        if self.secret_key is None:
            raise MissingSettings('SIGNED_REQUEST_API_KEY config required.')
        super().__init__(self.secret_key)


signed_request = DjangoSignedRequest()
