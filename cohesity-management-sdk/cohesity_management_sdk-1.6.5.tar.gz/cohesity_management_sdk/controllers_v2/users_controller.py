# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.security_principals import SecurityPrincipals
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class UsersController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(UsersController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_security_principals(self,
                                sids):
        """Does a GET request to /security-principals.

        Get Security Principals

        Args:
            sids (list of string): Specifies a list of SIDs.

        Returns:
            SecurityPrincipals: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_security_principals called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_security_principals.')
            self.validate_parameters(sids=sids)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_security_principals.')
            _url_path = '/security-principals'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'sids': sids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_security_principals.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_security_principals.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_security_principals')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_security_principals.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SecurityPrincipals.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
