"""This module implments a client for the Intelligent Plant App Store API"""
__author__ = "Ross Kelso"
__docformat__ = 'reStructuredText'

import time

import urllib

import requests

import intelligent_plant.data_core_client as data_core_client
import intelligent_plant.http_client as http_client

class AppStoreClient(http_client.HttpClient):
    """Access the Intelligent Plant Appstore API"""

    def __init__(self, access_token, refresh_token=None, expires_in=None, base_url = "https://appstore.intelligentplant.com/"):
        """
        Initialise an App Store Client
        :param access_token: The access token used to authenticate this client. 
            Get this by using the authorization code c#grant flow (for web servers) or
            the implicit grant flow (for clients e.g. native apps, JS web clients, Jupyter Notebook)
            Examples of this can be found in the "examples" folder and Jupyter notebook.
        :param refresh_token: The refresh token for this client (currently unused).
        :param base_url: The URL of the app store (optional, default value is "https://appstore.intelligentplant.com/").

        :return: An app store client that uses the provided access token for authorization.
        """
        self.access_token = access_token
        self.refresh_token = refresh_token

        if expires_in is None:
            self.expiry_time = None
        else:
            self.expiry_time = time.time() + expires_in

        http_client.HttpClient.__init__(self, base_url, authorization_header ="Bearer " + self.access_token)

    def get_data_core_client(self, data_core_url = None):
        """
        Get the data core client with the same authorization details as this app store client.
        :param data_core_url: The base URL for the data core API (optional, leaving it unspecified will determine the data core url relative to this client's base URL)

        :return: The data core client with the same authorization as this app store client.
        """
        data_core_url = urllib.parse.urljoin(self.base_url, "gestalt/datacore/") if data_core_url == None else data_core_url
        return data_core_client.DataCoreClient(base_url = data_core_url, authorization_header ="Bearer " + self.access_token)

    def get_user_info(self):
        """
        Get the authenticated user's user info from the app store.

        :return: The users infor as a parsed JSON object
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        return self.get_json("api/resource/userinfo")

    def get_user_balance(self):
        """
        Get the authenticated user's balance of credits.

        :return: The users balance as a float
        :raises: :class:`HTTPError`, if one occurred.
        """
        return float(self.get_text("api/resource/userbalance"))

    def debit_account(self, amount):
        """
        Debit the user's app store account.
        :param amount: The number of credits that should be debited from the user's account.

        :return: The transaction reference of the user's payment.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        params = {
            "debitAmount": amount
        }

        return self.post_json("api/resource/debit", params=params)

    def refund_account(self, transaction_ref):
        """
        Refund a transaction
        :param transaction_ref: The transaction reference of the transation you want to refund.

        :return: The requests response object.
        :raises: :class:`HTTPError`, if one occurred.
        """

        params = {
            "transactionRef": transaction_ref
        }

        return self.post("api/resource/refund", params=params)

    def refresh_session(self, app_id, app_secret):
        """
        Refresh the inustrial app store session using the refresh token.
        :param app_id: The ID of the app to authenticate under (found under Developer > Applications > Settings on the app store)
        :param app_secret: The secret of the app to authenticate under (found under Developer > Applications > Settings on the app store) :warn This should not be published.

        :return: A new instance of AppStoreClient with the refreshed access token.
        :raises: :class:`HTTPError`, if one occurred.
        """
        if self.refresh_token is None:
            raise ValueError("Cannot refresh. No refresh token specified.")

        path = "AuthorizationServer/OAuth/Token"
        url = urllib.parse.urljoin(self.base_url, path)
        r = requests.post(url, data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}, auth=requests.auth.HTTPBasicAuth(app_id, app_secret))

        r.raise_for_status()

        token_details = r.json()

        return token_details_to_client(token_details, self.base_url)
                    

def token_details_to_client(token_details, base_url="https://appstore.intelligentplant.com/"):
    """
    Convert access token details as provided by the app store API into an AppStoreClient.
    :param token_details: The token details as requested from the API.
    :param base_url: The app store base url (optional, default value is "https://appstore.intelligentplant.com/")

    :return: An instance of AppStoreClient using the speicifed acccess token.
    """
    access_token = token_details['access_token']
    refresh_token = token_details.get('refresh_token', None)
    expires_in = float(token_details['expires_in'])

    return AppStoreClient(access_token, refresh_token, expires_in, base_url)

def get_authorization_code_grant_flow_url(app_id, redirect_uri, scopes, base_url = "https://appstore.intelligentplant.com/"):
    """
    Get the url that the client should use for authorization code grant flow
    This grant flow should be used by web servers as it requires the app secret (which should not be made public).
    For information on the authorisation flow see: https://appstore.intelligentplant.com/wiki/doku.php?id=dev:app_store_developers
    :param app_id: The ID of the app to authenticate under (found under Developer > Applications > Settings on the app store)
    :param redirect_uri: The URI to redirect the user to after they log in with the authentication token (must be an authorized redirect URI in the app developer settings)
    :param scopes: A list of string that are the scopes the user is granting (e.g. "UserInfo" and "DataRead")
    :param base_url: The app store base url (optional, default value is "https://appstore.intelligentplant.com/")

    :return: The URL that the user should be redirected to to log in.
    """
    params = {
        'response_type': "code",
        'client_id': app_id,
        'redirect_uri': redirect_uri,
        'scope': " ".join(scopes)
    }
    url = base_url + "authorizationserver/oauth/authorize?" + urllib.parse.urlencode(params)

    return url

def complete_authorization_code_grant_flow(auth_code, app_id, app_secret, redirect_uri, base_url = "https://appstore.intelligentplant.com/"):
    """
    Complete logging in the user using authroization grant flow
    This grant flow should be used by web servers as it requires the app secret (which should not be made public).
    For information on the authorisation flow see: https://appstore.intelligentplant.com/wiki/doku.php?id=dev:app_store_developers
    :param auth_code: The code that was returned to the redirect URI after the user logged in.
    :param app_id: The ID of the app to authenticate under (found under Developer > Applications > Settings on the app store)
    :param app_secret: The secret of the app to authenticate under (found under Developer > Applications > Settings on the app store) :warn This should not be published.
    :param redirect_uri: Sn authorized redirect URI in the app developer settings
    :param base_url: The app store base url (optional, default value is "https://appstore.intelligentplant.com/")

    :return: An app store client with the access token specified
    """
    url = base_url + "authorizationserver/oauth/token"

    params = {
        'grant_type': "authorization_code",
        'code': auth_code,
        'client_id': app_id,
        'client_secret': app_secret,
        'redirect_uri': redirect_uri
    }
    
    r = requests.post(url, params)

    r.raise_for_status()

    token_details = r.json()

    return token_details_to_client(token_details, base_url)
  
def get_implicit_grant_flow_url(app_id, redirect_url, scopes, base_url = "https://appstore.intelligentplant.com/"):
    """
    Get the url that the client should use for implicit grant flow.
    This grant flow can be used by native applications and clients, as it doesn't require the app secret.
    For security reasons the PKCE grant flow is recommended over the implicit grant flow.
    For information on the authorisation flow see: https://appstore.intelligentplant.com/wiki/doku.php?id=dev:app_store_developers
    :param app_id: The ID of the app to authenticate under (found under Developer > Applications > Settings on the app store)
    :param redirect_url: The URL to redirect the user to after they log in with the access token (must be an authorized redirect URI in the app developer settings)
    :param scopes: A list of string that are the scopes the user is granting (e.g. "UserInfo" and "DataRead")
    :param base_url: The app store base url (optional, default value is "https://appstore.intelligentplant.com")

    :return: The URL that the user should be redirected to to log in.
    """
    params = {
        'response_type': "token",
        'client_id': app_id,
        'redirect_uri': redirect_url,
        'scope': " ".join(scopes)
    }

    url = base_url + "authorizationserver/oauth/authorize?" + urllib.parse.urlencode(params)

    return url

def get_pkce_url(app_id, redirect_uri, scopes, code_challenge, code_challenge_method, base_url = "https://appstore.intelligentplant.com/"):
    """
    Get the url that the client should use for the PKCE grant flow
    This grant flow should be used by web servers as it requires the app secret (which should not be made public).
    :param app_id: The ID of the app to authenticate under (found under Developer > Applications > Settings on the app store)
    :param redirect_uri: The URI to redirect the user to after they log in with the authentication token (must be an authorized redirect URI in the app developer settings)
    :param scopes: A list of string that are the scopes the user is granting (e.g. "UserInfo" and "DataRead")
    :param code_challenge: A PKCE code challenge. This should be generated from the verifier using sha256. A challenge verifier pair can be generated with the pkce package.
    :param code_challenge_method: The method used to generate the code challenge from the code verifier, should be 'Plain' or 'S256' for sha256 (recommended).
    :param base_url: The app store base url (optional, default value is "https://appstore.intelligentplant.com/")
    :return: The URL that the user should be redirected to to log in.
    """
    params = {
        'response_type': "code",
        'client_id': app_id,
        'redirect_uri': redirect_uri,
        'scope': " ".join(scopes),
        'code_challenge': code_challenge,
        'code_challenge_method': code_challenge_method
    }
    
    url = base_url + "authorizationserver/oauth/authorize?" + urllib.parse.urlencode(params)

    return url

def complete_pkce(auth_code, app_id, redirect_uri, code_verifier, base_url = "https://appstore.intelligentplant.com/"):
    """
    Complete logging in the user using the PKCE grant flow
    This grant flow should be used by web servers as it requires the app secret (which should not be made public).
    :param auth_code: The code that was returned to the redirect URI after the user logged in.
    :param app_id: The ID of the app to authenticate under (found under Developer > Applications > Settings on the app store)
    :param redirect_uri: An authorized redirect URI in the app developer settings
    :param code_verifier: The code verifier that was used to generate the code_challenge in the first step of the flow
    :param base_url: The app store base url (optional, default value is "https://appstore.intelligentplant.com/")
    :return: An app store client with the access token specified
    """
    url = base_url + "authorizationserver/oauth/token"

    params = {
        'grant_type': "authorization_code",
        'code': auth_code,
        'client_id': app_id,
        'code_verifier': code_verifier,
        'redirect_uri': redirect_uri
    }
    
    r = requests.post(url, params)

    r.raise_for_status()

    token_details = r.json()

    return token_details_to_client(token_details, base_url)