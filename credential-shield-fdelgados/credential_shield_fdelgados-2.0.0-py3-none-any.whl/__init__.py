import jwt
from typing import Dict, List
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


class Token:
    def __init__(self, token_claims: Dict):
        self._application_id = token_claims.get('aud')
        self._tenant_id = token_claims.get('tenant_id')
        self._username = token_claims.get('username')
        self._email = token_claims.get('email')
        self._role = token_claims.get('role')
        self._permissions = token_claims.get('scope').split()
        self._expiration_date = datetime.fromtimestamp(token_claims.get('exp'))

    def tenant_id(self) -> str:
        return self._tenant_id

    def username(self) -> str:
        return self._username

    def user_email(self) -> str:
        return self._email

    def user_role(self) -> str:
        return self._role

    def user_permissions(self) -> List[str]:
        return self._permissions

    def application_id(self) -> str:
        return self._application_id

    def expires_on(self) -> datetime:
        return self._expiration_date


class TokenValidator:
    _REQUIRED_CLAIMS = [
        'sub',
        'iss',
        'aud',
        'iat',
        'exp',
        'username',
        'tenant_id',
        'role',
        'email',
    ]

    def __init__(self, application_id: str, scope: str, token_issuer: str):
        self._application_id = application_id
        self._scope = scope
        self._token_issuer = token_issuer

    def validate(self, access_token: str, public_key: str) -> Token:
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

            scopes = payload.get('scope', '').split()
            if self._scope not in scopes:
                raise ScopeNotAllowedException()

            token_data = Token(payload)

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
