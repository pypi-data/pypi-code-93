# coding: utf-8

"""
    Akeyless API

    The purpose of this application is to provide access to Akeyless API.  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Contact: support@akeyless.io
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import akeyless
from akeyless.models.create_auth_method_universal_identity import CreateAuthMethodUniversalIdentity  # noqa: E501
from akeyless.rest import ApiException

class TestCreateAuthMethodUniversalIdentity(unittest.TestCase):
    """CreateAuthMethodUniversalIdentity unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test CreateAuthMethodUniversalIdentity
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = akeyless.models.create_auth_method_universal_identity.CreateAuthMethodUniversalIdentity()  # noqa: E501
        if include_optional :
            return CreateAuthMethodUniversalIdentity(
                access_expires = 56, 
                bound_ips = [
                    '0'
                    ], 
                deny_inheritance = True, 
                deny_rotate = True, 
                name = '0', 
                token = '0', 
                ttl = 56, 
                uid_token = '0'
            )
        else :
            return CreateAuthMethodUniversalIdentity(
                name = '0',
        )

    def testCreateAuthMethodUniversalIdentity(self):
        """Test CreateAuthMethodUniversalIdentity"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
