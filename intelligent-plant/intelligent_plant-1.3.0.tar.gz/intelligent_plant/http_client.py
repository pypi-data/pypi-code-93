"""This module implments a generic HTTP client and is used as the base of the App Store and Data Core clients"""
__author__ = "Ross Kelso"
__docformat__ = 'reStructuredText'

import urllib.parse as urlparse

import requests

from requests_ntlm import HttpNtlmAuth

class HttpClient(object):
    """A base HTTP client that has an authorization header and base url"""

    def __init__(self, base_url, **kwargs):
        """
        Initialise this HTTP client with an authorization header and base url.

        :param authorization_header: The value of the 'Authorization' HTTP header that should be sent with each request.
        :param base_url: The URL that relative URLs should be appended to.
        :type authorization_header: string
        :type base_url: string
        """
        self.base_url = base_url

        self.headers =  {}

        self.auth = None

        if ("authorization_header" in kwargs):
            self.headers = { 'Authorization': kwargs["authorization_header"] }

        if ("auth" in kwargs):
            self.auth = HttpNtlmAuth(kwargs["auth"]["user"], kwargs["auth"]["password"])

    def get(self, path, params):
        """
        Make a GET request to the specified path (relative to the client base url), with the specified parameters
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key
        :type path: string
        :type params: dict

        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        :raises: :class:`HTTPError`, if one occurred.
        """
        url = urlparse.urljoin(self.base_url, path)
        r = requests.get(url, params, headers=self.headers, auth=self.auth)

        r.raise_for_status()

        return r


    def post(self, path, params=None, data=None, json=None):
        """
        Make a POST request to the specified path (relative to the client base url), with the specified parameters
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key
        :param data: The data to be included in the request body.
        :type path: string
        :type params: dict

        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        :raises: :class:`HTTPError`, if one occurred.
        """
        url = urlparse.urljoin(self.base_url, path)
        r = requests.post(url, data, params=params, headers=self.headers, json=json, auth=self.auth)

        r.raise_for_status()

        return r

    def put(self, path, params=None, data=None, json=None):
        """
        Make a PUT request to the specified path (relative to the client base url), with the specified parameters
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key
        :param data: The data to be included in the request body.
        :type path: string
        :type params: dict

        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        :raises: :class:`HTTPError`, if one occurred.
        """

        url = urlparse.urljoin(self.base_url, path)
        r = requests.put(url, data, params=params, headers=self.headers, json=json, auth=self.auth)

        r.raise_for_status()

        return r

    def get_json(self, path, params=None):
        """
        Make a GET request to the specified path (relative to the client base url), with the specified parameters
        This method additionally parses the JSON response object.
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key.
        :type path: string
        :type params: dict

        :return: The parsed JSON response object.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        return self.get(path, params).json()

    def get_text(self, path, params=None):
        """
        Make a GET request to the specified path (relative to the client base url), with the specified parameters
        This method returns the text content of the response body.
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key.
        :type path: string
        :type params: dict

        :return: The conetent body as text.
        :raises: :class:`HTTPError`, if one occurred.
        """
        return self.get(path, params).text

    def post_text(self, path, params=None, data=None):
        """
        Make a POST request to the specified path (relative to the client base url), with the specified parameters
        This method returns the response content as text
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key
        :param data: The data to be included in the request body.
        :type path: string
        :type params: dict

        :return: The resposne body content as text
        :raises: :class:`HTTPError`, if one occurred.
        """
        return self.post(path, params=params, data=data).text

    def post_json(self, url, params=None, data=None, json=None):
        """
        Make a POST request to the specified path (relative to the client base url), with the specified parameters
        This method returns parses the reponse body as JSON.
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key
        :param data: The data to be included in the request body.
        :type path: string
        :type params: dict

        :return: The parsed response JSON object
        :raises: :class:`HTTPError`, if one occurred.
        """
        return self.post(url, params=params, data=data, json=json).json()

    def put_json(self, url, params=None, data=None, json=None):
        """
        Make a PUT request to the specified path (relative to the client base url), with the specified parameters
        This method returns parses the reponse body as JSON.
        :param path: The path to the target endpoint.
        :param params: The query string parameters as a dictionary with the parameter name as the key
        :param data: The data to be included in the request body.
        :type path: string
        :type params: dict

        :return: The parsed response JSON object
        :raises: :class:`HTTPError`, if one occurred.
        """
        return self.put(url, params=params, data=data, json=json).json()