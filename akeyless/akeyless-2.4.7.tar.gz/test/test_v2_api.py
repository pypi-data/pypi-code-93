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

import akeyless
from akeyless.api.v2_api import V2Api  # noqa: E501
from akeyless.rest import ApiException


class TestV2Api(unittest.TestCase):
    """V2Api unit test stubs"""

    def setUp(self):
        self.api = akeyless.api.v2_api.V2Api()  # noqa: E501

    def tearDown(self):
        pass

    def test_assoc_role_auth_method(self):
        """Test case for assoc_role_auth_method

        """
        pass

    def test_auth(self):
        """Test case for auth

        """
        pass

    def test_configure(self):
        """Test case for configure

        """
        pass

    def test_create_auth_method(self):
        """Test case for create_auth_method

        """
        pass

    def test_create_auth_method_awsiam(self):
        """Test case for create_auth_method_awsiam

        """
        pass

    def test_create_auth_method_azure_ad(self):
        """Test case for create_auth_method_azure_ad

        """
        pass

    def test_create_auth_method_huawei(self):
        """Test case for create_auth_method_huawei

        """
        pass

    def test_create_auth_method_o_auth2(self):
        """Test case for create_auth_method_o_auth2

        """
        pass

    def test_create_auth_method_saml(self):
        """Test case for create_auth_method_saml

        """
        pass

    def test_create_auth_method_universal_identity(self):
        """Test case for create_auth_method_universal_identity

        """
        pass

    def test_create_dynamic_secret(self):
        """Test case for create_dynamic_secret

        """
        pass

    def test_create_key(self):
        """Test case for create_key

        """
        pass

    def test_create_pki_cert_issuer(self):
        """Test case for create_pki_cert_issuer

        """
        pass

    def test_create_role(self):
        """Test case for create_role

        """
        pass

    def test_create_secret(self):
        """Test case for create_secret

        """
        pass

    def test_create_ssh_cert_issuer(self):
        """Test case for create_ssh_cert_issuer

        """
        pass

    def test_decrypt(self):
        """Test case for decrypt

        """
        pass

    def test_decrypt_pkcs1(self):
        """Test case for decrypt_pkcs1

        """
        pass

    def test_delete_auth_method(self):
        """Test case for delete_auth_method

        """
        pass

    def test_delete_auth_methods(self):
        """Test case for delete_auth_methods

        """
        pass

    def test_delete_item(self):
        """Test case for delete_item

        """
        pass

    def test_delete_items(self):
        """Test case for delete_items

        """
        pass

    def test_delete_role(self):
        """Test case for delete_role

        """
        pass

    def test_delete_role_association(self):
        """Test case for delete_role_association

        """
        pass

    def test_delete_role_rule(self):
        """Test case for delete_role_rule

        """
        pass

    def test_delete_roles(self):
        """Test case for delete_roles

        """
        pass

    def test_describe_item(self):
        """Test case for describe_item

        """
        pass

    def test_encrypt(self):
        """Test case for encrypt

        """
        pass

    def test_encrypt_pkcs1(self):
        """Test case for encrypt_pkcs1

        """
        pass

    def test_get_auth_method(self):
        """Test case for get_auth_method

        """
        pass

    def test_get_dynamic_secret_value(self):
        """Test case for get_dynamic_secret_value

        """
        pass

    def test_get_role(self):
        """Test case for get_role

        """
        pass

    def test_get_rsa_public(self):
        """Test case for get_rsa_public

        """
        pass

    def test_get_secret_value(self):
        """Test case for get_secret_value

        """
        pass

    def test_get_ssh_certificate(self):
        """Test case for get_ssh_certificate

        """
        pass

    def test_list_auth_methods(self):
        """Test case for list_auth_methods

        """
        pass

    def test_list_items(self):
        """Test case for list_items

        """
        pass

    def test_list_roles(self):
        """Test case for list_roles

        """
        pass

    def test_move_objects(self):
        """Test case for move_objects

        """
        pass

    def test_refresh_key(self):
        """Test case for refresh_key

        """
        pass

    def test_reverse_rbac(self):
        """Test case for reverse_rbac

        """
        pass

    def test_rollback_secret(self):
        """Test case for rollback_secret

        """
        pass

    def test_rotate_key(self):
        """Test case for rotate_key

        """
        pass

    def test_set_item_state(self):
        """Test case for set_item_state

        """
        pass

    def test_set_role_rule(self):
        """Test case for set_role_rule

        """
        pass

    def test_sign_pkcs1(self):
        """Test case for sign_pkcs1

        """
        pass

    def test_static_creds_auth(self):
        """Test case for static_creds_auth

        """
        pass

    def test_uid_create_child_token(self):
        """Test case for uid_create_child_token

        """
        pass

    def test_uid_generate_token(self):
        """Test case for uid_generate_token

        """
        pass

    def test_uid_list_children(self):
        """Test case for uid_list_children

        """
        pass

    def test_uid_revoke_token(self):
        """Test case for uid_revoke_token

        """
        pass

    def test_uid_rotate_token(self):
        """Test case for uid_rotate_token

        """
        pass

    def test_update_item(self):
        """Test case for update_item

        """
        pass

    def test_update_role(self):
        """Test case for update_role

        """
        pass

    def test_update_secret_val(self):
        """Test case for update_secret_val

        """
        pass

    def test_upload_rsa(self):
        """Test case for upload_rsa

        """
        pass

    def test_verify_pkcs1(self):
        """Test case for verify_pkcs1

        """
        pass


if __name__ == '__main__':
    unittest.main()
