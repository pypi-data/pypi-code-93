from os import error
import requests, json, jwt

import random
from datetime import datetime
import base64, hashlib

from typing import Tuple, Union, Dict

from requests.api import head
class LoginID:
    def __init__(self, client_id: str, private_key: str, base_url: str) -> None:
        """ This server SDK leverages either a web or mobile application 
        and requires an API credential to be assigned to that integration.

        Args:
            client_id (str): The client ID
            private_key (str): API private key
            base_url (str): LoginID serivce address

        Example:: 

            from loginid import LoginID
            lid = LoginID(CLIENT_ID, PRIVATE_KEY)
        
           
        """
        self._private_key = private_key
        self._client_id = client_id
        self._base_url = base_url

        # allowed code types
        self._code_types = {'short', 'long', 'phrase'}

    def get_clientId(self) -> str:
        """Extract the client id 

        Returns:
            str: The client id
        """
        return self.client_id

    def _getUtcEpoch(self):
        return int((datetime.utcnow()-datetime(1970,1,1)).total_seconds())

    def _getRandomString(self, length: int=16) -> str:
        """
        Generate a random string of given length with alphanumeric characters

        Args:
            length (int): length of the output string

        Returns:
            str: a random string
        """
        possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        ret = [random.choice(possible) for _ in range(length)]
        return "".join(ret)

    def _getPublicKey(self, kid: str) -> Tuple[Union[Exception, None], str]:
        """Extract the client's public key with `kid`

        Args:
            kid (str): the kid included in jwt's header

        Returns:
            tuple: a 2-element tuple containing

                - **error** (*int*): HTTP error code, `None` if no errors
                - **response** (str): The public key if `error` is `None`, else the error message
        """
        try:
            params = {"kid":kid}
            r = requests.get(f'{self._base_url}/certs', params=params)
            if (r.status_code != 200): return r.status_code, r.json()
            
            return None, r.text 
        except Exception as e:
            return e, str(e)
        
    def verifyToken(self, token: str, username: Union[None, str]=None) -> bool:
        """Verify a JWT token returned upon user authorization

        Args:
            token (str): JWT token
            username (Union[None, str], optional): if given, checks for if `username` matches the `udata` in JWT.
                 Defaults to None.

        Returns:
            bool: `True` if the token is valid, `False` otherwise (including errors)
        """

        try:
            headers = jwt.get_unverified_header(token)
            algo, kid = headers['alg'], headers['kid']
            assert algo=="ES256", f"{algo} is not an allowed algorithm."

            # extracting public key from LogInID
            err, public_key = self._getPublicKey(kid)
            if err is not None:
                return False

            payload = jwt.decode(token, public_key, 
                algorithms=algo,
                audience=self._client_id
            )

            if username is not None:
                return username == payload['udata']
            return True
        except:
            return False

    def generateServiceToken(self, scope: str, algo: str="ES256", username: str=None, user_id:str=None, nonce: str=None) -> str:
        """
        Generate a service token

        Args:
            scope (str): the scope of the service
            algo (str, optional): Encryption algorithm, defaults to `"ES256"`
            username (str, optional): the username to-be granted by the token
            user_id (str, optional): the user_id to be granted by the token. If `username` is given, 
                this is ignored
            nonce (str, optional): nonce for the token, randomly generated if not given

        Returns:
            str: the JWT service token
        """
        payloads = {
            "client_id": self._client_id,
            "type": scope,
            "nonce": nonce or self._getRandomString(16),
            "iat": self._getUtcEpoch()
        }

        if username is not None:
            payloads['username'] = username
        elif user_id is not None:
            payloads['user_id'] = user_id

        jwt_headers = {"alg": algo, "typ": "JWT"}

        return jwt.encode(
            payloads, self._private_key, algorithm=algo,
            headers=jwt_headers
        )

    def _request(self, method: str, url: str, payloads: dict, headers:dict=None) -> Tuple[Union[None, int], Dict]:
        methods = {'post': requests.post, 'get': requests.get}
        r_method = methods.get(method, None)
        if r_method is None:
            return -1, {'message': f'request method {method} not allowed'}
        
        r = r_method(url, data=json.dumps(payloads), headers=headers)

        if (r.status_code != 200):
            return r.status_code, r.json()
        
        return None, r.json()
        
    # Tx Flow 
    def generateTxAuthToken(self, tx_payload: str, username: str=None, nonce: str=None) -> str:
        """Generate an Authorization Token for Transaction Flow

        Args:
            tx_payload (str): The transaction payload
            username (str, optional): The username
            nonce (str, optional): optional nonce for the token, auto-generated if not given

        Returns:
            str: The JWT authorization token
        """

        # encryption algorithm, only supports ES256
        algo = "ES256"

        # hash and encode tx_payload
        payload_hash = hashlib.sha256(tx_payload.encode()).digest()
        payload_hash = (base64.urlsafe_b64encode(payload_hash)
                              .decode().strip('=')
                       )

        payloads = {
            'type': 'tx.create',
            'nonce': nonce or self._getRandomString(16),
            'payload_hash': payload_hash,
            'iat': self._getUtcEpoch()
        }

        # TODO: remove username when native-service is updated
        if username is not None: payloads['username'] = username

        return jwt.encode(
            payloads, self._private_key,
            algorithm=algo,
            headers={'alg': algo, 'typ': 'JWT'}
        )

    def createTx(self, tx_payload: str, username: str=None, nonce: str=None) -> Tuple[Union[Exception, int, None], str]:
        """Create a Transaction ID

        Args:
            tx_payload (str): The transaction payload
            username (str, optional): The username that initiates the transaction
            nonce (str, optional): The optional nonce, randomly generated if not provided


        Returns:
            tuple: a 2-element tuple containing

                - **error** (*int*): The HTTP error, `None` if no errors            
                - **tx_id** (*str*): The transaction id if no error, the empty string otherwise
        """
        try:
            url = f"{self._base_url}/tx"

            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + self.generateTxAuthToken(tx_payload)
            }
            payloads = dict(
                client_id=self._client_id,
                username=username,
                tx_type='text',
                tx_payload=tx_payload,
                nonce=nonce or self._getRandomString()  
            )

            err, response = self._request('post', url, payloads, headers=headers)

            if (err is not None):
                return err, ""

            return None, response['id']
        except Exception as e:
            return e, str(e) 

    def verifyTransaction(self, tx_token: str, tx_payload: str) -> Tuple[Union[Exception, None], bool]: 
        """Verify the jwt token returned upon completion of a transaction

        Args:
            tx_token (str): The JWT token 
            tx_payload (str): the original transaction payload 

        Returns:
            tuple: A 2-element tuple containing

                **error** (*Exception*): Error code if errors occur, `None` otherwise
                **valid** (*bool*): `True` if the token is valid, `False` if not
        """
        try:
            headers = jwt.get_unverified_header(tx_token)
            algo, kid = headers['alg'], headers['kid']
            assert algo == "ES256", f"{algo} is not an allowed algorithm"

            # get public key
            err, public_key = self._getPublicKey(kid)
            if err is not None:
                return err, public_key

            payload = jwt.decode(tx_token, public_key, algorithms=algo,
                                 audience=self._client_id)

            to_hash = tx_payload + payload.get("nonce","") + payload.get("server_nonce","")
            hash = hashlib.sha256(to_hash.encode()).digest()
            hash = base64.urlsafe_b64encode(hash).decode().strip('=')

            return None, payload.get('tx_hash') == hash
        except Exception as e:
            return e, str(e)
            
    # Code
    def isValidCodeType(self, codeType: str)->bool:
        """Check if a code type is valid

        Args:
            codeType (str): code type

        Returns:
            bool: `True` if codeType is value, `False` otherwise
        """
        return codeType in self._code_types

    def waitCode(self, username: str, code: str, codeType: str)->Tuple[Union[int, Exception, None], dict]:
        """ Wait for a given code

        Args:
            username (str): The username
            code (str): The code associate to the username
            codeType (str): Type of the code

        Returns:
            tuple: a 2-element tuple containing

                - **error** (*int*): The HTTP error, `None` if no errors
                - **response** (*dict*): The response body from code wait 
        """
        try:
            assert self.isValidCodeType(codeType)

            url = f'{self._base_url}/authenticate/code/wait'

            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + self.generateServiceToken("auth.temporary")
            }

            payloads = {
                "client_id": self._client_id,
                "username": username,
                "authentication_code": {
                    "code" : code,
                    "type": codeType
                }
            }

            r = requests.post(url, data=json.dumps(payloads), headers=headers)

            if (r.status_code != 200):
                return r.status_code, r.json()

            json_response = r.json()
            token = json_response.get('jwt')
            if (token is None) or (not self.verifyToken(token)):
                raise Exception("Cannot authorize code")

            return None, r.json()
        except Exception as e:
            return e, {"message": str(e)}
