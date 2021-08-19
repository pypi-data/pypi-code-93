import datetime
import json
from typing import Union
from RDS import User


def initToken(obj: Union[str, dict]):
    if isinstance(obj, (Token, OAuth2Token)):
        return obj

    if not isinstance(obj, (str, dict)):
        raise ValueError("Given object not from type str or dict.")

    from RDS.Util import try_function_on_dict

    load = try_function_on_dict(
        [
            OAuth2Token.from_json,
            OAuth2Token.from_dict,
            LoginToken.from_json,
            LoginToken.from_dict,
            Token.from_json,
            Token.from_dict,
        ]
    )
    return load(obj)


class Token:
    """
    This token represents a simple username:password, but will not enforce anything for service.
    """

    _service = None
    _user = None
    _access_token = None

    def __init__(self, user: User, service, access_token: str):
        from RDS import BaseService, LoginService

        if not isinstance(service, BaseService):
            raise ValueError(f"service parameter needs to be of type Service.")

        if not isinstance(service, LoginService):
            self.check_string(access_token, "access_token")

        self._service = service
        self._user = user
        self._access_token = access_token

    @staticmethod
    def check_string(obj: str, string: str):
        if not obj:
            raise ValueError(f"{string} cannot be an empty string, was {obj}")

    @property
    def servicename(self):
        return self._service.servicename

    @property
    def service(self):
        return self._service

    @property
    def access_token(self):
        return self._access_token

    @property
    def user(self):
        return self._user

    def __str__(self):
        return json.dumps(self)

    def __eq__(self, other):
        """
        Returns True, if this object and other object have the same servicename and user. Otherwise false.
        """
        return (
            isinstance(other, (Token))
            and self.service == other.service
            and self.user == other.user
        )

    def to_json(self):
        """
        Returns this object as a json string.
        """

        data = {"type": self.__class__.__name__, "data": self.to_dict()}
        return data

    def to_dict(self):
        """
        Returns this object as a dict.
        """
        data = {
            "service": self._service,
            "access_token": self._access_token,
            "user": self._user,
        }

        return data

    @classmethod
    def from_json(cls, tokenStr: str):
        """
        Returns a token object from a json string.
        """

        data = tokenStr
        while (
            type(data) is not dict
        ):  # FIX for bug: JSON.loads sometimes returns a string
            data = json.loads(data)

        if "type" in data and str(data["type"]).endswith("Token") and "data" in data:
            data = data["data"]
            return cls.from_dict(data)

        raise ValueError("not a valid token json string.")

    @classmethod
    def from_dict(cls, tokenDict: dict):
        """
        Returns a token object from a dict.
        """
        from RDS import Util

        return cls(
            Util.getUserObject(tokenDict["user"]),
            Util.getServiceObject(tokenDict["service"]),
            tokenDict["access_token"],
        )


class LoginToken(Token):
    """Provides a token object, which enforces service configuration.
    """

    def __init__(
        self,
        user: User,
        service,
        access_token: str
    ):
        # Workaround for empty passwords in LoginTokens
        super().__init__(user, service, "---")
        self._access_token = access_token

        from RDS import LoginService

        if not isinstance(service, LoginService):
            raise ValueError("parameter service is not a LoginService, was: {}".format(
                service.__class__.__name__))

        if service.userId and self.user is None:
            raise ValueError(
                "user is needed, because username must be provided for specified service.")

        if service.password and (self.access_token is None or not self.access_token):
            raise ValueError(
                "access_token is needed, because password must be provided for specified service.")


class OAuth2Token(Token):
    """
    Represents a token object.
    """

    _refresh_token = None
    _expiration_date = None

    def __init__(
        self,
        user: User,
        service,
        access_token: str,
        refresh_token: str = "",
        expiration_date: datetime.datetime = None,
    ):
        super().__init__(user, service, access_token)

        from RDS import OAuth2Service

        if not isinstance(service, OAuth2Service):
            raise ValueError("parameter service is not an oauth2service, was: {}".format(
                service.__class__.__name__))

        if expiration_date is None:
            expiration_date = datetime.datetime.now()

        # remove check for empty string for refresh_token, because it could be an authorization_token
        # self.check_string(refresh_token, "refresh_token")

        if refresh_token:
            self._refresh_token = refresh_token
            self._expiration_date = expiration_date

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def expiration_date(self):
        return self._expiration_date

    def refresh(self):
        return self.service.refresh(self)

    def __eq__(self, obj):
        """
        Check, if tokens are equal. You must not check if the refresh or access_tokens are equal,
        because they could be changed already. Only servicename is relevant.
        """
        return super().__eq__(obj)

    def to_json(self):
        """
        Returns this object as a json string.
        """

        data = super().to_json()

        data["type"] = self.__class__.__name__
        data["data"].update(self.to_dict())

        return data

    def to_dict(self):
        """
        Returns this object as a dict.
        """
        data = super().to_dict()
        data["refresh_token"] = self._refresh_token
        data["expiration_date"] = str(self._expiration_date)

        return data

    @classmethod
    def from_json(cls, tokenStr: str):
        """
        Returns an oauthtoken object from a json string.
        """

        data = tokenStr
        while (
            type(data) is not dict
        ):  # FIX for bug: JSON.loads sometimes returns a string
            data = json.loads(data)

        if "type" in data and str(data["type"]).endswith("OAuth2Token"):
            data = data["data"]
            return cls.from_dict(data)

        raise ValueError("not a valid token json string.")

    @classmethod
    def from_dict(cls, tokenDict: dict):
        """
        Returns an oauthtoken object from dict.
        """
        token = super(OAuth2Token, cls).from_dict(tokenDict)

        return OAuth2Token(
            token.user,
            token.service,
            token.access_token,
            tokenDict["refresh_token"],
            datetime.datetime.fromisoformat(tokenDict["expiration_date"]),
        )
