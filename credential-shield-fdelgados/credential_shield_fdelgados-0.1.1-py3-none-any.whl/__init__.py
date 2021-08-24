import jwt
from typing import Dict
from parse import parse
from datetime import datetime

from .exceptions import (
    CredentialShieldException,
    InvalidTokenFormatException,
    InvalidApplicationIdException,
    InvalidTokenSourceException,
    InvalidAccessTokenException,
    ExpiredTokenException,
    ScopeNotAllowedException,
    InvalidPublicKeyError
)


class TokenData:
    def __init__(self, token_claims: Dict):
        self._application_id = token_claims.get('aud')
        self._tenant_id = token_claims.get('tenant_id')
        self._username = token_claims.get('username')
        self._user_email = token_claims.get('user_email')
        self._expiration_date = datetime.fromtimestamp(token_claims.get('exp'))

    def tenant_id(self):
        return self._tenant_id

    def username(self):
        return self._username

    def user_email(self):
        return self._user_email

    def application_id(self):
        return self._application_id

    def expires_on(self):
        return self._expiration_date


class TokenValidator:
    _REQUIRED_CLAIMS = [
        'sub',
        'iss',
        'aud',
        'iat',
        'exp',
        'tenant_id',
        'username',
        'user_role',
        'user_email',
        'scope',
    ]

    def __init__(self, application_id: str, scope: str, token_issuer: str):
        self._application_id = application_id
        self._scope = scope
        self._token_issuer = token_issuer

    def validate(self, access_token: str, public_key: str) -> TokenData:
        parse_result = parse('Bearer {}', access_token)
        if not parse_result:
            raise InvalidTokenFormatException()

        token = parse_result[0]
        header = jwt.get_unverified_header(token)

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[header.get('alg'), ],
                options={
                    'require': self._REQUIRED_CLAIMS,
                    'verify_exp': True,
                    'verify_aud': True
                },
                audience=self._application_id,
                issuer=self._token_issuer
            )

            scopes = str(payload.get('scope')).split()
            if self._scope not in scopes:
                raise ScopeNotAllowedException()

            token_data = TokenData(payload)

            return token_data

        except jwt.InvalidIssuerError:
            raise InvalidTokenSourceException()
        except jwt.InvalidAudienceError:
            raise InvalidApplicationIdException()
        except (jwt.DecodeError, jwt.MissingRequiredClaimError):
            raise InvalidAccessTokenException()
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException()
        except jwt.exceptions.InvalidKeyError:
            raise InvalidPublicKeyError()
