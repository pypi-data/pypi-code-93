"""A set of tests for the bridgeobjects Auction class."""

import pytest
import os

from ..source.auction import Auction
from ..source.call import Call
from ..source.file_operations import load_pbn

DATA_PATH = 'test_data/'
load_path = os.path.join(DATA_PATH, 'pbn_auction_1.pbn')
event = load_pbn(load_path)[0]
test_auction = event.boards[0].auction

"""
1D      1S   3H =1= 4S
4NT =2= X    Pass   Pass
5C      X    5H     X
Pass    Pass Pass

auction.calls = [
    Call('1D'), Call('1S'), Call('3H'), Call('4S'),
    Call('4NT'), Call('D'), Call('P'), Call('P'),
    Call('5C'), Call('D'), Call('5H'), Call('D'),
    Call('P'), Call('P'), Call('P'),
]
"""


def test_first_caller_valid():
    """Test the first caller validation"""
    with pytest.raises(TypeError):
        auction = Auction(first_caller=3)
    with pytest.raises(ValueError):
        auction = Auction(first_caller='L')


def test_calls_valid():
    """Test the call validation"""
    with pytest.raises(TypeError):
        auction = Auction(calls=3)
    with pytest.raises(ValueError):
        auction = Auction(calls=['0NT'])
    auction = Auction(calls=['1NT', 'P', 'P', 'P'])
    assert auction.calls == [Call('1NT'), Call('P'), Call('P'), Call('P')]


def test_auction_caller():
    """Ensure that the auction caller is correct."""
    auction = Auction(first_caller='N')
    assert auction.first_caller == 'N'


def test_auction_caller_assign():
    """Ensure that the auction caller assignment is correct."""
    auction = Auction()
    auction.first_caller = 'N'
    assert auction.first_caller == 'N'


def test_auction_repr():
    """Ensure that the auction __repr__ is correct."""
    assert repr(test_auction) == 'Auction: 1D, 1S, 3H, 4S, 4NT, D, P, P, 5C, D, 5H, D, P, P, P'


def test_auction_str():
    """Ensure that the auction __str__ is correct."""
    assert str(test_auction) == 'Auction: 1D, 1S, 3H, 4S, 4NT, D, P, P, 5C, D, 5H, D, P, P, P'


def test_auction_note_keys():
    """Ensure that the auction  note_keys is correct."""
    assert test_auction.note_keys == ['', '', '1', '', '2', '', '', '', '', '', '', '', '', '', '']


def test_auction_note_key_validation():
    """Ensure that the auction note key setter is correct."""
    with pytest.raises(TypeError):
        auction = Auction()
        auction.note_keys = '1'
    with pytest.raises(TypeError):
        auction = Auction()
        auction.note_keys = [1, 2, 3]


def test_auction_note_key_setter():
    """Ensure that the auction note key setter is correct."""
    auction = Auction()
    auction.note_keys = ['', '', '1', '']
    assert auction.note_keys == ['', '', '1', '']


def test_auction_notes_setter():
    """Ensure that the auction notes setter is correct."""
    with pytest.raises(TypeError):
        auction = Auction()
        auction.notes = '1'
    auction = Auction()
    auction.notes = {'1': 'test note 1'}
