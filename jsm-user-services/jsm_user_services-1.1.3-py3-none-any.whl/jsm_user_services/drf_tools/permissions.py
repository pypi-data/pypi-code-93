"""
Module with useful user permissions classes meant to be used with Django Rest Framework.
"""

import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import requests
from django.conf import settings
from jsm_user_services.drf_tools.helpers import AllowClassBehaviorAsFunction
from jsm_user_services.drf_tools.helpers import is_exception_related_to_api_exception
from jsm_user_services.exception import IncorrectTypePermissionConfiguration
from jsm_user_services.services.google import perform_recaptcha_validation
from jsm_user_services.services.user import get_user_data_from_server
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.request import Request

logger = logging.getLogger(__name__)


class JSMUserBasePermission(permissions.BasePermission):
    """
    Base class for JSM user permissions. Implements methods for validating requests against
    the user micro service so that any type of permission can be carried out (role, status, etc).
    """

    APPEND_USER_DATA = getattr(settings, "JSM_USER_SERVICES_DRF_APPEND_USER_DATA", True)
    USER_DATA_ATTR_NAME = getattr(settings, "JSM_USER_SERVICES_DRF_REQUEST_USER_DATA_ATTR_NAME", "user_data")
    USER_SERVICE_NOT_AUTHORIZED_CODES = (401, 403, 404)

    @classmethod
    def _retrieve_user_data(cls, request: Request) -> Dict:
        try:
            user_data = getattr(request, cls.USER_DATA_ATTR_NAME)
        except AttributeError:
            user_data = get_user_data_from_server()

        return user_data

    @classmethod
    def _validate_request_against_user_service(cls, request: Request, append_user_data_to_request: bool = True) -> Dict:
        """
        Gets valid user_data from the User micro service.
        """
        try:
            user_data: Dict = cls._retrieve_user_data(request)

            if append_user_data_to_request:
                setattr(request, cls.USER_DATA_ATTR_NAME, user_data)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in cls.USER_SERVICE_NOT_AUTHORIZED_CODES:
                return {}

            raise

        return user_data

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Abstract method that must be implemented by children classes.
        """
        raise NotImplementedError("This method must be overridden!")


class StatusBasedPermission(JSMUserBasePermission):
    """
    Base class for the status-based permissions. Implements methods for validating requests against
    the user micro service and an utility method that asserts that the user has the appropriate status.
    """

    @classmethod
    def _validate_user_status(cls, request: Request, allowed_status: List[str]):
        """
        Validates if the user has the appropriate status against the allowed status.
        """
        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )

        if "status" not in user_data:
            return False

        return user_data["status"] in allowed_status


class RoleBasedPermission(JSMUserBasePermission):
    """
    Base class for the role-based permissions. Implements methods for validating requests against
    the user micro service and an utility method that asserts that the user has the appropriate role.
    """

    @classmethod
    def _validate_user_role(cls, request: Request, allowed_roles: List[str]):
        """
        Validates if the user has the appropriate role against the allowed roles.
        """
        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )
        user_roles: List[str] = user_data.get("roles", [])

        if not user_roles:
            return False

        return any([user_role in allowed_roles for user_role in user_roles])


class ProfessionalUserPermission(RoleBasedPermission):
    """
    Permission that allows only users with the role 'professional'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is a professional.
        """
        return self._validate_user_role(request, allowed_roles=["professional"])


class EmployeeOrManagerUserPermission(RoleBasedPermission):
    """
    Permission that allows only users with the role 'employee' or 'manager'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is either an employee or manager.
        """
        return self._validate_user_role(request, allowed_roles=["employee", "manager"])


class EmployeeOnlyUserPermission(RoleBasedPermission):
    """
    Permission that allows only users with the role 'employee'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an employee.
        """
        return self._validate_user_role(request, allowed_roles=["employee"])


class OwnerUserPermission(RoleBasedPermission):
    """
    Permission that allows only users with the role 'owner'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an owner.
        """
        return self._validate_user_role(request, allowed_roles=["owner"])


class IndustrySellerUserPermission(RoleBasedPermission):
    """
    Permission that allows only users with the role 'industry-seller'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an industry seller.
        """
        return self._validate_user_role(request, allowed_roles=["industry-seller"])


class AnyLoggedUserPermission(RoleBasedPermission):
    """
    Permission that allows users to access the requested resource regardless
    of their roles as long as they have a VALID, NON EXPIRED JSM JWT.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is just logged in with a valid jwt (non expired).
        """
        return self._validate_user_role(request, allowed_roles=["professional", "employee", "manager", "owner"])


class ActiveUserPermission(StatusBasedPermission):
    """
    Permission that allows only users which the status is 'active'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user status is 'active'.
        """
        return self._validate_user_status(request, allowed_status=["active"])


class PendingValidationUserPermission(StatusBasedPermission):
    """
    Permission that allows only users which the status is 'pending-validation'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user status is 'pending-validation'.
        """
        return self._validate_user_status(request, allowed_status=["pending-validation"])


class GoogleRecaptchaPermission(permissions.BasePermission, AllowClassBehaviorAsFunction):
    """
    A permission class which checks if the request is authorized by Google Recaptcha V3.

    In order to use it, the request must have the key "g_recaptcha_response" or "g-recaptcha-response" on the request's
    body or header. Otherwise the request won't be authorized without even checking it on Google.

    Just be aware that a header with underscore is not allowed. So do not use the key "g_recaptcha_response"
    on the header.
    """

    def __init__(self, exception_in_case_of_failed: Optional[Union[APIException, Type[APIException]]] = None):
        """
        Sets the default value for "exception_in_case_of_failed_verification" property. It will be used to return
        a custom response, in case of this permission fails.
        This exception must inherit APIException, from rest_framework.exceptions, otherwise it will be ignored.
        """

        self.exception_in_case_of_failed_verification = exception_in_case_of_failed

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Retrieves the Google data on the request and then performs a request to Google, in order to check if the
        received data is valid or not.
        """

        g_recaptcha_response = self._retrieve_g_recaptcha_response(request)
        use_received_exception = is_exception_related_to_api_exception(self.exception_in_case_of_failed_verification)

        # preventing an unnecessary request to Google, since key is not defined
        if not g_recaptcha_response:
            if use_received_exception:
                raise self.exception_in_case_of_failed_verification
            return False

        google_response: bool = perform_recaptcha_validation(g_recaptcha_response)

        if not google_response and use_received_exception:
            # raising an APIException that will return the customized response
            raise self.exception_in_case_of_failed_verification

        return google_response

    @classmethod
    def _retrieve_g_recaptcha_response(cls, request: Request) -> Optional[str]:
        """
        Lookup on the request's body and header in order to retrieve the recaptcha key.

         If the same key is present on header and body, the header data will be overridden by the body value.
         Also, if both keys are present, the priority is "g_recaptcha_response" over "g-recaptcha-response".
        """

        expected_keys = ["g_recaptcha_response", "g-recaptcha-response"]

        for key in expected_keys:
            key_value = request.data.get(key) or request.headers.get(key)
            if key_value:
                return key_value


class IsUserAllowedToPermission(JSMUserBasePermission, AllowClassBehaviorAsFunction):
    """
    A permission class which checks if user is authorized to execute an action based on 'not_allowed_to' parameter.
    Implements methods for validating requests against the user micro service and an utility method that asserts
    the user has the appropriate permission for to do, or not to do, a determined action.

    Example:
        class SomeAwesomeView():
            permission_classes = [
                IsUserAllowedToPermission(
                    ["redeem", "score"], full_match=False, exception_in_case_of_failed=CustomExceptionNotAllowedTo
                )
            ]

        In this example, the custom exception should be implemented into your own project.
    """

    def __init__(
        self,
        not_allowed_to: List[str],
        full_match: bool = False,
        exception_in_case_of_failed: Optional[Union[APIException, Type[APIException]]] = None,
    ):
        """
        Sets the default value for "exception_in_case_of_failed_verification" property. It will be used to return
        a custom response, in case of this permission fails. This exception must inherit APIException,
        from rest_framework.exceptions, otherwise it will be ignored.

        Full match property indicates that user data must contains all the 'not_allowed_to' defined parameters.
        On the other hand, if full match is equal to False, the permission class checks
        if user data contains any of the 'not_allowed_to' parameters.
        """

        self.exception_in_case_of_failed_verification = exception_in_case_of_failed
        self.full_match = full_match

        if not isinstance(not_allowed_to, list):
            logger.error(
                f"Permission class 'IsUserAllowedToPermission' expected 'List[str]', got  {type(not_allowed_to)}"
            )
            raise IncorrectTypePermissionConfiguration(f"Expected type 'List[str]', got {type(not_allowed_to)} instead")

        self.not_allowed_to = not_allowed_to

    @classmethod
    def _verify_if_user_should_be_allowed(
        cls, request: Request, not_allowed_actions: List[str], full_match: bool
    ) -> bool:
        """
        Validates 'not_allowed_to' user parameter against the 'not_allowed_actions' permission class parameter.
        """

        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )
        user_not_allowed_to: List[str] = user_data.get("not_allowed_to", [])

        set_from_not_allowed_actions = set(not_allowed_actions)
        set_from_user_not_allowed_to = set(user_not_allowed_to)
        intersected_actions = set_from_not_allowed_actions.intersection(set_from_user_not_allowed_to)

        if not (user_not_allowed_to or intersected_actions):
            return True

        if full_match:
            return len(intersected_actions) != len(set_from_not_allowed_actions)
        return not bool(intersected_actions)

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user hasn't an action restriction against the 'not_allowed_to' permission class parameter.
        """

        use_received_exception: bool = is_exception_related_to_api_exception(
            self.exception_in_case_of_failed_verification
        )

        is_allowed: bool = self._verify_if_user_should_be_allowed(
            request, not_allowed_actions=self.not_allowed_to, full_match=self.full_match,
        )

        if use_received_exception and not is_allowed:
            raise self.exception_in_case_of_failed_verification

        return is_allowed
