"""
Getting contracts ABI through Etherscan API.
"""
import json
import time
import logging
import requests

from functools import lru_cache, partial
from typing import (
    Optional
)

from .base import (
    ABI, ABI_T
)

# ============================================================================
# ===================== Constants ============================================
# ============================================================================

DEFAULT_NET = 'goerli'
NET_URL_MAP = {
    'mainnet': 'https://api.etherscan.io',
    'goerli': 'https://api-goerli.etherscan.io',
    'kovan': 'https://api-kovan.etherscan.io',
    'rinkebay': 'https://api-rinkeby.etherscan.io',
    'ropsten': 'https://api-ropsten.etherscan.io'
}
SUCCESS = '1'
MINIMUM_RETRIES = 1
CACHE_SIZE = 128


# ============================================================================
# ================================ Utilities =================================
# ============================================================================


@lru_cache(maxsize=CACHE_SIZE)
def _send_query(
        module: str, action: str, api_key: str, address: str,
        retries: int, specific_net: str
) -> str:
    """
    Send query to Etherscan API.

    :param module: str, part of Etherscan API.
    :param action: str, concrete function from API.
    :param api_key: str, API credentials.
    :param address: str, address of target contract.
    :param retries: int, number of retry in case of unsuccessful api call.
    :param specific_net: str, name of target net.
    :return: str, encoded json description of abi.
    :exception HTTPError in case of error at network layer.
    :exception RuntimeError in case of error in api calls.
    """
    retries = max(MINIMUM_RETRIES, retries)

    if specific_net not in NET_URL_MAP:
        raise KeyError(f'Unexpected name of net. '
                       f'Should be one of: '
                       f'{str(NET_URL_MAP.keys())}')

    url = NET_URL_MAP[specific_net]
    parameters = '&'.join([
        f'{name}={value}'
        for name, value in zip(
            ['module', 'action', 'address', 'apikey'],
            [module, action, address, api_key]
        )
    ])
    query = f'{url}/api?{parameters}'

    data = {}
    initial_wait = 0
    increase_wait = 1
    for ind in range(retries):
        logging.debug(
            f'Send query to Etherscan API; retry: {ind + 1}/{retries}; '
            f'sleep for {initial_wait} seconds.'
        )
        time.sleep(initial_wait)

        response = requests.get(query, headers={'User-Agent': ''})
        response.raise_for_status()

        data = response.json()

        if data['status'] == SUCCESS:
            return data['result']

        initial_wait += increase_wait
        increase_wait *= 2

    message = data.get('message', 'unknown')
    result = data.get('result', 'unknown')
    failed_reason = f'{message}; {result}'
    raise RuntimeError(f'Failed reason: {failed_reason}')


"""Alias for calling getabi functionality."""
_get_contract_abi = partial(_send_query, 'contract', 'getabi')


def get_abi(
        api_key: str, address: str, specific_net: str,
        retries: int = 5
) -> ABI_T:
    """
    Get ABI of target contract by calling to Etherscan API.

    :param api_key: str, API credentials.
    :param address: str, address of target contract.
    :param retries: int, number of retry in case of unsuccessful api call.
    :param specific_net: str, name of target net.
    :return: List[Dict[str, Any]], abi description.
    :exception HTTPError in case of error at network layer.
    :exception RuntimeError in case of error in api calls.
    """
    return json.loads(_get_contract_abi(
        api_key, address, retries, specific_net
    ))


# ============================================================================
# ============================== ABI =========================================
# ============================================================================

class ABIEtherscan(ABI):
    """
    Getting contracts ABI through Etherscan API.
    """

    def __init__(
            self, api_key: str, address: str,
            specific_net: Optional[str] = None,
            retries: int = 5
    ):
        """
        Create instance for getting ABI through Etherscan API.

        :param api_key: str, API credentials.
        :param address: str, address of target contract.
        :param specific_net: str, name of target net.
        :exception HTTPError in case of error at network layer.
        :exception RuntimeError in case of error in api calls.
        """
        if specific_net is None:
            specific_net = DEFAULT_NET
        self._api_key = api_key
        self._address = address
        self._specific_net = specific_net
        self._retries = retries
        super().__init__()

    def _load_abi(self) -> ABI_T:
        return get_abi(
            self._api_key, self._address, self._specific_net, self._retries
        )
