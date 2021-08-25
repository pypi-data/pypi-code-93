from os import error
import requests, json, jwt

import random
from datetime import datetime
import base64, hashlib

from typing import Tuple, Union, Dict

from .loginid import LoginID

class LoginIdManagement(LoginID):
    def __init__(self, client_id: str, private_key: str, base_url: Union[str, None]=None) -> None:
        """This server SDK can be used with a management application and requires an API credential to be assigned to that integration. 
        All calls made from this SDK are intended to be backend-to-backend calls, as the operations are sensitive.

        Args:
            client_id (str): Client ID as per the value provided on the dashboard
            private_key (str): Private key of the API credential assigned to the application on the dashboard.
            base_url (Union[str, None], optional): Base URL where requests should be made (if specifying which environment is being used). Defaults to the LoginID production URL if not given (`None`)

        Example::

            from loginid import LoginIdManagememnt
            lManagement = LoginIdManagement(CLIENT_ID, PRIVATE_KEY)
        """
        base_url = base_url or "https://usw1.loginid.io/"
        super().__init__(client_id, private_key, base_url=base_url)

    # User Management    
    def getUserId(self, username: str) -> Tuple[Union[Exception,int], Dict]:
        """Get the user ID from username

        Args:
            username (str): The username

        Returns:
            tuple: a 2-element tuple with
            
                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): the user id if no errors, else the JSON response
        """
        try:
            url = self._base_url + "/manage/users/retrieve"

            headers = {
                "Content-type": "application/json",
                "x-client-id": self._client_id,
                "Authorization": "Bearer " + self.generateServiceToken("users.retrieve")
            }

            payloads = {
                "username": username
            }

            r = requests.post(url, data=json.dumps(payloads), headers=headers)

            if (r.status_code != 200):
                return r.status_code, r.json()
            
            return None, r.json()['id']
        except Exception as e:
            return e, {'error': str(e)}

    def deleteByUsername(self, username: str) -> Tuple[Union[int, Exception], bool]:
        """Delete a User by the username

        Args:
            username (str): the username to be deleted

        Returns:
            tuple: a 2-element tuple with
            
                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): success message if user deleted successfully, else the JSON response
        """
        try:
            url = self._base_url + "/manage/users/delete"
            headers = {
                "Content-type": "application/json",
                "x-client-id": self._client_id,
                "Authorization": "Bearer " + self.generateServiceToken("users.delete")
            } 

            payloads = {
                "username": username
            }

            r = requests.post(url=url, data=json.dumps(payloads), headers=headers)

            if r.status_code != 204:
                print(r.status_code)
                return r.status_code, r.json()
            return None, {"message": f"User {username} deleted"}
        except Exception as e:
            return e, {'error':str(e)}

    def deleteByUserId(self, user_id: str) -> Tuple[Union[None, Exception], Dict]:
        """Delete a user by user Id

        Args:
            user_id (str): the user id to be deleted

        Returns:
            tuple: a 2-element tuple with
            
                - **error** (*Union[int, Exception]*): HTTP error code if any, Exception for unknown error, `None` if no errors
                - **response** (*Union[str, Dict]*): success message if user deleted successfully, else the JSON response
        """
        try:
            url = f"{self._base_url}/manage/users/{user_id}"

            headers = {
                "Content-type":"application/x-www-form-urlencoded",
                "Authorization": "Bearer " + self.generateServiceToken("users.delete"),
                "x-client-id": self._client_id
            }

            r = requests.delete(url, headers=headers)
            
            if r.status_code != 204:
                return r.status_code, r.json()
            return None, {'message': f'user with id {user_id} deleted'}
        except Exception as e:
            return e, {'error': str(e)}

    def activateUserById(self, user_id: str) -> Tuple[Union[None, Exception], Dict]:
        """Activate a previously deactivated user

        Args:
            user_id (str): the user id to be activated

        Returns:
            tuple: a 2-element tuple with
            
                - **error** (*Union[int, Exception]*): HTTP error code if any, Exception for unknown error, `None` if no errors
                - **response** (*Union[str, Dict]*): user profiles if no error, else the JSON response
        """
        try:
            url = f"{self._base_url}/manage/users/{user_id}/activate"

            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Authorization": "Bearer " + self.generateServiceToken("users.activate"),
                "x-client-id": self._client_id
            }

            r = requests.put(url, headers=headers)

            if r.status_code != 200:
                return r.status_code, r.json()

            return None, r.json()
        except Exception as e:
            return e, {'error': str(e)}

    def deactivateUserById(self, user_id: str) -> Tuple[Union[None, Exception], Dict]:
        """Deactivate a currently active user

        Args:
            user_id (str): the user id to be deactivated

        Returns:
            tuple: a 2-element tuple with
            
                - **error** (*Union[int, Exception]*): HTTP error code if any, Exception for unknown error, `None` if no errors
                - **response** (*Union[str, Dict]*): user profiles if no error, else the JSON response
        """
        try:
            url = f"{self._base_url}/manage/users/{user_id}/deactivate"

            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Authorization": "Bearer " + self.generateServiceToken("users.deactivate"),
                "x-client-id": self._client_id
            }

            r = requests.put(url, headers=headers)

            if r.status_code != 200:
                return r.status_code, r.json()

            return None, r.json()         
        except Exception as e:
            return e, {'error': str(e)}

    # Code APIs
    def generateCode(self, user_id: str, codeType: str, 
                     codePurpose: str, isAuthorized: bool) -> Tuple[Union[None,int], Dict]:
        """Generate a code

        Args:
            user_id (str): The user_id for the code
            codeType (str): The code type
            codePurpose (str): The purpose of the code
            isAuthorized (bool): Whether the code authorizes the user or not


        Returns:
            tuple: a 2-element tuple with 
            
                - **error** (*int*): HTTP error code, `None` if no errors
                - **response** (*dict*): the response body from code generation request
        """
        url = f"{self._base_url}/codes/{codeType}/generate"

        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + self.generateServiceToken("codes.generate")
        }
        payloads = dict(
            client_id=self._client_id,
            user_id=user_id,
            purpose=codePurpose,
            authorize=isAuthorized
        )

        r = requests.post(url, data=json.dumps(payloads), headers=headers)

        if (r.status_code != 200):
            return r.status_code, r.json()

        return None, r.json()

    def authorizeCode(self, user_id: str, code: str, 
                      codeType: str, codePurpose: str) -> Tuple[Union[None,int], Dict]:
        """Authorize a given code

        Args:
            user_id (str): The user_id associate with the code
            code (str): The code that needs authorization
            codeType (str): The type of the code
            codePurpose (str): The purpose of the code

        Returns:
            tuple: a 2-element tuple containing

                - **error** (*int*): The HTTP error, `None` if no errors
                - **response** (*dict*): The response body from code authorization
        """
        try:
            assert self.isValidCodeType(codeType), f"{codeType} is not a valid code type"

            url = f"{self._base_url}/codes/{codeType}/authorize"

            headers = {
                "Content-type": 'application/json',
                'Authorization': 'Bearer ' + self.generateServiceToken('codes.authorize')
            }

            payloads = dict(
                client_id=self._client_id,
                user_id=user_id,
                purpose=codePurpose,
                code=code
            )

            r = requests.post(url, data=json.dumps(payloads), headers=headers)

            # TODO: throw a proper error here
            if (r.status_code != 200):
                return r.status_code, r.json()

            return None, r.json()
        except Exception as e:
            return e, {'message': str(e)}
    
    def invalidateAllCodes(self, user_id: str, codeType: str, codePurpose: str) -> int:
        """Invalidate the given code

        Args:
            user_id (str): the user ID
            codeType (str): code type
            codePurpose (str): the purpose of the code 

        Returns:
            int: `0` if the code is successfully invalidated, `-1` for unknown error, otherwise HTTP response status code  
        """
        try:
            assert self.isValidCodeType(codeType)

            url = f'{self._base_url}/codes/{codeType}/invalidate-all'

            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + self.generateServiceToken("codes.invalidate")
            }

            payloads = dict(
                client_id=self._client_id,
                user_id=user_id,
                purpose=codePurpose,
            )
            r = requests.post(url, data=json.dumps(payloads), headers=headers)
            
            if r.status_code != 200: return r.status_code

            return 0
        except:
            return -1

    # Credentials
    def getCredentials(self, user_id: str) -> Tuple[Union[int, Exception], Dict]:
        """Get an exhaustive list of credentials for a given user

        Args:
            user_id (str): User ID of the end user who you would like to get the list of credentials

        Returns:
            tuple: A 2-element tuple consisting of

                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): User's credentials if no error, else the JSON response
        """
        try:
            url = f"{self._base_url}/credentials"

            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Authorization" : "Bearer " + self.generateServiceToken("credentials.list"),
                "x-api-key": self._client_id
            }

            params = {
                "user_id": user_id
            }

            r = requests.get(url, params=params, headers=headers)

            if r.status_code != 200:
                return r.status_code, str(r)

            return None, r.json()
        except Exception as e:
            return e, str(e)
    
    def renameCredential(self, user_id: str, cred_id: str, updated_name: str) -> Tuple[Union[int, Exception], Dict]:
        """Rename a credential of a user

        Args:
            user_id (str): The id of the user
            cred_id (str): The id of the credential to be renamed
            updated_name (str): The new name

        Returns:
            tuple: A 2-element tuple consisting of

                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): The renamed credential's detail if no error, else the JSON response
        """
        try:
            url = self._base_url + "/credentials/rename"

            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + self.generateServiceToken("credentials.rename"),
                # "x-api-key": self._client_id
            }

            payloads = {
                "client_id": self._client_id,
                "user_id": user_id,
                "credential": {
                    "uuid": cred_id,
                    "name": updated_name
                }
            }

            r = requests.post(url, data=json.dumps(payloads), headers=headers)
            
            if r.status_code!=200:
                return r.status_code, r.json()
            
            return None, r.json()
        except Exception as e:
            return e, str(e)

    def revokeCredential(self, user_id: str, cred_id: str) -> Tuple[Union[int, Exception], Dict]:
        """Revoke an existing credential from a user

        Args:
            user_id (str): The user id to extract the credential
            cred_id (str): The credential id to be revoked

        Returns:
            tuple: A 2-element tuple consisting of

                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): The revoked credential's detail if no error, else the JSON response
        """
        try:
            url = self._base_url + "/credentials/revoke"
            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + self.generateServiceToken("credentials.revoke")
            }
            payloads = {
                "client_id": self._client_id,
                "user_id": user_id,
                "credential":{
                    "uuid": cred_id
                }
            }
            r = requests.post(url, data=json.dumps(payloads), headers=headers)

            if r.status_code != 200:
                return r.status_code, r.json()

            return None, r.json()
        except Exception as e:
            return e, str(e)

    def addUserWithoutCredentials(self, username: str) -> Tuple[Union[int, Exception], Dict]:
        """Add a new user without credentials. The new user can create new credentials with recovery flow

        Args:
            username (str): The username of the new user

        Returns:
            tuple: A 2-element tuple consisting of

                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): The new user's profile if no errors, else the JSON response

        """
        try:
            url = f'{self._base_url}/manage/users'

            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + self.generateServiceToken("users.create"),
                "x-client-id": self._client_id
            }

            payloads = {
                "username": username
            }

            r = requests.post(url, data=json.dumps(payloads), headers=headers)

            if (r.status_code !=200):
                return r.status_code, r.json()

            return None, r.json()
        except Exception as e:
            return e, {'message': str(e)}
            
    def initAddCredentialWithoutCode(self, user_id: str) -> Tuple[Union[int, Exception], Dict]:
        """Add a credential without pre-generated authorization code
        Args:
            user_id (str): ID of the user to add new credential to
        Returns:
            tuple: A 2-element tuple consisting of
                - **error** (*Union[int, Exception]*): HTTP error code, `None` if no errors
                - **response** (*Union[str, Dict]*): The attestation payload for the credentials if no errors, else the JSON response
        """
        url = f'{self._base_url}/credentials/fido2/init/force'

        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.generateServiceToken('credentials.force_add')}"
        }

        payloads = {
            "client_id": self._client_id,
            "user_id": user_id
        }
        
        r = requests.post(url, data=json.dumps(payloads), headers=headers)

        if (r.status_code != 200):
            return r.status_code, r.json()

        return None, r.json()