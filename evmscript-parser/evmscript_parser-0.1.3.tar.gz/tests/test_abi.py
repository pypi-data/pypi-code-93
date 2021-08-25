"""Tests of getting ABI from different sources."""
from evmscript_parser.abi.etherscan import ABIEtherscan


def test_etherscan_api(api_key, abi_positive_example):
    """Run tests for getting ABI from Etherscan API."""
    contract, sign, name = abi_positive_example
    assert ABIEtherscan(
        api_key, contract, 'mainnet'
    ).get_func_abi(sign).get('name', 'no answer') == name
