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
    ScopeNotAllowedException
)


class TokenData:
    def __init__(self, token_claims: Dict):
        self._application_id = str(token_claims.get('aud')).strip()
        self._tenant_id = str(token_claims.get('tenant_id')).strip()
        self._expiration_date = datetime.fromtimestamp(token_claims.get('exp'))


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

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['HS256', ],
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
            raise ExpiredTokenException
