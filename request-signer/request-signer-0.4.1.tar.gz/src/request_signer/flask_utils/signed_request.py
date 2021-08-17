from ..core.request import SignedRequest
from ..core.signer import Signer


class FlaskSignedRequest(SignedRequest):
    def __init__(self):
        pass

    def configure(self, secret_key):
        self.secret_key = secret_key
        self.signer = Signer(self.secret_key)

    def get(self, url, params=None, *, api_key, headers=None, company_id=None, user_id=None):
        self.configure(api_key)
        return super().get(url, params=params, headers=headers, company_id=company_id, user_id=user_id)

    def post(self, url, data, *, api_key, headers=None, company_id=None, user_id=None):
        self.configure(api_key)
        return super().post(url, data, headers=headers, company_id=company_id, user_id=user_id)

    def patch(self, url, data, *, api_key, headers=None, company_id=None, user_id=None):
        self.configure(api_key)
        return super().patch(url, data, headers=headers, company_id=company_id, user_id=user_id)


signed_request = FlaskSignedRequest()
