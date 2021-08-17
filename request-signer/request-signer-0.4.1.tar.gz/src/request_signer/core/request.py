from urllib.parse import urlparse
import requests
import simplejson as json

from .signer import Signer


class SignedRequest:
    header = 'X-SignedRequest-Signature'

    def __init__(self, secret_key):
        self.signer = Signer(secret_key)

    def get(self, url, *, params=None, headers=None, company_id=None, user_id=None):
        headers = self.add_signature_header('GET', url, '', headers, company_id, user_id)
        params = self.add_sig_params(params, company_id=company_id, user_id=user_id)
        return requests.get(url, params=params, headers=headers)

    def post(self, url, data, *, headers=None, company_id=None, user_id=None):
        headers = self.add_signature_header('POST', url, json.dumps(data), headers, company_id, user_id)
        params = self.add_sig_params(None, company_id=company_id, user_id=user_id)
        return requests.post(url, json=data, headers=headers, params=params)

    def patch(self, url, data, *, headers=None, company_id=None, user_id=None):
        headers = self.add_signature_header('PATCH', url, json.dumps(data), headers, company_id, user_id)
        params = self.add_sig_params(None, company_id=company_id, user_id=user_id)
        return requests.patch(url, json=data, headers=headers, params=params)

    def add_signature_header(self, method, url, data, headers, company_id, user_id):
        signature = self.create_signature(method, url, data, company_id, user_id)
        sig_header = {self.header: signature}
        if headers:
            headers.update(sig_header)
            return headers
        return sig_header

    def add_sig_params(self, params, *, company_id, user_id):
        sig_params = {
            'rs_company_id': company_id,
            'rs_user_id': user_id,
        }
        if params:
            params.update(sig_params)
            return params
        return sig_params

    def create_signature(self, method, url, payload=None, company_id=None, user_id=None):
        path = urlparse(url).path
        data = f'{method}.{path}.{payload}.{company_id}.{user_id}'
        return self.signer.sign(data)
