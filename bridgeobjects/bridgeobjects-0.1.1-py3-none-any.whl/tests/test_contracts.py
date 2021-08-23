"""A set of tests for the bridgeobjects Contract class."""
import pytest

from ..source.constants import SUITS
from ..source.contract import Contract, Call
from ..source.denomination import Denomination


def test_contract_name_valid():
    """Ensure that the contract name is correct: valid names."""
    assert Contract('1S').name == '1S'


def test_contract_name_invalid():
    """Ensure that the contract name is correct: invalid names."""
    with pytest.raises(ValueError) as exc_info:
        contract = Contract('1Q')
    assert True


def test_contract_is_nt():
    """Ensure that the contract is_nt is correct: valid names."""
    assert not Contract('1S').is_nt
    assert Contract('3NT')
    contract = Contract()
    assert contract.is_nt == False


def test_contract_repr():
    """Ensure that the contract repr string is correct."""
    contract = Contract('4S', 'E')
    assert repr(contract) == 'Contract("4S", "E")'


def test_contract_str():
    """Ensure that the contract str string is correct."""
    contract = Contract('4S', 'E')
    assert str(contract) == 'Contract. 4S by E'


def test_contract_name_setter():
    """Ensure that the contract name is correct: invalid names."""
    contract = Contract()
    with pytest.raises(ValueError) as exc_info:
        contract.name = '1Q'
    assert True


def test_contract_name_setter_valid():
    """Ensure that the contract name is correct."""
    contract = Contract()
    contract.name = '5D'
    contract.declarer = 'S'
    assert repr(contract) == 'Contract("5D", "S")'


def test_contract_call_setter_valid():
    """Ensure that the contract call is correct."""
    contract = Contract()
    contract.call = Call('3H')
    contract.declarer = 'N'
    assert repr(contract) == 'Contract("3H", "N")'


def test_contract_call_setter_invalid_type():
    """Ensure that the contract call is correct."""
    contract = Contract()
    with pytest.raises(TypeError) as exc_info:
        contract.call = None


def test_contract_call_setter_invalid():
    """Ensure that the contract call is correct."""
    contract = Contract()
    with pytest.raises(ValueError) as exc_info:
        contract.call = 'W'
    assert True
    with pytest.raises(ValueError) as exc_info:
        contract.call = Call('8NT')
    with pytest.raises(ValueError) as exc_info:
        contract.call = Call('0S')
    assert True


def test_contract_call_setter_valid_double():
    """Ensure that the contract call is correct."""
    contract = Contract()
    contract.call = '3C'
    assert contract.call == Call('3C')
    contract.call = Call('3NTX')
    assert contract.call.name == '3NTX'


def test_contract_trump_suit_setter_valid():
    """Ensure that the contract trump suit is correct."""
    contract = Contract()
    contract.trump_suit = SUITS['H']
    contract.declarer = 'N'
    assert contract.trump_suit.name == 'H'
    contract = Contract()
    contract.trump_suit = 'C'
    contract.declarer = 'N'
    assert contract.trump_suit.name == 'C'


def test_contract_trump_suit_setter_invalid():
    """Ensure that the contract trump suit is correct."""
    contract = Contract()
    with pytest.raises(TypeError) as exc_info:
        contract.trump_suit ='W'
    assert True


def test_contract_denomination_valid():
    """Ensure that the contract trump suit is correct."""
    contract = Contract()
    contract.trump_suit = SUITS['H']
    assert contract.denomination == Denomination('H')


def test_contract_declarer_invalid():
    """Ensure that the contract trump suit is correct."""
    contract = Contract()
    with pytest.raises(ValueError) as exc_info:
        contract.declarer ='M'
    assert True
