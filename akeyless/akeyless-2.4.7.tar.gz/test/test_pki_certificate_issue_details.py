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
from akeyless.models.pki_certificate_issue_details import PKICertificateIssueDetails  # noqa: E501
from akeyless.rest import ApiException

class TestPKICertificateIssueDetails(unittest.TestCase):
    """PKICertificateIssueDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test PKICertificateIssueDetails
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = akeyless.models.pki_certificate_issue_details.PKICertificateIssueDetails()  # noqa: E501
        if include_optional :
            return PKICertificateIssueDetails(
                allow_any_name = True, 
                allow_subdomains = True, 
                allowed_domains_list = [
                    '0'
                    ], 
                allowed_uri_sans = [
                    '0'
                    ], 
                client_flag = True, 
                code_signing_flag = True, 
                country = [
                    '0'
                    ], 
                enforce_hostnames = True, 
                key_bits = 56, 
                key_type = '0', 
                key_usage_list = [
                    '0'
                    ], 
                locality = [
                    '0'
                    ], 
                not_before_duration = 56, 
                organization_list = [
                    '0'
                    ], 
                organization_unit_list = [
                    '0'
                    ], 
                postal_code = [
                    '0'
                    ], 
                province = [
                    '0'
                    ], 
                require_cn = True, 
                server_flag = True, 
                street_address = [
                    '0'
                    ]
            )
        else :
            return PKICertificateIssueDetails(
        )

    def testPKICertificateIssueDetails(self):
        """Test PKICertificateIssueDetails"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
