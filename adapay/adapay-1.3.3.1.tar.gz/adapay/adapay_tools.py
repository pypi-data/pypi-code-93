from adapay.request_tools import request_post, bill_download, query_identity, public_key
from adapay_core.rsa_utils import rsa_design


class AdapayTools(object):

    @classmethod
    def union_user_id(cls, **kwargs):
        return request_post(query_identity, kwargs)

    @classmethod
    def download_bill(cls, **kwargs):
        return request_post(bill_download, kwargs)

    @classmethod
    def verify_sign(cls, data, sign, pub_key=public_key):
        return rsa_design(sign, data, pub_key)
