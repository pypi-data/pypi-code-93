import importlib
import json
from .Service import initService, BaseService, LoginService, OAuth2Service
from .User import initUser
from .Token import initToken, Token
from typing import Union
import os
import requests
import logging

logger = logging.getLogger()


def parseUserId(obj: str):
    # TODO: add regex here (\S+):\/\/(\S+?):(\S+)
    service, user = obj.split("://")
    userId, password = user.split(":")

    if not "port-" in service:
        service = "port-{}".format(service)

    if password == "None":
        password = None

    if userId == "":
        userId = None

    if password == "":
        password = None

    return service, userId, password


def parseToken(token: Token):
    serviceport = "{}".format(token.service.servicename)
    if not "port-" in serviceport:
        serviceport = "port-{}".format(serviceport)

    data = {
        "userId": "{}://{}:{}".format(serviceport, token.user.username, token.access_token)
    }

    return data


def getServiceObject(obj: Union[str, dict]):
    """Creates a service object, corresponding to the given object

    Args:
        obj (Union[str, dict]): The object needs to be a valid json or dictionary, created with to_json or to_dict method of a valid Service object

    Returns:
        BaseService: It is a Service object, which inherates from BaseService
    """
    return initService(obj)


def getUserObject(obj: Union[str, dict]):
    """Creates a User object, corresponding to the given object

    Args:
        obj (Union[str, dict]): The object needs to be a valid json or dictionary, created with to_json or to_dict method of a valid User object

    Returns:
        User: It is a User object, which inherates from User
    """
    return initUser(obj)


def getTokenObject(obj: Union[str, dict]):
    """Creates a Token object, corresponding to the given object

    Args:
        obj (Union[str, dict]): The object needs to be a valid json or dictionary, created with to_json or to_dict method of a valid Token object

    Returns:
        Token: It is a Token object, which inherates Token
    """
    return initToken(obj)


def loadToken(userId: str, service: Union[str, BaseService]) -> str:
    # FIXME make localhost dynamic for pactman
    tokenStorageURL = os.getenv(
        "USE_CASE_SERVICE_PORT_SERVICE", "http://localhost:3000"
    )
    # load access token from token-storage
    try:
        servicename = service.servicename
    except:
        servicename = service

    if not servicename.startswith("port-"):
        servicename = "port-{}".format(servicename)

    result = requests.get(
        f"{tokenStorageURL}/user/{userId}/service/{servicename}",
        verify=(os.environ.get("VERIFY_SSL", "True") == "True"),
    )

    if result.status_code > 200:
        return None

    access_token = result.json()
    logger.debug(f"got: {access_token}")

    token = getTokenObject(access_token)

    logger.debug("initialize type: {}, data: {}".format(
        token.__class__.__name__, token.to_json()))

    return token


def register_service(
    service: BaseService
):
    """Register the given service to Token Storage

    Args:
        service (BaseService): The Service, which will be registered in Token Storage

    Raises:
        Exception: Raises, when there is something wrong in registering process.

    Returns:
        Bool: Returns True, when success, Otherwise False or raise Exception
    """
    tokenStorage = os.getenv("CENTRAL_SERVICE_TOKEN_STORAGE")
    if tokenStorage is None:
        return False

    data = service.to_dict()
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        f"{tokenStorage}/service",
        json=data,
        headers=headers,
        verify=(os.environ.get("VERIFY_SSL", "True") == "True"),
    )

    if response.status_code != 200:
        raise Exception(
            "Cannot find and register Token Storage, msg:\n{}".format(
                response.text)
        )

    response = response.json()
    if response["success"]:
        logger.info(
            f"Registering {service.servicename} in token storage was successful.")
        return True

    logger.error(
        f"There was an error while registering {service.servicename} to token storage.\nJSON: {response}"
    )

    return False


def load_class_from_json(jsonStr: str):
    """
    Returns the class of the given json string.
    """

    if not isinstance(jsonStr, str):
        raise ValueError("Given parameter not a string.")

    data = jsonStr

    # FIX for json bug: Sometimes it returns a string.
    while not isinstance(data, dict):
        data = json.loads(data)

    return internal_load_class(data)


def load_class_from_dict(data: dict):
    """
    Returns the class of the given dict.
    """
    return internal_load_class(data)


def initialize_object_from_json(jsonStr: str):
    """
    Initialize and returns an object of the given json string.

    This is the easiest way to reverse the to_json method for objects from our lib folder.
    """
    return load_class_from_json(jsonStr).from_json(jsonStr)


def initialize_object_from_dict(jsonDict: dict):
    """
    Initialize and returns an object of the given dict.

    This is another easy way to reverse the to_json method for objects from our lib folder.
    """
    return load_class_from_dict(jsonDict).from_dict(jsonDict["data"])


def internal_load_class(data: dict):
    """
    For internal use only.
    """

    if not isinstance(data, dict):
        raise ValueError("Given parameter not a dict object.")

    if "type" in data:
        try:
            klass = None
            if data["type"].endswith("Token"):
                mod = importlib.import_module("RDS.Token")
                klass = getattr(mod, data["type"])
            elif data["type"].endswith("Service"):
                mod = importlib.import_module("RDS.Service")
                klass = getattr(mod, data["type"])
            elif data["type"].endswith("User"):
                mod = importlib.import_module("RDS.User")
                klass = getattr(mod, data["type"])

            if klass is not None:
                return klass

        except Exception:
            raise

        raise ValueError("given parameter is not a valid class.")
    raise ValueError("Type not specified in dict.")


def try_function_on_dict(func: list):
    """
    This method trys the given functions on the given dictionary. Returns the first function, which returns a value for given dict.

    Main purpose of this is the initialization of multiple Classes from json dicts.

    Usage:
    ```python
    func_list = [func1, func2, func3]
    x = Util.try_function_on_dict(func_list)
    object = x(objDict)
    ```

    equals to:
    ```python
    try:
        try:
            func1(objDict)
        except:
            pass
        try:
            func2(objDict)
        except:
            pass
        try:
            func3(objDict)
        except:
            pass
    except:
        raise Exception(...)
    ```

    Raise an `Exception` with all raised exception as strings, if no function returns a value for the given jsonDict.
    """

    def inner_func(jsonDict: dict):
        nonlocal func

        exp_list = []

        for f in func:
            try:
                return f(jsonDict)
            except Exception as e:
                exp_list.append(e)
                continue

        raise Exception(
            "The given jsonDict raise in all functions an exception.\ndata: {}, errors: \n{}".format(
                jsonDict,
                "\n".join(
                    [f"Error: {type(e)}, Msg: {str(e)}" for e in exp_list])
            )
        )

    return inner_func


def monkeypatch(func_name: str = "to_json"):
    """ Module that monkey-patches json module when it's imported so
    JSONEncoder.default() automatically checks for a special "to_json()"
    method and uses it to encode the object if found.
    """
    from json import JSONEncoder, JSONDecoder

    def to_default(self, obj):
        return getattr(obj.__class__, func_name, to_default.default)(obj)

    to_default.default = JSONEncoder.default  # Save unmodified default.
    JSONEncoder.default = to_default  # Replace it.


# this part can only be used, if flask is installed. See: https://github.com/Sciebo-RDS/py-research-data-services-common#optional-dependencies
try:
    from flask.json import JSONEncoder
    from functools import wraps

    def get_json_encoder(func_name: str = "to_json"):
        """ Module that monkey-patches json module when it's imported so
        JSONEncoder.default() automatically checks for a special "to_json()"
        method and uses it to encode the object if found.
        """

        class RDSEncoder(JSONEncoder):
            def default(self, o):
                method = getattr(o, func_name, JSONEncoder.default)
                try:
                    return method()
                except:
                    try:
                        return method(o)
                    except:
                        return method(self, o)

        return RDSEncoder

    def wrap_monkeypatch(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = "app"
            if kwargs.get(key) is not None:
                app = kwargs[key]
                del kwargs[key]
                app.json_encoder = get_json_encoder(*args, **kwargs)
            else:
                try:
                    from flask import current_app

                    current_app.json_encoder = get_json_encoder(
                        *args, **kwargs)
                except:
                    pass
            return fn(*args, **kwargs)

        return wrapper

    monkeypatch = wrap_monkeypatch(monkeypatch)

except:
    pass
