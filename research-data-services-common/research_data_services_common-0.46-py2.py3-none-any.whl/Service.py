from .Token import Token, OAuth2Token
from .User import User
from .Informations import LoginMode, FileTransferMode, FileTransferArchive
from urllib.parse import urlparse, urlunparse
import requests
import json
from datetime import datetime, timedelta
from typing import Union
import logging
import mimetypes
import base64
import os.path
from io import IOBase
from urllib import parse

logger = logging.getLogger()


def initService(obj: Union[str, dict]):
    """
    Returns a Service or oauthService object for json String or dict.
    """
    if isinstance(obj, (LoginService, OAuth2Service)):
        return obj

    if not isinstance(obj, (str, dict)):
        raise ValueError("Given object not from type str or dict.")

    from RDS.Util import try_function_on_dict

    load = try_function_on_dict(
        [
            OAuth2Service.from_json,
            OAuth2Service.from_dict,
            LoginService.from_json,
            LoginService.from_dict,
            BaseService.from_json,
            BaseService.from_dict
        ]
    )
    return load(obj)


class BaseService:
    """
    Represents a service, which can be used in RDS.
    """

    _servicename = None
    _implements = None
    _fileTransferMode = None
    _fileTransferArchive = None
    _description = None
    _icon = None
    _infoUrl = None
    _helpUrl = None
    _displayName = None

    def __init__(
        self,
        servicename: str,
        implements: list = None,
        fileTransferMode: FileTransferMode = FileTransferMode.active,
        fileTransferArchive: FileTransferArchive = FileTransferArchive.none,
        description: dict = None,
        icon: str = "",
        infoUrl: str = "",
        helpUrl: str = "",
        displayName: str = None
    ):
        """Initialize Service without any authentication.

        Args:
            servicename (str): The name of the service, which will be registered. Must be unique.
            implements (list, optional): Specified the implemented port endpoints. Defaults to empty list.
            fileTransferMode (int, optional): Set the mode for transfering files. Defaults to 0=active. Alternative is 1=passive.
            fileTransferArchive (str, optional): Set the archive, which is needed for transfering files. Defaults to "". Other value is "zip"
            description (dict, optional): Set a short description for this service with corresponding language. Defaults to {"en":""}.
            icon: (str, optional): Takes a filepath, so the mimetype and base64 can be calculated for later usage. Defaults to "".
            infoUrl: (str, optional): Set the infoUrl for this service, so the user can be redirected to it to find more information about the service. Defaults to "".
            helpUrl: (str, optional): Set the helpUrl for this service, so the user can be redirected to a helpdesk page about this service. Defaults to "".
            displayName: (str, optional): Set the displayName for this service, which can be different as the servicename. Servicename will be used for identifiers. Defaults to "".
        """
        self.check_string(servicename, "servicename")

        self._servicename = servicename.lower()

        if description is None:
            self._description = {"en": ""}
        else:
            self._description = description

        if infoUrl is not None:
            if parse.unquote_plus(infoUrl) == infoUrl:
                self._infoUrl = parse.quote_plus(infoUrl)
            else:
                self._infoUrl = infoUrl
        else:
            self._infoUrl = ""

        if helpUrl is not None:
            if parse.unquote_plus(helpUrl) == helpUrl:
                self._helpUrl = parse.quote_plus(helpUrl)
            else:
                self._helpUrl = helpUrl
        else:
            self._helpUrl = ""

        if displayName is not None:
            self._displayName = displayName
        else:
            self._displayName = ""

        if icon is not None and icon != "":
            if isinstance(icon, (str)) and str(icon).startswith("data:"):
                self._icon = icon
            elif os.path.isfile(icon):
                mime = mimetypes.guess_type(icon)[0]

                with open(icon, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    self._icon = f"data:{mime};base64,{b64}"
            else:
                raise FileNotFoundError

        self._implements = implements
        if implements is None:
            self._implements = []

        valid_implements = ["fileStorage", "metadata"]

        if len(self._implements) == 0 or len(self._implements) > 2:
            raise ValueError(
                "implements is empty or over 2 elements. Value: {}, Only valid: {}".format(
                    len(self._implements), valid_implements)
            )

        for impl in self._implements:
            if impl not in valid_implements:
                raise ValueError("implements holds an invalid value: {}. Only valid: {}".format(
                    impl, valid_implements))

        self._fileTransferMode = fileTransferMode
        self._fileTransferArchive = fileTransferArchive

    @property
    def servicename(self):
        return self._servicename

    @property
    def fileTransferMode(self):
        return self._fileTransferMode

    @property
    def fileTransferArchive(self):
        return self._fileTransferArchive

    @property
    def description(self):
        return self._description

    @property
    def icon(self):
        return self._icon

    @property
    def infoUrl(self):
        return self._infoUrl

    @property
    def helpUrl(self):
        return self._helpUrl

    @property
    def displayName(self):
        return self._displayName

    @property
    def implements(self):
        return self._implements

    def check_string(self, obj: str, string: str):
        if not obj:
            raise ValueError(f"{string} cannot be an empty string.")

    def is_valid(self, token: Token, user: User):
        pass

    def __eq__(self, obj):
        try:
            return self.servicename == obj.servicename
        except:
            return False

    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self.to_dict())

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
            "servicename": self._servicename,
            "implements": self._implements,
            "fileTransferMode": self.fileTransferMode.value,
            "fileTransferArchive": self.fileTransferArchive.value,
            "description": self._description,
            "icon": self._icon,
            "infoUrl": self._infoUrl,
            "helpUrl": self._helpUrl,
            "displayName": self._displayName
        }

        return data

    @classmethod
    def from_json(cls, serviceStr: str):
        """
        Returns an service object from a json string.
        """

        data = serviceStr
        while (
            type(data) is not dict
        ):  # FIX for bug: JSON.loads sometimes returns a string
            data = json.loads(data)

        if "type" in data and str(data["type"]).endswith("Service") and "data" in data:
            data = data["data"]

            return BaseService(
                servicename=data["servicename"],
                implements=data.get("implements"),
                fileTransferMode=FileTransferMode(
                    data.get("fileTransferMode", 0)),
                fileTransferArchive=FileTransferArchive(
                    data.get("fileTransferArchive", 0)),
                description=data.get("description"),
                icon=data.get("icon"),
                infoUrl=data.get("infoUrl"),
                helpUrl=data.get("helpUrl"),
                displayName=data.get("displayName")
            )

        raise ValueError("not a valid service json string.")

    @classmethod
    def from_dict(cls, serviceDict: dict):
        """
        Returns an service object from a dict string.
        """

        try:
            return BaseService(
                servicename=serviceDict["servicename"],
                implements=serviceDict.get("implements", ["metadata"]),
                fileTransferMode=FileTransferMode(
                    serviceDict.get("fileTransferMode", 0)),
                fileTransferArchive=FileTransferArchive(
                    serviceDict.get("fileTransferArchive", 0)),
                description=serviceDict.get("description"),
                icon=serviceDict.get("icon"),
                infoUrl=serviceDict.get("infoUrl"),
                helpUrl=serviceDict.get("helpUrl"),
                displayName=serviceDict.get("displayName")
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            raise ValueError("not a valid service dict for class {}".format(
                cls.__class__))


class LoginService(BaseService):
    _userId = None
    _password = None

    def __init__(
        self,
        userId: bool = True,
        password: bool = True,
        *args, **kwargs
    ):
        """Initialize Service with username:password authentication.

        Args:
            userId (bool, optional): Set True, if username is needed to work. Defaults to True.
            password (bool, optional): Set True, if password is needed to work. Defaults to True.
        """
        super().__init__(*args, **kwargs)

        self._userId = userId
        self._password = password

    @property
    def userId(self):
        return self._userId

    @property
    def password(self):
        return self._password

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
        data["credentials"] = {
            "userId": self.userId, "password": self.password
        }

        return data

    @classmethod
    def from_json(cls, serviceStr: str):
        """
        Returns an oauthservice object from a json string.
        """

        data = serviceStr
        while (
            type(data) is not dict
        ):  # FIX for bug: JSON.loads sometimes returns a string
            data = json.loads(data)

        service = super().from_json(serviceStr)

        try:
            data = data["data"]
            cred = data.get("credentials", {})

            return cls.from_service(
                service,
                cred.get("userId", True),
                cred.get("password", True)
            )
        except:
            raise ValueError("not a valid oauthservice json string.")

    @classmethod
    def from_dict(cls, serviceDict: dict):
        """
        Returns an oauthservice object from a dict.
        """

        service = super().from_dict(serviceDict)

        try:
            cred = serviceDict.get("credentials", {})
            return cls.from_service(
                service,
                cred.get("userId", True),
                cred.get("password", True)
            )
        except:
            raise ValueError("not a valid loginservice dict.")

    @classmethod
    def from_service(
        cls,
        service: BaseService,
        userId: bool,
        password: bool
    ):
        return cls(
            userId=userId,
            password=password,
            servicename=service.servicename,
            implements=service.implements,
            fileTransferMode=service.fileTransferMode,
            fileTransferArchive=service.fileTransferArchive,
            description=service.description,
            icon=service.icon,
            infoUrl=service.infoUrl,
            helpUrl=service.helpUrl,
            displayName=service.displayName,
        )


class OAuth2Service(BaseService):
    """
    Represents an OAuth2 service, which can be used in RDS.
    This service enables the oauth2 workflow.
    """

    _authorize_url = None
    _refresh_url = None
    _client_id = None
    _client_secret = None

    def __init__(
        self,
        authorize_url: str = "",
        refresh_url: str = "",
        client_id: str = "",
        client_secret: str = "",
        *args, **kwargs
    ):
        """Initialize a service for oauth2.

        Args:
            authorize_url (str, optional): The authorize url from oauth2 workflow. Defaults to "".
            refresh_url (str, optional): The refresh url from oauth2 workflow. Defaults to "".
            client_id (str, optional): The client id from oauth2 workflow. Defaults to "".
            client_secret (str, optional): The client secret from oauth2 workflow. Defaults to "".
        """
        super().__init__(*args, **kwargs)

        self.check_string(authorize_url, "authorize_url")
        self.check_string(refresh_url, "refresh_url")
        self.check_string(client_id, "client_id")
        self.check_string(client_secret, "client_secret")

        self._authorize_url = self.parse_url(authorize_url)
        self._refresh_url = self.parse_url(refresh_url)

        self._client_id = client_id
        self._client_secret = client_secret

    def parse_url(self, url: str):
        u = urlparse(url)
        if not u.netloc:
            raise ValueError("URL needs a protocoll")

        # check for trailing slash for url
        if u.path and u.path[-1] == "/":
            u = u._replace(path=u.path[:-1])

        return u

    def refresh(self, token: OAuth2Token):
        """
        Refresh the given oauth2 token for specified user.
        """

        if not isinstance(token, OAuth2Token):
            logger.debug("call refresh on non oauth token.")
            raise ValueError("parameter token is not an oauthtoken.")

        import os

        data = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "redirect_uri": "{}".format(
                os.getenv("RDS_OAUTH_REDIRECT_URI",
                          "http://localhost:8080/redirect")
            ),
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        logger.debug(f"send data {data}")

        req = requests.post(
            self.refresh_url,
            data=data,
            auth=(self.client_id, self.client_secret),
            verify=(os.environ.get("VERIFY_SSL", "True") == "True"),
        )

        logger.debug(f"status code: {req.status_code}")

        if req.status_code >= 400:
            data = json.loads(req.text)

            if "error" in data:
                error_type = data["error"]

                if error_type == "invalid_request":
                    from RDS.ServiceException import OAuth2InvalidRequestError

                    raise OAuth2InvalidRequestError()
                elif error_type == "invalid_client":
                    from RDS.ServiceException import OAuth2InvalidClientError

                    raise OAuth2InvalidClientError()
                elif error_type == "invalid_grant":
                    from RDS.ServiceException import OAuth2InvalidGrantError

                    raise OAuth2InvalidGrantError()
                elif error_type == "unauthorized_client":
                    from RDS.ServiceException import OAuth2UnauthorizedClient

                    raise OAuth2UnauthorizedClient()
                elif error_type == "unsupported_grant_type":
                    from RDS.ServiceException import OAuth2UnsupportedGrantType

                    raise OAuth2UnsupportedGrantType()

            from RDS.ServiceException import OAuth2UnsuccessfulResponseError

            raise OAuth2UnsuccessfulResponseError()

        data = json.loads(req.text)

        logger.debug(f"response data {data}")

        """ obsolete
        if not data["user_id"] == self.client_id:
            from RDS.ServiceException import Token.TokenNotValidError
            raise Token.TokenNotValidError(
                self, token, "User-ID in refresh response not equal to authenticated user.")
        """

        date = datetime.now() + timedelta(seconds=data["expires_in"])
        try:
            new_token = OAuth2Token(
                token.user,
                token.service,
                data["access_token"],
                data["refresh_token"],
                date,
            )
        except KeyError as e:
            logger.error(e)
            logger.debug("refresh_token still active.")

            new_token = OAuth2Token(
                token.user,
                token.service,
                data["access_token"],
                token.refresh_token,
                date,
            )

        logger.debug(f"new token {new_token}")
        return new_token

    @property
    def refresh_url(self):
        return urlunparse(self._refresh_url)

    @property
    def authorize_url(self):
        return urlunparse(self._authorize_url)

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @classmethod
    def from_service(
        cls,
        service: BaseService,
        authorize_url: str,
        refresh_url: str,
        client_id: str,
        client_secret: str,
    ):
        """
        Converts the given Service to an oauth2service.
        """
        return cls(
            authorize_url=authorize_url,
            refresh_url=refresh_url,
            client_id=client_id,
            client_secret=client_secret,
            servicename=service.servicename,
            implements=service.implements,
            fileTransferMode=service.fileTransferMode,
            fileTransferArchive=service.fileTransferArchive,
            description=service.description,
            icon=service.icon,
            infoUrl=service.infoUrl,
            helpUrl=service.helpUrl,
            displayName=service.displayName,
        )

    def __eq__(self, obj):
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
        data["authorize_url"] = self.authorize_url
        data["refresh_url"] = self.refresh_url
        data["client_id"] = self._client_id
        data["client_secret"] = self._client_secret

        return data

    @classmethod
    def from_json(cls, serviceStr: str):
        """
        Returns an oauthservice object from a json string.
        """

        data = serviceStr
        while (
            type(data) is not dict
        ):  # FIX for bug: JSON.loads sometimes returns a string
            data = json.loads(data)

        service = super().from_json(serviceStr)

        try:
            data = data["data"]
            return cls.from_service(
                service,
                data["authorize_url"],
                data["refresh_url"],
                data["client_id"],
                data.get("client_secret", ""),
            )
        except:
            raise ValueError("not a valid oauthservice json string.")

    @classmethod
    def from_dict(cls, serviceDict: dict):
        """
        Returns an oauthservice object from a dict.
        """

        service = super().from_dict(serviceDict)

        try:
            return cls.from_service(
                service,
                serviceDict["authorize_url"],
                serviceDict["refresh_url"],
                serviceDict["client_id"],
                serviceDict.get("client_secret", ""),
            )
        except:
            raise ValueError("not a valid oauthservice dict.")
