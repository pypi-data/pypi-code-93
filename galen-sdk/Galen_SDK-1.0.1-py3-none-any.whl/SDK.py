"""
Wrapper on the Galen API
"""

import requests
import json
import datetime


from galenSDK.enumeration.SortOrder import SortOrder
from galenSDK.enumeration.Role import Role
from galenSDK.enumeration.Status import Status

from galenSDK.exception.IllegalArgumentException import IllegalArgumentException
from galenSDK.exception.httpHandler import check_http_status

from galenSDK.model.CustomField import CustomField
from galenSDK.model.CustomFieldData import CustomFieldData
from galenSDK.model.DeviceCriteria import DeviceCriteria
from galenSDK.model.DeviceData import DeviceData
from galenSDK.model.DeviceDataView import DeviceDataView
from galenSDK.model.HelperFunctions import date_time_formater, date_formater
from galenSDK.model.OwnerFilter import OwnerFilter
from galenSDK.model.Page import Page
from galenSDK.model.PageInfo import PageInfo
from galenSDK.model.Practice import Practice
from galenSDK.model.Supplier import Supplier
from galenSDK.model.User import User

# Meta data
__author__ = "Nathanael Goza"
__copyright__ = "This software is copyrighted to Galen Data and is only available for licensees of the Galen Cloud(" \
                "TM) Product. Your right to use the software is limited to subscription period of the Galen Cloud. " \
                "License are non transferable unless agreed upon in the subscription contract. "
__credits__ = ["Nathanael Goza", "Abbas Dhilawala"]
__license__ = "Proprietary"
__version__ = "1.0.1"
__maintainer__ = "Nathanael Goza"
__email__ = "support@galendata.com"
__status__ = "Development"


# noinspection PyUnresolvedReferences
def date_time_data_formater(date_time: datetime):
    """
    Helper function to format datetime into data that can be used to save_data
    :param date_time: the datetime date to format
    :return: a string version of the datetime that will be accepted by the save(s)_data functions
    """
    return date_time_formater(date_time)


def date_data_formater(date: datetime):
    """
    Helper function to format dates into data that can be used to save_data
    :param date: the date date to format
    :return: a string version of the date that will be accepted by the save(s)_data functions
    """
    return date_formater(date)


class SDK:
    #     private User appUser;
    appUser = None
    #     private String apiUrl;
    apiURL = None
    #     private String authToken;
    authToken = None
    #     private String tenantDomainName;
    tenantDomainName = None
    #     private String apiVersion;
    apiVersion = None

    AUTHENTICATION_TOKEN_HEADER = "Authorization"
    AUTHENTICATION_TOKEN_HEADER_PREFIX = "Bearer "
    TENANT_DOMAIN_HEADER = "X-TENANT-DOMAIN"
    APP_TYPE_HEADER = "X-APP-TYPE"
    API_VERSION_HEADER = "X-API-VERSION"

    TENANT_GET_URL = "user/tenant"
    LOGIN_URL = "auth/login"
    REFRESH_WITH_MASTERTOKEN = "auth/refresh-token"

    DEVICEDATA_SAVE_URL = "data/devicedata"
    DEVICEDATA_BULK_SAVE_URL = "data/devicedata/bulk"
    DEVICEDATA_SAVE_MEDIA_URL = "data/devicedata/"
    DEVICEDATA_GET_URL = "data/devicedata"
    DEVICEDATA_GET_ADVANCED_URL = "data/devicedata-advanced"
    DEVICEDATA_GET_ADVANCED_URL_OWNER = "data/devicedata-advanced/owner"
    DEVICEDATA_GET_BYID_URL = "data/devicedata/"
    DEVICEDATA_GET_MEDIA_URL = "data/devicedata/"
    DEVICEDATA_GET_MEDIA_PROPERTY_URL = "data/devicedata-media/"
    DEVICEDATA_DELETE_URL = "data/"
    DEVICEDATA_DELETE_URL_SUFFIX = "/devicedata/delete"

    DEVICE_GET_URL = "user/device/"
    DEVICES_GET_URL = "user/device"

    DEVICEPROPSET_GET_URL = "user/devicepropertyset/"
    DEVICEPROPSETS_GET_URL = "user/devicepropertyset"

    DEVICEPROP_GET_URL = "user/deviceproperty/"
    DEVICEPROPS_GET_URL = "user/deviceproperty"

    PATIENTDEVICES_GET_URL = "user/patientdevice"
    PATIENTDEVICE_GET_URL = "user/patientdevice/"
    PATIENTDEVICE_ADD_LINK_URL = "user/patientdevice"
    PATIENTDEVICE_MOD_LINK_URL = "user/patientdevice"
    PATIENTDEVICE_DEL_LINK_URL = "user/patientdevice"

    USER_REGISTER_URL = "user/register"
    USER_ACTIVATE_URL = "user/activate"
    USER_REQUEST_PASSWORD_RESET_URL = "user/password/send-reset-code"
    USER_PASSWORD_RESET_URL = "user/password/reset"
    USER_CREATE_URL = "user/user/"
    USER_GET_URL = "user/user/"
    ME_USER_GET_URL = "user/me"
    USER_GET_CUSTOM_URL = "user/user-custom/"
    USER_UPDATE_URL = "user/user-custom"
    USER_UPDATE_PASS_URL = "user/updatepassword"
    USER_DELETE_URL = "user/user/"

    SUPPLIER_CREATE_URL = "user/supplier-custom/"
    SUPPLIER_GET_URL = "user/supplier/"
    SUPPLIER_UPDATE_URL = "user/supplier-custom"
    SUPPLIER_DELETE_URL = "user/supplier"

    PRACTICE_CREATE_URL = "user/practice-custom/"
    PRACTICE_GET_URL = "user/practice/"
    PRACTICE_UPDATE_URL = "user/practice-custom"
    PRACTICE_DELETE_URL = "user/practice/"

    CUSTOMDATA_GET_URL = "user/custom-field/data/"
    CUSTOMDATA_POST_URL = "user/custom-field/"

    # /**
    #  * The default API Version.
    #  */
    DEFAULT_API_VERSION = "3"

    def __init__(self, apiUrl: str, tenantDomainName: str, apiVersion: str = DEFAULT_API_VERSION,
                 authToken: str = None):
        """
        Creates an SDK object with API URL, tenant domain, API version and a specific auth token.
        :param apiUrl: the base URL for the API [Required]
        :param tenantDomainName: the domain name for the tenant on which the APIs will be called [Required]
        :param apiVersion: the version of the API [Default is 3]
        :param authToken: the auth token to use. [Optional]
        :raise:
            IllegalArgumentException: API URL is required
            IllegalArgumentException: Tenant domain name is required
            IllegalArgumentException: API version is required

        """
        if (apiUrl == None or apiUrl.strip() == ''):
            raise IllegalArgumentException("API URL is required")
        self.apiURL = apiUrl

        if (tenantDomainName == None or tenantDomainName.strip() == ''):
            raise IllegalArgumentException("Tenant domain name is required")
        self.tenantDomainName = tenantDomainName

        if (apiVersion == None or apiVersion.strip() == ''):
            raise IllegalArgumentException("API version is required")
        else:
            self.apiVersion = apiVersion

        self.apiURL = apiUrl
        if (apiUrl[-1] != "/"):
            self.apiURL += "/"

        self.tenantDomainName = tenantDomainName

        if (authToken != None and authToken.strip() == ""):
            self.authToken = authToken

    def login(self, emailAddress: str, password: str) -> User:
        """
        :param emailAddress: the email address to use for login. Required.
        :param password: password the password to use for the login. Required.
        :return: the logged in user if authentication is successful. [Does not return customdata within user]
        also sets the SDK object's current 'appUser' and 'authToken'

        :throws: Exception for any error. The following specific exceptions are thrown based on API response:
            412: {@link IllegalArgumentException}
            401: {@link AuthenticationFailureException}
            404: {@link ItemNotFoundException}
            500: {@link Exception}
        """

        url = self.apiURL + self.LOGIN_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            "emailAddress": emailAddress,
            "password": password
        }
        response = requests.request("POST", url, headers=my_headers, data=data)

        # SUCCESS
        if (check_http_status(response)):
            # grabs the authtoken and stores it in the sdk
            self.authToken = response.headers["Authorization"]

            # Make a user obj and return it
            userObj = User.from_json(response.json())
            self.appUser = userObj
            return self.appUser
        return None

    def login_with_master_token(self, master_token: str):
        """
        :param master_token: token to login with
        sets the auth token in the SDK to auth code received from cloud after logging in with token
        """
        url = self.apiURL + self.REFRESH_WITH_MASTERTOKEN
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        response = requests.request("POST", url, headers=my_headers, data=master_token)

        if (check_http_status(response)):
            # grabs the authtoken and stores it in the sdk
            self.authToken = response.headers["Authorization"]

    def logout(self) -> bool:
        """
        Logs a user out.
        :return: true if successful, false otherwise
        """
        self.authToken = None
        self.appUser = None
        return True

    def get_auth_token(self) -> str:
        """
        Gets the current authentication token.
        :return: the authentication token if one is available, None otherwise.
        """
        return self.authToken

    ##############################
    ####### Custom Data ##########
    ##############################
    def get_user_custom_data(self, userId: str) -> [CustomFieldData]:
        """
        :param userId: userId string. Required.
        :return: a list of custom data that belong to the user, or an empty list if the user did not have any customData
        """
        url = self.apiURL + self.CUSTOMDATA_GET_URL + userId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        jsonHolder = response.json()
        customDataHolder = []
        if check_http_status(response):
            for jh in jsonHolder:
                customDataHolder.append(CustomFieldData.from_json(jh))
            return customDataHolder
        return []

    def get_supplier_custom_data(self, supplierId: str) -> [CustomFieldData]:
        """
        :param supplierId: supplierId string. Required.
        :return: a list of custom data that belong to the supplier, or an empty list if the supplier did not have any customData
        """
        url = self.apiURL + self.CUSTOMDATA_GET_URL + supplierId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        jsonHolder = response.json()
        customDataHolder = []
        if check_http_status(response):
            for jh in jsonHolder:
                customDataHolder.append(CustomFieldData.from_json(jh))
            return customDataHolder

    def get_practice_custom_data(self, practiceId: str) -> [CustomFieldData]:
        """
        :param practiceId: practiceId string. Required.
        :return: a list of custom data that belong to the practice, or an empty list if the practice did not have any customData
        """
        url = self.apiURL + self.CUSTOMDATA_GET_URL + practiceId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        jsonHolder = response.json()
        customDataHolder = []
        if check_http_status(response):
            for jh in jsonHolder:
                customDataHolder.append(CustomFieldData.from_json(jh))
            return customDataHolder

    def create_field(self, field: CustomField) -> bool:
        """
        Creates a custom field
        :param field: Takes in a CustomField
        :return: True if created successfully, otherwise returns false
        """
        url = self.apiURL + self.CUSTOMDATA_POST_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        data = json.dumps(field.__dict__())
        response = requests.request("POST", url, headers=my_headers, data=data)

        if check_http_status(response):
            return True
        return

    def update_field(self, field: CustomField) -> bool:
        """
        Updates a custom field
        fieldId is the id of the field you want to update while the rest of the variables in the customField are how you want to update the field
        :param field: Takes in a CustomField
        :return: True if created successfully, otherwise returns false
        """
        url = self.apiURL + self.CUSTOMDATA_POST_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        data = json.dumps(field.__dict__())
        response = requests.request("PUT", url, headers=my_headers, data=data)

        if check_http_status(response):
            return True
        return False

    def delete_field(self, customFieldId: str):
        """
        Deletes a custom field
        :param customFieldId: Id of the field you want to delete
        :return: True if created successfully, otherwise returns false
        """
        url = self.apiURL + self.CUSTOMDATA_POST_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        data = {
            "customFieldId": customFieldId
        }

        response = requests.request("DELETE", url, headers=my_headers, params=data)

        if check_http_status(response):
            return True
        return False

    def get_field(self, customFieldId: str) -> CustomField:
        """
        Gets a custom field
        :param customFieldId: Id of the field you want to get
        :return: customField
        """
        url = self.apiURL + self.CUSTOMDATA_POST_URL + customFieldId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)  # , params=data)

        if check_http_status(response):
            return CustomField.from_json(response.json())

    ##############################
    ############ USER ############
    ##############################
    def get_current_user(self) -> User:
        """
        :return: The user that is logged into the SDK
        """
        url = self.apiURL + self.ME_USER_GET_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        if check_http_status(response):
            user_holder = User.from_json(response.json())
            user_holder.set_custom_data(self.get_user_custom_data(user_holder.get_user_id()))
            return user_holder
        return self.appUser

    def get_user(self, userId: str) -> User:
        """
        Retrieve a single user from the galen cloud given an ID
        :param userId: ID of the user. string. Required.
        :return: User object [Does not get custom data]
        """
        url = self.apiURL + self.USER_GET_URL + userId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        if check_http_status(response):
            user_holder = User.from_json(response.json())
            return user_holder

    def get_users(self, supplierId: str = None, practiceId: str = None, nameLike: str = None, emailAddress: str = None,
                  role: Role = None, pageInfo: PageInfo = None):
        """
        :param supplierId: the identifier of the supplier to which the requested users must belong. Optional.
        :param practiceId: the identifier of the practice to which the requested users must belong. Optional.
        :param nameLike: the pattern the user's full name must match. Optional.
        :param emailAddress: the email address of the user. Optional.
        :param role: the role of the user. Optional.
        :param pageInfo: the paging information for sorting and paging. Optional
            :PageInfo param pageNumber: the paging information for sorting and paging. Optional.
            :PageInfo param pageSize: the paged user list. Optional.
            :PageInfo param sortBy: what to sort the resultant Page output you want to access. attribute name. For device data this
                should be data.{propertycode}. String. Optional.
                Valid SortBy Values: "userId", "firstName", "middleName", "lastName", "emailAddress", "gender",
                    "dateOfBirth", "height", "weight", "status", "failedLoginAttempts", "lockOut", "lockOutDate",
                    "acceptedTermsOfUse", "language", "timeZone", "createdOn", "createdBy", "lastUpdatedOn", "lastUpdatedBy"
            :PageInfo param sortOrder: SortOrder of the resultant Page output you want. Default is Ascending. SortOrder. Optional.
        :return: Page object with the content of that page object being a list of json data for users
        :throws: Exception for any error. The following specific exceptions are thrown based on API response:
            412: {@link IllegalArgumentException}
            401: {@link AuthenticationFailureException}
            403: {@link IllegalAuthorizationException}
            404: {@link ItemNotFoundException}
            500: {@link Exception}
        """
        url = self.apiURL + self.USER_GET_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            'nameLike': nameLike,
            'supplierId': supplierId,
            'practiceId': practiceId,
            'nameLike': nameLike,
            'emailAddress': emailAddress,
            'role': role,
        }
        if pageInfo is not None:
            if pageInfo.get_current_page() is not None:
                if pageInfo.get_current_page() < 0:
                    raise Exception("Invalid Page Number | Must be greater than or equal to zero")
                data["pageNumber"] = pageInfo.get_current_page()
            if pageInfo.get_items_per_page() is not None:
                if pageInfo.get_items_per_page() < 0 or pageInfo.get_items_per_page() > 2147483647:
                    raise Exception("PageSize must be with in range: 0 to 2147483647")
                data["pageSize"] = pageInfo.get_items_per_page()
            if pageInfo.get_sort_by() is not None:
                data["sortBy"] = pageInfo.get_sort_by()
            if pageInfo.get_sort_order() is not None:
                data["sortOrder"] = SortOrder.to_string(pageInfo.get_sort_order())

        response = requests.request("GET", url, headers=my_headers, params=data)

        if check_http_status(response):
            # turns the [json user] content into [User]
            user_content = []
            page_of_users = Page.from_json(response.json())
            for content in page_of_users.get_content():
                user_content.append(User.from_json(content))

            page_of_users.set_content(user_content)
            return page_of_users

        if check_http_status(response):
            pageHolder = Page.from_json(response.json())
            return pageHolder

    def create_user(self, user: User, password: str):
        """
        Creates a user.
        :param user: the user object to create. Required.
        :param password: password for the user. Required.
        :return: true if successful, false otherwise.
        :throws: Exception for any error. The following specific exceptions are thrown based on API response:
            412: {@link IllegalArgumentException}
            401: {@link AuthenticationFailureException}
            403: {@link IllegalAuthorizationException}
            404: {@link ItemNotFoundException}
            500: {@link Exception}
        """
        url = self.apiURL + self.USER_CREATE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # takes a list of customData and turns them into data that can be easily be turned into json data
        customDataIn = []
        if user.get_custom_data() != None:
            for cd in user.get_custom_data():
                customDataIn.append(cd.__dict__())

        data = {
            "user": user.__dict__(),
            "password": password,
            "customData": customDataIn
        }
        response = requests.request("POST", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    def update_user(self, user: User):
        """
        Updates a user.
        :param user: the user object to create. userId of this object determines which user in the cloud it updates. Required.
        :return: true if successful, false otherwise.
        :throws: Exception for any error. The following specific exceptions are thrown based on API response:
            412: {@link IllegalArgumentException}
            401: {@link AuthenticationFailureException}
            403: {@link IllegalAuthorizationException}
            404: {@link ItemNotFoundException}
            500: {@link Exception}
        """
        url = self.apiURL + self.USER_UPDATE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # takes a list of customData and turns them into data that can be easily be turned into json data
        customDataIn = []
        if user.get_custom_data() != None:
            for cd in user.get_custom_data():
                customDataIn.append(cd.__dict__())

        data = {
            "user": user.__dict__()
            # "customData" : customDataIn
        }
        response = requests.request("PUT", url, headers=my_headers, data=json.dumps(data))
        if check_http_status(response):
            return True
        return False

    def delete_user(self, userId: str) -> bool:
        """
        Deletes a user given a UserId
        Credentials used to login needs to be high enough to execute this successfully
        :param userId: userId of the user that is going to be delete. Required.
        :return: True if successful, false otherwise
        :throws: Exception for any error
            error: user does not exist
        """
        url = self.apiURL + self.USER_DELETE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            "userId": userId
        }
        response = requests.request("DELETE", url, headers=my_headers, data=data)

        if check_http_status(response):
            return True
        return False

    def update_user_password(self, userId: str, currentPassword: str, newPassword: str,
                             newConfirmPassword: str) -> bool:
        """
        Updates the user password given the following parameters
        :param userId: user ID of the user. Required.
        :param currentPassword: current password of the user. Required.
        :param newPassword: new password of the user. Required.
        :param newConfirmPassword: new password of the user. Required
        :return: true if successful, false otherwise.
        :throws: Exception for any error
            InvalidArgumentException: password-was-reused-previously
            ItemNotFoundException: user-does-not-exists
            IllegalAuthorizationException: not-authorized
            others: WIP
        """
        url = self.apiURL + self.USER_UPDATE_PASS_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }
        data = {
            "userId": userId,
            "currentPassword": currentPassword,
            "newPassword": newPassword,
            "newConfirmPassword": newConfirmPassword

        }
        response = requests.request("PUT", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    ##############################
    ######### SUPPLIERS ##########
    ##############################

    def create_supplier(self, supplier: Supplier) -> bool:
        """
        :param supplier: Supplier to be created. Required.
        :return: true if successful, false otherwise.
        """
        url = self.apiURL + self.SUPPLIER_CREATE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # takes a list of customData and turns them into data that can be easily be turned into json data
        customDataIn = []
        if supplier.get_custom_data() != None:
            for cd in supplier.get_custom_data():
                customDataIn.append(cd.__dict__())

        data = {
            "customData": customDataIn,
            "supplier": supplier.__dict__()
        }
        response = requests.request("POST", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    def update_supplier(self, supplier: Supplier) -> bool:
        """
        :param supplier: supplier to update. SupplierId of this supplier will be matched with a supplier stored in the
            cloud. Everything else will be updated. Required.
        :return:  true if successful, false otherwise.
        """
        url = self.apiURL + self.SUPPLIER_CREATE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # takes a list of customData and turns them into data that can be easily be turned into json data
        customDataIn = []
        if supplier.get_custom_data() != None:
            for cd in supplier.get_custom_data():
                customDataIn.append(cd.__dict__())

        data = {
            "customData": customDataIn,
            "supplier": supplier.__dict__()
        }
        response = requests.request("PUT", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    def get_supplier(self, supplierId: str) -> Supplier:
        """
        Retrieve a single supplier from the galen cloud given an ID
        :param supplierId: ID of the supplier. string. Required.
        :return: Supplier object
        """
        url = self.apiURL + self.SUPPLIER_GET_URL + supplierId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        if check_http_status(response):
            supplierHolder = Supplier.from_json(response.json())
            return supplierHolder

    def get_suppliers(self, name: str = None, emailAddress: str = None, status: Status = None, pageInfo: PageInfo = None
                      ) -> Page:
        """
        Retrieve a page of suppliers that fit the given filters
        :param name: name of Supplier you want to get. String. Optional.
        :param emailAddress: emailAddress of Supplier you want to get. String. Optional.
        :param status: Status of Supplier you want to get. Status. Optional.
        :param pageInfo: the paging information for sorting and paging. Optional.
            :PageInfo param pageNumber: pageNumber of the resultant Page output you want to access. int. Optional.
            :PageInfo param pageSize: pageSizeof the resultant Page output you want to access. int. Optional.
            :PageInfo param sortBy: what to sort the resultant Page output you want to access. attribute name.
            For device data this should be data.{propertycode}. String. Optional.
                Valid sortBy Values: "supplierId", "tenantId", "name", "emailAddress", "status", "createdOn", "createdBy", "lastUpdatedOn", "lastUpdatedBy"
            :PageInfo param sortOrder: SortOrder of the resultant Page output you want. Default is Ascending. SortOrder. Optional.
        :return: Page with suppliers in the content portion of the page.
        """
        url = self.apiURL + self.SUPPLIER_GET_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        data = {
            "name": name,
            "emailAddress": emailAddress,
            "status": Status.to_string(status)
        }
        if pageInfo is not None:
            if pageInfo.get_current_page() is not None:
                if pageInfo.get_current_page() < 0:
                    raise Exception("Invalid Page Number | Must be greater than or equal to zero")
                data["pageNumber"] = pageInfo.get_current_page()
            if pageInfo.get_items_per_page() is not None:
                if pageInfo.get_items_per_page() < 0 or pageInfo.get_items_per_page() > 2147483647:
                    raise Exception("PageSize must be with in range: 0 to 2147483647")
                data["pageSize"] = pageInfo.get_items_per_page()
            if pageInfo.get_sort_by() is not None:
                data["sortBy"] = pageInfo.get_sort_by()
            if pageInfo.get_sort_order() is not None:
                data["sortOrder"] = SortOrder.to_string(pageInfo.get_sort_order())

        response = requests.request("GET", url, headers=my_headers, params=data)

        if check_http_status(response):
            pageHolder = Page.from_json(response.json())

            # turns json in context part of page to supplier obj
            supplier_list = []
            for sup_json in pageHolder.content:
                supplier_list.append(Supplier.from_json(sup_json))
            pageHolder.content = supplier_list

            return pageHolder

    def delete_supplier(self, supplierId: str) -> bool:
        """
        :param supplierId: ID of the supplier to be deleted.
        :return: True if successful, false otherwise.
        """
        url = self.apiURL + self.SUPPLIER_DELETE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            "supplierId": supplierId
        }
        response = requests.request("DELETE", url, headers=my_headers, data=data)

        if check_http_status(response):
            return True
        return False

    ##############################
    ######### PRACTICES ##########
    ##############################
    def create_practice(self, practice: Practice) -> bool:
        """
        Adds a practice to the galen cloud
        :param practice: practice object to be added. Required.
        :return: True if successful, otherwise return false
        """
        url = self.apiURL + self.PRACTICE_CREATE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # takes a list of customData and turns them into data that can be easily be turned into json data
        customDataIn = []
        if practice.get_custom_data() != None:
            for cd in practice.get_custom_data():
                customDataIn.append(cd.__dict__())

        data = {
            "customData": customDataIn,
            "practice": practice.__dict__()
        }
        response = requests.request("POST", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    def update_practice(self, practice: Practice) -> bool:
        """
        :param practice: practice that is being updated. PracticeID will determine which practice is updated. Required.
        :return: True if successful, otherwise return false
        """
        url = self.apiURL + self.PRACTICE_CREATE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # takes a list of customData and turns them into data that can be easily be turned into json data
        customDataIn = []
        if practice.get_custom_data() != None:
            for cd in practice.get_custom_data():
                customDataIn.append(cd.__dict__())

        data = {
            "customData": customDataIn,
            "practice": practice.__dict__()
        }
        response = requests.request("PUT", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    def get_practice(self, practiceId: str) -> Practice:
        """
        :param: practiceId. Id of the practice you want to fetch. Required.
        :return: The Practice that correlates to the practiceId.
        """
        url = self.apiURL + self.PRACTICE_GET_URL + practiceId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        if check_http_status(response):
            practiceHolder = Practice.from_json(response.json())
            return practiceHolder

    def get_practices(self, name: str = None, status: Status = None,
                      pageInfo: PageInfo = None) -> Page:  # emailAddress: str = None,
        """
        Retrieve a page of Practices that fit the given filters
        :param name: name of Practice you want to get. String. Optional.
        :param status: Status of Practice you want to get. Status. Optional.
        :param pageInfo: the paging information for sorting and paging. Optional.
            :PageInfo param pageNumber: the paging information for sorting and paging. Optional.
            :PageInfo param pageSize: the paged user list. Optional.
            :PageInfo param sortBy: what to sort the resultant Page output you want to access. attribute name. For device data this
                should be data.{propertycode}. String. Optional.
                Valid SortBy Values: "userId", "firstName", "middleName", "lastName", "emailAddress", "gender",
                    "dateOfBirth", "height", "weight", "status", "failedLoginAttempts", "lockOut", "lockOutDate",
                    "acceptedTermsOfUse", "language", "timeZone", "createdOn", "createdBy", "lastUpdatedOn", "lastUpdatedBy"
            :PageInfo param sortOrder: SortOrder of the resultant Page output you want. Default is Ascending. SortOrder. Optional.
        :return: Page with Practices in the content portion of the page.
        """
        url = self.apiURL + self.PRACTICE_GET_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        data = {
            'name': name,
            # "emailAddress": emailAddress,         # :param emailAddress: emailAddress of Practice you want to get. String. Optional.
            "status": Status.to_string(status)
        }
        if pageInfo is not None:
            if pageInfo.get_current_page() is not None:
                if pageInfo.get_current_page() < 0:
                    raise Exception("Invalid Page Number | Must be greater than or equal to zero")
                data["pageNumber"] = pageInfo.get_current_page()
            if pageInfo.get_items_per_page() is not None:
                if pageInfo.get_items_per_page() < 0 or pageInfo.get_items_per_page() > 2147483647:
                    raise Exception("PageSize must be with in range: 0 to 2147483647")
                data["pageSize"] = pageInfo.get_items_per_page()
            if pageInfo.get_sort_by() is not None:
                data["sortBy"] = pageInfo.get_sort_by()
            if pageInfo.get_sort_order() is not None:
                data["sortOrder"] = SortOrder.to_string(pageInfo.get_sort_order())

        response = requests.request("GET", url, headers=my_headers, params=data)

        if check_http_status(response):
            page_holder = Page.from_json(response.json())

            # turns json in context part of page to supplier obj
            practice_list = []
            for sup_json in page_holder.content:
                practice_list.append(Practice.from_json(sup_json))
            page_holder.content = practice_list

            return page_holder

    def delete_practice(self, practiceId: str) -> bool:
        """
        :param: practiceId. string. Required.
        :return: True if successful, otherwise return false
        """
        url = self.apiURL + self.PRACTICE_DELETE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            "practiceId": practiceId
        }
        response = requests.request("DELETE", url, headers=my_headers, data=data)

        if check_http_status(response):
            return True
        return False

    ##############################
    ####### Device Data ##########
    ##############################

    def save_data(self, deviceDataModelId: str, devicePropertySetId: str, data, deviceDataId: str = None,
                  ownerId: str = None):
        """
        :param deviceDataModelId: deviceDataModelId. Required.       [Device Data > manage Data > in URL]
        :param devicePropertySetId: devicePropertySetId. Required.   [Devices List > Edit > Data model edit > in URL]
        :param data: data in dictionary form. Property code as key and the value as the value. Required.
            example_data = {
               "propertyCode": desired_data
            }
            Depending on the data type there are different ways to input the desired_data:
                Date Time                   Date_time_formater(datetime_value)
                Json                        json.dumps(Dict)
                Height                      Number
                Blood Pressure              String with "systolic-pressure-value/diastolic-pressure-value"
                Dropdown List               String with the Dropdown Option as its innards ie) "Dropdown Value 3"
                Geographical Cooridnates    String that represents the coordinates
                Number                      Number
                Number Array                Number Array
                Temperature                 Number
                Text                        String
                Weight                      Number
                Xml                         String that represents the Xml
                Yes No                      Use True or False       (kinda acts like text but true/false works best)
                Date                        Date_formater(date_value)
        :param deviceDataId: ID of the deviceData. If not supplied, ID is auto generated. Optional.
        :param ownerId: ownerId. Optional.
        :return: Returns the Id of the created data
        """
        url = self.apiURL + self.DEVICEDATA_SAVE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }
        data = {
            "deviceDataId": deviceDataId,
            "deviceDataModelId": deviceDataModelId,
            "devicePropertySetId": devicePropertySetId,
            "ownerId": ownerId,
            "data": data
        }
        response = requests.request("POST", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return response.content.decode("utf-8")
        return " "

    def save_data_bulk(self, deviceDataModelId: str, devicePropertySetId: str,
                       dataList: [DeviceData]):  # , deviceDataId:str, ownerId:str
        """
        :param deviceDataModelId: deviceDataModelId. Required.       [Device Data > manage Data > in URL]
        :param devicePropertySetId: devicePropertySetId. Required.   [Devices List > Edit > Data model edit > in URL]
        :param dataList: List of Device Data. Required.
        :return: Returns a list of Ids of the created data
        """
        url = self.apiURL + self.DEVICEDATA_BULK_SAVE_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }

        # Formats the list of dicts for json handling
        dataListDicts = []
        for dl in dataList:
            dataListDicts.append(dl.__dict__())

        data = {
            # "deviceDataId": deviceDataId,
            "deviceDataModelId": deviceDataModelId,
            "devicePropertySetId": devicePropertySetId,
            "dataArray": dataListDicts
        }
        response = requests.request("POST", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            # turns byte data into a list of strings that represent the data ID
            data_id_list = []
            for data_id in response.content.decode("utf-8")[1:-1].replace("\"", "").split(","):
                data_id_list.append(data_id)
            return data_id_list
        return []

    def save_data_media(self, deviceDataModelId: str, deviceDataId: str, devicePropertyCode: str, mediaFile: bytes,
                        fileName: str) -> bool:
        """
        :param deviceDataModelId: The identifier of the device data model. Required.[Device Data > manage Data > in URL]
        :param deviceDataId: The device data record identifier. Required.
        :param devicePropertyCode: The property code of the property on which to save the media file. Required.
        :param mediaFile: byte Array of the media you want uploaded. Required.
        :param fileName: name of the mediaFile. Include the extension. Required.
        :return: True if successful, False otherwise
        """
        # print("saving data")
        url = self.apiURL + self.DEVICEDATA_GET_MEDIA_URL + deviceDataId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            "deviceDataModelId": deviceDataModelId,
            "propertyCode": devicePropertyCode
        }
        files = {
            'data': (fileName, mediaFile, "application/octet-stream")
        }
        response = requests.request("POST", url, headers=my_headers, files=files, params=data)

        if check_http_status(response):
            return True
        return False

    def get_data(self, deviceDataModelId: str, deviceDataId: str):
        """
        :param deviceDataModelId: deviceDataModelId. Required.
        :param deviceDataId: deviceDataId. Required.
        :return: device data correlating to the input params
        """
        url = self.apiURL + self.DEVICEDATA_GET_BYID_URL + deviceDataModelId + "/" + deviceDataId
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }
        data = {
            # "deviceId": deviceId,
            # "deviceDataId": deviceDataId
        }
        response = requests.request("GET", url, headers=my_headers)  # , data=data)

        if check_http_status(response):
            device_data = DeviceData.from_json(response.json())
            return device_data
        return None

    def get_datas(self, deviceDataModelId: str, startDateTime: datetime = None, endDateTime: datetime = None,
                  deviceCriteria: [DeviceCriteria] = None, propertyCodes: [str] = None, ownerFilter: OwnerFilter = None,
                  pageInfo: PageInfo = None) -> Page:
        """
        :param deviceDataModelId: deviceDataModelId. Required.
        :param startDateTime: Naive Date Time for start date. UTC/GMT time. Optional.
        :param endDateTime: Naive Date Time for end date. UTC/GMT time. Optional.
        :param deviceCriteria: WIP.
        :param propertyCodes: specific property code. List of strings. Optional.
        :param ownerFilter: OwnerFilter. Data attached to owners in the filter will be shown. Optional. WIP.
        :param pageInfo: Extra parameters to change what data is returned
        :return: Page with the contents variable being a list of device data
        """
        # This is different for V3 and V2 so Continue Here
        url = self.apiURL + self.DEVICEDATA_GET_ADVANCED_URL
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }
        query = {}
        if pageInfo is not None:
            if pageInfo.get_current_page() is not None:
                if pageInfo.get_current_page() < 0:
                    raise Exception("Invalid Page Number | Must be greater than or equal to zero")
                query["pageNumber"] = pageInfo.get_current_page()
            if pageInfo.get_items_per_page() is not None:
                if pageInfo.get_items_per_page() < 0 or pageInfo.get_items_per_page() > 2147483647:
                    raise Exception("PageSize must be with in range: 0 to 2147483647")
                query["pageSize"] = pageInfo.get_items_per_page()
            if pageInfo.get_sort_by() is not None:
                query["sortBy"] = pageInfo.get_sort_by()
            if pageInfo.get_sort_order() is not None:
                query["sortOrder"] = SortOrder.to_string(pageInfo.get_sort_order())

        device_criteria_dict_list = []  # parses deviceCriteria into a format that works with the rest api
        if deviceCriteria is not None:
            for dc in deviceCriteria:
                device_criteria_dict_list.append(dc.__dict__())
        data = {
            "deviceDataModelId": deviceDataModelId,
            "rangeStartDateTime": (date_time_formater(startDateTime) if startDateTime else ""),
            "rangeEndDateTime": (date_time_formater(endDateTime) if endDateTime else ""),
            "devicePropertyCodes": propertyCodes,  # ?
            "ownerFilter": (ownerFilter.__dict__() if ownerFilter is not None else None),
            "deviceCriteria": device_criteria_dict_list
        }
        response = requests.request("POST", url, headers=my_headers, params=query, data=json.dumps(data))

        if check_http_status(response):
            page_device_data = Page.from_json(response.json())

            # turning the json content field into DeviceData objects
            device_data_content = []
            for a in page_device_data.get_content():
                device_data_content.append(DeviceData.from_json(a))
            page_device_data.set_content(device_data_content)

            return page_device_data
        return None

    def get_datas_with_owner(self, deviceDataModelId: str, startDateTime: datetime = None, endDateTime: datetime = None,
                             deviceCriteria: [DeviceCriteria] = None, propertyCodes: [str] = None,
                             ownerFilter: OwnerFilter = None, pageInfo: PageInfo = None) -> Page:
        """
        WORK IN PROGRESS
        :param deviceDataModelId: deviceDataModelId. Required.
        :param startDateTime: Naive Date Time for start date. UTC/GMT time. Optional.
        :param endDateTime: Naive Date Time for end date. UTC/GMT time. Optional.
        :param deviceCriteria: WIP.
        :param propertyCodes: specific property code. List of strings. Optional.
        :param ownerFilter: OwnerFilter. Data attached to owners in the filter will be shown. Optional. WIP.
        :param pageInfo: Extra parameters to change what data is returned
        :return: Page with the contents variable being a list of DeviceDataView Objects
        """
        url = self.apiURL + self.DEVICEDATA_GET_ADVANCED_URL_OWNER
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }
        query = {}
        if pageInfo is not None:
            if pageInfo.get_current_page() is not None:
                if pageInfo.get_current_page() < 0:
                    raise Exception("Invalid Page Number | Must be greater than or equal to zero")
                query["pageNumber"] = pageInfo.get_current_page()
            if pageInfo.get_items_per_page() is not None:
                if pageInfo.get_items_per_page() < 0 or pageInfo.get_items_per_page() > 2147483647:
                    raise Exception("PageSize must be with in range: 0 to 2147483647")
                query["pageSize"] = pageInfo.get_items_per_page()
            if pageInfo.get_sort_by() is not None:
                query["sortBy"] = pageInfo.get_sort_by()
            if pageInfo.get_sort_order() is not None:
                query["sortOrder"] = SortOrder.to_string(pageInfo.get_sort_order())

        device_criteria_dict_list = []  # parses deviceCriteria into a format that works with the rest api
        if deviceCriteria is not None:
            for dc in deviceCriteria:
                device_criteria_dict_list.append(dc.__dict__())
        data = {
            "deviceDataModelId": deviceDataModelId,
            "rangeStartDateTime": date_time_formater(startDateTime),
            "rangeEndDateTime": date_time_formater(endDateTime),
            "devicePropertyCodes": propertyCodes,  # ?
            "ownerFilter": (ownerFilter.__dict__() if ownerFilter is not None else None),
            "deviceCriteria": device_criteria_dict_list
        }
        response = requests.request("POST", url, headers=my_headers, params=query, data=json.dumps(data))

        if check_http_status(response):
            page_device_data = Page.from_json(response.json())

            # turning the json content field into DeviceData objects
            # inspect owner to see what type of object needs to be created
            device_data_content = []
            for a in page_device_data.get_content():
                device_data_content.append(DeviceDataView.from_json(a))
            page_device_data.set_content(device_data_content)

            return page_device_data
        return None

    def get_data_media_for_property(self, deviceDataModelId: str, deviceDataId: str, propertyCode: str):
        """
        Gets the byte data for a specific media
        :param deviceDataModelId: deviceDataModelId of the data. Required.  [Devices > List > Edit > Id in url]
        :param deviceDataId: deviceDataId of the data. Required. [Device Data > Manage Data > Edit > Id in url]
        :param propertyCode: propertyCode of data. Required. [Devices > List > Edit > DataModel Edit > Property Code]
        :return: A list of bytes that are the data for a media file
        :throws: Exception for any error. The following specific exceptions are thrown based on API response:
            401: {@link AuthenticationFailureException}
            403: {@link Unauthorized Access}
            404: {@link ItemNotFoundException}
            412: {@link IllegalArgumentException}
            500: {@link Exception}
        """
        url = self.apiURL + self.DEVICEDATA_GET_MEDIA_PROPERTY_URL + deviceDataModelId + "/" + deviceDataId + "/" + propertyCode
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE"
        }

        response = requests.request("GET", url, headers=my_headers)

        if check_http_status(response):
            return response.content
        return None

    def delete_data(self, deviceDataModelId: str, deviceDataIds: [str] = [], ownerIds: [str] = None,
                    deviceCriteria: [DeviceCriteria] = None, rangeEndDateTime: datetime = None,
                    rangeStartDateTime: datetime = None):
        """
        Deletes Data given a modelId and constraints on which parameters to delete
        Be Very Careful To not Delete All Your Data
        :param deviceDataModelId: deviceDataModelId. Required.
        :param deviceDataIds: deviceDataIds. Optional.
        :param ownerIds: ownerIds. Optional.
        :param deviceCriteria: list of deviceCriteria. Optional.
        :param rangeEndDateTime: rangeEndDateTime. UTC/GMT time. Optional.
        :param rangeStartDateTime: rangeStartDateTime. UTC/GMT time. Optional.
        :return: True if successful, false otherwise 
        """
        url = self.apiURL + self.DEVICEDATA_DELETE_URL + deviceDataModelId + self.DEVICEDATA_DELETE_URL_SUFFIX
        my_headers = {
            self.TENANT_DOMAIN_HEADER: self.tenantDomainName,
            self.API_VERSION_HEADER: self.apiVersion,
            self.AUTHENTICATION_TOKEN_HEADER: self.authToken,
            self.APP_TYPE_HEADER: "DEVICE",
            "Content-Type": "application/json"
        }
        # formatting data properly
        device_criteria_list = []
        if deviceCriteria is not None:
            for dc in deviceCriteria:
                device_criteria_list.append(dc.__dict__())

        data = {
            "deviceDataModelId": deviceDataModelId,
            "deviceDataIds": deviceDataIds,
            "ownerIds": ownerIds,
            "deviceCriteria": device_criteria_list,
            "rangeEndDateTime": date_time_formater(rangeEndDateTime),
            "rangeStartDateTime": date_time_formater(rangeStartDateTime)
        }
        response = requests.request("POST", url, headers=my_headers, data=json.dumps(data))

        if check_http_status(response):
            return True
        return False

    #########################################################################################
    def get_practice_with_custom_data(self, practiceId: str) -> Practice:
        """
        :param: practiceId. Id of the practice you want to fetch. Required.
        :return: The Practice that correlates to the practiceId.
        """
        practice = self.get_practice(practiceId)
        practice.set_custom_data(self.get_practice_custom_data(practiceId))
        return practice

    def get_practices_with_custom_data(self, name: str = None, status: Status = None,
                                       pageInfo: PageInfo = None) -> Page:  # emailAddress: str = None,
        """
        Retrieve a page of Practices that fit the given filters
        :param name: name of Practice you want to get. String. Optional.
        :param status: Status of Practice you want to get. Status. Optional.
        :param pageInfo: the paging information for sorting and paging. Optional.
            :PageInfo param pageNumber: the paging information for sorting and paging. Optional.
            :PageInfo param pageSize: the paged user list. Optional.
            :PageInfo param sortBy: what to sort the resultant Page output you want to access. attribute name. For device data this
                should be data.{propertycode}. String. Optional.
                Valid SortBy Values: "userId", "firstName", "middleName", "lastName", "emailAddress", "gender",
                    "dateOfBirth", "height", "weight", "status", "failedLoginAttempts", "lockOut", "lockOutDate",
                    "acceptedTermsOfUse", "language", "timeZone", "createdOn", "createdBy", "lastUpdatedOn", "lastUpdatedBy"
            :PageInfo param sortOrder: SortOrder of the resultant Page output you want. Default is Ascending. SortOrder. Optional.
        :return: Page with Practices in the content portion of the page. Including any customData
        """
        practices_page = self.get_practices(name, status,
                                            pageInfo)  # emailAddress,         :param emailAddress: emailAddress of Practice you want to get. String. Optional.

        # makes a new content list to store all the practices now including customData and then fills it out
        content_with_custom_data = []
        for practice in practices_page.get_content():
            practice_holder = practice
            practice_holder.set_custom_data(self.get_practice_custom_data(practice_holder.get_practice_id()))
            content_with_custom_data.append(practice_holder)
        practices_page.set_content(content_with_custom_data)

        return practices_page

    def get_supplier_with_custom_data(self, supplierId: str) -> Supplier:
        """
        :param: supplierId. Id of the supplier you want to fetch. Required.
        :return: The Supplier that correlates to the supplierId.
        """
        supplier = self.get_supplier(supplierId)
        supplier.set_custom_data(self.get_supplier_custom_data(supplierId))
        return supplier

    def get_suppliers_with_custom_data(self, name: str = None, emailAddress: str = None, status: Status = None,
                                       pageInfo: PageInfo = None) -> Page:
        """
        Retrieve a page of suppliers that fit the given filters
        :param name: name of Supplier you want to get. String. Optional.
        :param emailAddress: emailAddress of Supplier you want to get. String. Optional.
        :param status: Status of Supplier you want to get. Status. Optional.
        :param pageInfo: the paging information for sorting and paging. Optional.
            :PageInfo param pageNumber: pageNumber of the resultant Page output you want to access. int. Optional.
            :PageInfo param pageSize: pageSizeof the resultant Page output you want to access. int. Optional.
            :PageInfo param sortBy: what to sort the resultant Page output you want to access. attribute name.
            For device data this should be data.{propertycode}. String. Optional.
                Valid sortBy Values: "supplierId", "tenantId", "name", "emailAddress", "status", "createdOn", "createdBy", "lastUpdatedOn", "lastUpdatedBy"
            :PageInfo param sortOrder: SortOrder of the resultant Page output you want. Default is Ascending. SortOrder. Optional.
        :return: Page with suppliers in the content portion of the page. Suppliers in page include custom data
        """
        supplier_page = self.get_suppliers(name, emailAddress, status, pageInfo)

        # makes a new content list to store all the practices now including customData and then fills it out
        content_with_custom_data = []
        for supplier in supplier_page.get_content():
            supplier_holder = supplier
            supplier_holder.set_custom_data(self.get_supplier_custom_data(supplier_holder.get_supplier_id()))
            content_with_custom_data.append(supplier_holder)
        supplier_page.set_content(content_with_custom_data)

        return supplier_page

    def get_user_with_custom_data(self, userId: str) -> User:
        """
        :param: userId. Id of the User you want to fetch. Required.
        :return: The User that correlates to the userId.
        """
        user = self.get_user(userId)
        user.set_custom_data(self.get_user_custom_data(userId))
        return user

    def get_users_with_custom_data(self, supplierId: str = None, practiceId: str = None, nameLike: str = None,
                                   emailAddress: str = None, role: Role = None, pageInfo: PageInfo = None) -> Page:
        """
        :param supplierId: the identifier of the supplier to which the requested users must belong. Optional.
        :param practiceId: the identifier of the practice to which the requested users must belong. Optional.
        :param nameLike: the pattern the user's full name must match. Optional.
        :param emailAddress: the email address of the user. Optional.
        :param role: the role of the user. Optional.
        :param pageInfo: the paging information for sorting and paging. Optional.
            :PageInfo param pageNumber: the paging information for sorting and paging. Optional.
            :PageInfo param pageSize: the paged user list. Optional.
            :PageInfo param sortBy: what to sort the resultant Page output you want to access. attribute name. For device data this
                should be data.{propertycode}. String. Optional.
                Valid SortBy Values: "userId", "firstName", "middleName", "lastName", "emailAddress", "gender",
                    "dateOfBirth", "height", "weight", "status", "failedLoginAttempts", "lockOut", "lockOutDate",
                    "acceptedTermsOfUse", "language", "timeZone", "createdOn", "createdBy", "lastUpdatedOn", "lastUpdatedBy"
            :PageInfo param sortOrder: SortOrder of the resultant Page output you want. Default is Ascending. SortOrder. Optional.
        :return: Page object with the content of that page object being a list of json data for users
        :throws: Exception for any error. The following specific exceptions are thrown based on API response:
            412: {@link IllegalArgumentException}
            401: {@link AuthenticationFailureException}
            403: {@link IllegalAuthorizationException}
            404: {@link ItemNotFoundException}
            500: {@link Exception}
        """
        user_page = self.get_users(supplierId, practiceId, nameLike, emailAddress, role, pageInfo)

        # makes a new content list to store all the practices now including customData and then fills it out
        content_with_custom_data = []
        for user in user_page.get_content():
            user_holder = user
            user_holder.set_custom_data(self.get_user_custom_data(user_holder.get_user_id()))
            content_with_custom_data.append(user_holder)
        user_page.set_content(content_with_custom_data)
        return user_page
