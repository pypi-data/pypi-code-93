from urllib3 import request
from .config import Config
from .client import DXClient
import urllib3


import logging
logging.basicConfig(level=logging.INFO)

DEBUG = False
CLIENT_DEBUG = 'Auto'

__config = Config(debug=DEBUG)
__client = None


logging.info('Inializating deployx.')


def _set_client_debug():
    import socket
    ip_addr = socket.gethostbyname(socket.gethostname())
    global CLIENT_DEBUG
    if ip_addr.startswith('127.0.'):
        CLIENT_DEBUG = True
    else:
        CLIENT_DEBUG = False


def set_config(config):
    
    global __config
    global __client

    logging.info("Initialize new config with manual data.")
    new_config = __config.set_config(config)

    _set_client_debug()

    try:
        if __client:
            logging.info('Close connection in old client.')
            old_client = __client
            old_client.close()
    finally:
        __config = new_config
        logging.info('Initializate new client.')
        new_client = DXClient(config=__config)
        __client = new_client


def set_debug(value:bool):
    """
    CLIENT_DEBUG used for default_value logig
    if CLIENT_DEBUG == Auto
        we check socket.gethostbyname() and it have not 127.0.... address
        we set CLIENT_DEBUG False else CLIENT_DEBUG = True
    if CLIENT_DEBUG == True
        try to get value from deploy-x
        if deploy-x.com not available return default value
        if client don't provide default_value in dxclient.get(...)
        try to find value in redis and return it
    if CLIENT_DEBUG == False
        try to get value from deploy-x
        if deploy-x.com not available try to find redis and value inside it
        if we didn't find redis - return default value
        if default_value was not found - raise error
    """
    global CLIENT_DEBUG
    CLIENT_DEBUG = value


def set_sdk_key(key):
    global __config
    global __client

    _set_client_debug()

    # user already initialized with the same sdk_key
    if __config.sdk_key == key:
        logging.info('Client with this key already initialized.')

    # user already initialized with another sdk_key
    elif __config.sdk_key and __config.sdk_key != key:
        logging.info('Sdk key was installed. Install new key passed to set_sdk_key().')
        __config.set_sdk_key(key)
        if __client:
            logging.info('Initializate new client.')
            old_client = __client
            __client = DXClient(__config)
            old_client.close()

    # user not initialized
    elif not __config.sdk_key:
        logging.info('Install new sdk_key to exist Config instance')
        __config.set_sdk_key(key)
        __client = DXClient(config=__config)


def get(flag_key, user, default=None):
    if default and type(default) != bool:
        raise TypeError("Use True or False for default value.")
    if __client and __config.sdk_key:
        if isinstance(user, dict):
            return __client.get_flag(flag_key, user, default, client_debug=CLIENT_DEBUG)
        else:
            raise TypeError("User instance must be dict type.")
    else:
        raise AttributeError('Client was not found. Call set_config() or set_sdk_key() to initializate client and install required sdk_key.')
