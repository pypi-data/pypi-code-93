from __future__ import absolute_import

VERSION = '0.1.0'

def get_version():
    return VERSION

# import logging
#
# logging.getLogger('requests').setLevel(logging.WARNING)
# console = logging.StreamHandler
# console.setLevel(logging.ERROR)
# formatter = logging.Formatter('[%(levelname)s] %(message)s')
# console.setFormatter(formatter)
# logging.getLogger('').addHandler(console)


from .setting import *
from .api_wrapper import Wrapper


def create_api_wrapper(nodeHost=DEFAULT_NODE, apiKey=DEFAULT_NODE_API_KEY):
    return Wrapper(nodeHost, apiKey)


from .chain import *


def testnet_chain(apiWrapper=create_api_wrapper(DEFAULT_TESTNET_NODE, DEFAULT_TESTNET_API_KEY)):
    return Chain(TESTNET_CHAIN, TESTNET_CHAIN_ID, ADDRESS_VERSION, apiWrapper)


def mainnet_chain(apiWrapper=create_api_wrapper()):
    return Chain(DEFAULT_CHAIN, DEFAULT_CHAIN_ID, ADDRESS_VERSION, apiWrapper)
