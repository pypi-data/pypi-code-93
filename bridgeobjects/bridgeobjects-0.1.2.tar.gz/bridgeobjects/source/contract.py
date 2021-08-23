"""The contract object for the bridgeobjects module."""

from typing import List, Union

from .denomination import Denomination
from .call import Call
from .suit import Suit
from .auction import Auction
from .constants import CONTRACTS, SEATS, SUITS

__all__ = ['Contract']


class Contract(object):
    """
    A Contract object for the bridgeobjects module.

    A contract has a declarer, a denomination.

    Parameters
    ----------
    name: (str) call's name
    declarer: (str) the declarer's seat name

    Example
    -------
        contract = Contract("3NTX", "S")

    It is also identified (if appropriate) as either major, minor or no trumps.
    """

    def __init__(self, name: str='', declarer: str='', auction: Union[Auction, None]=None):
        self._name = name
        self._declarer = declarer
        self.auction = self._analyse_auction(auction)
        self._is_nt = False
        self._denomination = None
        if self._name and self._is_valid(self._name):
            self._call = Call(self._name)
            self._denomination = self._get_denomination(self._name)
            if self._denomination:
                self._is_nt = self._denomination.is_nt
            if self._is_nt:
                self._trump_suit = None
            else:
                self._trump_suit = SUITS[self._name[1]]
        else:
            self._trump_suit = None
            self._call = Call('')
        if self._name:
            self._level = int(self._name[0])
        else:
            self._level = 0
        self._modifier  = ''

    def __repr__(self) -> str:
        """Return the repr string for the object."""
        return f'Contract("{self._call.name}", "{self._declarer}")'

    def __str__(self) -> str:
        """Return the str string for the object."""
        return f'Contract. {self._call.name} by {self._declarer}'

    @property
    def declarer(self) -> str:
        """Return the declarer value."""
        return self._declarer

    @declarer.setter
    def declarer(self, value: str):
        """Assign the declarer value."""
        if value and value not in SEATS:
            raise ValueError(f"'{value}' is not a valid seat")
        self._declarer = value

    @property
    def leader(self) -> Union[str, None]:
        """Return the dealer value."""
        if self._declarer:
            return SEATS[(SEATS.index(self._declarer) + 1) % 4]
        return None

    @property
    def name(self) -> str:
        """Return the name value."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Assign the name value."""
        if self._is_valid(value):
            self._denomination = self._get_denomination(value)
            self._is_nt = self._denomination.is_nt
            if not self._is_nt:
                self._trump_suit = SUITS[value[1]]
        self._name = value
        self._call = Call(self._name)

    @property
    def call(self) -> Call:
        """Return the call value."""
        return self._call

    @call.setter
    def call(self, value: Union[str, Call]):
        """Assign the denomination value."""
        if isinstance(value, str):
            if value in CONTRACTS:
                value = Call(value)
            else:
                raise ValueError(f'{value} is not a valid Call')
        elif not isinstance(value, Call):
            raise TypeError(f'{value} is not a Call')
        self._call = value
        self._denomination = self._get_denomination(value.name)
        self._is_nt = self._denomination.is_nt or self._denomination.is_no_trumps

    @property
    def trump_suit(self) -> Union[Suit, None]:
        """Return a value for the trump suit as a Suit."""
        return self._trump_suit

    @trump_suit.setter
    def trump_suit(self, value: Union[str, Suit]):
        """Set the value of the trump suit as a Suit."""
        if isinstance(value, str) and value in SUITS:
            value = SUITS[value]
        elif not isinstance(value, Suit):
            raise TypeError(f'{value} is not a suit.')
        self._denomination = Denomination(value.name)
        self._trump_suit = value

    @property
    def level(self) -> int:
        """Return the level value."""
        return self._level

    @property
    def denomination(self) -> Union[Denomination, None]:
        """Return the denomination value."""
        return self._denomination

    @property
    def is_nt(self) -> bool:
        """Return True if the denomination is NT."""
        return self._is_nt

    @property
    def modifier(self) -> str:
        """Return contract's modifier (i.e.: '', 'D' or 'R')."""
        return self._modifier

    @modifier.setter
    def modifier(self, value: str):
        """Set contract's modifier (i.e.: '', 'D' or 'R')."""
        if value in ['D', 'R']:
            self._modifier = value
        else:
            self._modifier = ''

    @staticmethod
    def _is_valid(name: str) -> bool:
        """Return True if the contact name is valid."""
        if name not in CONTRACTS:
            raise ValueError(f'{name} is not a valid contract')
        return True

    @staticmethod
    def _get_denomination(name: str) -> Denomination:
        """Return the denomination of the contract."""
        if name[1:3] == 'NT':
            return Denomination('NT')
        return Denomination(name[1])

    def _analyse_auction(self, auction: Union[Auction, None]) -> Union[Auction, None]:
        """Generate name and declarer from auction and return auction."""
        if auction:
            if auction.calls and auction.first_caller:
                if (self._three_final_passes(auction.calls) and
                        not self._passed_out(auction.calls)):
                    dealer_index = SEATS.index(auction.first_caller)

                    auction_calls = [call for call in auction.calls]
                    auction_calls.reverse()
                    for call in auction_calls:
                        if call.is_value_call:
                            break

                    denomination = call.denomination
                    for index, check_call in enumerate(auction.calls):
                        if check_call.denomination == denomination:
                            break
                    declarer_index = (dealer_index + index) % 4
                    self._declarer = SEATS[declarer_index]
                    self._name = call.name
                    return auction
        return None

    @staticmethod
    def _three_final_passes(calls: List[Call]) -> bool:
        """Return True if there have been three consecutive passes."""
        three_passes = False
        if len(calls) >= 4:
            if calls[-1].is_pass and calls[-2].is_pass and calls[-3].is_pass:
                three_passes = True
        return three_passes

    @staticmethod
    def _passed_out(calls: List[Call]) -> bool:
        """Return True if the board has been passed out."""
        if len(calls) != 4:
            return False
        for call in calls:
            if not call.is_pass:
                return False
        return True