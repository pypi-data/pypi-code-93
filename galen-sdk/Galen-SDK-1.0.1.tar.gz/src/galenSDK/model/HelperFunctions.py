"""
Helper Function Class

Has functions to help with different parts of the SDK
"""

import datetime
from galenSDK.enumeration.Scope import Scope


# some imports are in functions to avoid the problem of circular imports

class HelperFunctions:
    pass


def url_helper(self, url: str, key, value) -> str:
    """
    Helps format urls given a base url, key value and value
    example: url.com?Key=Value      Helper function
    :param url: baseurl
    :param key: key Value of url extension
    :param value: value that matches the keyvalue
    :return: url with key/value pair added in
    """
    if value is None:
        return url
    if url.endswith("/"):
        url += "?" + key + "=" + value.__str__()
        return url
    else:
        url += "&" + key + "=" + value.__str__()
        return url


def date_time_formater(date_time: datetime) -> str:
    """
    Helper function to format datetime properly to interact with galen cloud
    :param date_time: datetime to format
    :return: a string that represents the datetime
    """
    if date_time is None:
        return None
    return date_time.__str__().replace(" ", "T")


def date_formater(date: datetime) -> str:
    """
    Helper function to format datetime properly to interact with galen cloud
    :param date: datetime to format
    :return: a string that represents the datetime
    """
    if date is None:
        return None
    return date.__str__() + "T00:00:00.000"


def str_to_date_time(string_date_time: str) -> datetime:
    """
    Helper function to format datetime properly to interact with galen cloud
    :param string_date_time: datetime string to format
    :return: a datetime that represents the strings
    """
    if string_date_time is None:
        return None
    if "." not in string_date_time:
        return datetime.datetime.strptime(string_date_time, '%Y-%m-%dT%H:%M:%S')
    return datetime.datetime.strptime(string_date_time, '%Y-%m-%dT%H:%M:%S.%f')


def parse_owner_helper(scope: Scope, owner_dict):
    # imports are here to avoid circular imports
    from galenSDK.model.User import User
    from galenSDK.model.Supplier import Supplier
    from galenSDK.model.Practice import Practice
    from galenSDK.model.Tenant import Tenant
    """
    Helper function to parse scope and owner properly
    :param scope: scope enum that represents the type of object to be created
    :param owner_dict: dict that will be the basis of the object
    :return: an object of type denoted in scope with the variables being taken from the owner_dict
    """
    if scope is None:
        return None
    if owner_dict is None:
        return None
    if scope == Scope.PATIENT:
        return User.from_json(owner_dict)
    if scope == Scope.SUPPLIER:
        return Supplier.from_json(owner_dict)
    if scope == Scope.PRACTICE:
        return Practice.from_json(owner_dict)
    if scope == Scope.TENANT:
        return Tenant.from_json(owner_dict)
    return None
