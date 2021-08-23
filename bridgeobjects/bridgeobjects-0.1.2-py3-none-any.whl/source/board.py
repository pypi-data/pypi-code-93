"""The Board class for the bridgeobjects package."""

from typing import Dict, List, Union, Tuple

from .card import Card
from .hand import Hand
from .auction import Auction
from .contract import Contract
from .trick import Trick

from .constants import SEATS, RANKS, SUITS, VULNERABLE, SUIT_NAMES, CARD_NAMES

__all__ = ['Board']


class Board(object):
    """
    The board object for the bridgeobjects module.

    A board is the collection of four hands used in Playing a contract.
    It supports vulnerability.

    Parameters
    ----------
    identifier: (string) board's identifier
    hands: (dict) board's hands, a dict of Hand objects
            or
            (list) a list of hand objects.
    """

    def __init__(self, identifier: Union[str, None]='', hands: Union[List[Hand], None]=None):
        # identifier/board number: a positive integer (as string)  under PBN but
        # can be any character combination under RPN.
        if identifier is None:
            identifier = ''
        self.identifier = identifier

        self.vulnerable = ''  # must be in VULNERABLE.
        if hands is None:
            self._hands: Dict[object, Hand] = dict()
            self._hands_by_index: Dict[int, Hand] = dict()
            self._hands_by_seat: Dict[str, Hand]  = dict()
        else:
            (self._hands, self._hands_by_index, self._hands_by_seat)  = self._set_hands(hands)

        self._dealer = ''    # must be in SEATS
        self._dealer_index = -1
        self.north = ""
        self.south = ""
        self.west = ""
        self.east = ""
        self.result = ""
        self._declarer = ''    # must be in SEATS
        self._declarer_index = -1
        self._contract = Contract()
        self.auction = Auction()
        self.tricks: List[Trick] = []
        self.NS_tricks = 0
        self.EW_tricks = 0
        self.play_notes: Dict[str, str] = {}
        self.description = ""

    def _set_hands(self, hands: List[Hand]) -> Tuple[Dict[object, Hand], Dict[int, Hand], Dict[str, Hand]]:
        """Return the hands as a dict."""
        # If hands is a list then 0 is the North hand and proceed clockwise.
        # If hands is a dict, then determine if the keys are numeric (position) or
        # alpha (SEATS) and proceed accordingly.
        hand_dict: Dict[object, Hand] = dict()
        hands_by_index: Dict[int, Hand] = dict()
        hands_by_seat: Dict[str, Hand] = dict()
        # hands is a list
        if isinstance(hands, list):
            for key, hand in enumerate(hands):
                if not isinstance(hand, Hand):
                    raise TypeError('item must be a Hand')
                hand_dict[key] = hand
                hand_dict[SEATS[key]] = hand
                hands_by_index[key] = hand
                hands_by_seat[SEATS[key]] = hand
        # hands is a dict
        elif isinstance(hands, dict):
            for key, hand in hands.items():
                if not isinstance(hand, Hand):
                    raise TypeError('item must be a Hand')
                if isinstance(key, int):
                    if key not in range(4):
                        raise ValueError(f'{key} is invalid hand index')
                    hands_by_index[key] = hand
                    hands_by_seat[SEATS[key]] = hand
                    hand_dict[key] = hand
                    hand_dict[SEATS[key]] = hand
                if isinstance(key, str):
                    if key not in SEATS:
                        raise ValueError(f'{key} is invalid hand index')
                    hands_by_seat[key] = hand
                    hands_by_index[SEATS.index(key)] = hand
                    hand_dict[key] = hand
                    hand_dict[SEATS.index(key)] = hand
        else:
            raise TypeError('Hands must be a list or a  dict')
        if len(hands_by_index) == 3:
            hand = self.build_fourth_hand(hands_by_index)
            for key in range(4):
                if key not in hands_by_index:
                    hands_by_index[key] = hand
                    hands_by_seat[SEATS[key]] = hand
                    hand_dict[key] = hand
                    hand_dict[SEATS[key]] = hand
                    break
        return (hand_dict, hands_by_index, hands_by_seat)

    def __repr__(self) -> str:
        """Return a repr string for the object."""
        if self._hands_by_index:
            return f'Board("{self._identifier}", {self._hands_by_index})'
        else:
            return f'Board("{self._identifier}")'

    def __str__(self) -> str:
        """Return a str string for the object."""
        return f'Board("{self._identifier}")'

    @property
    def vulnerable(self) -> str:
        """
        Return the board's vulnerable status as a string.
        Valid values are in the constant VULNERABLE:
            VULNERABLE = ['None', 'NS', 'EW', 'Both', 'All']
        """
        return self._vulnerable

    @vulnerable.setter
    def vulnerable(self, value: str):
        """Set the vulnerable property to an allowed value."""
        if value and value not in VULNERABLE:
            raise ValueError('f{value} not a valid value for vulnerable')
        if value == 'All':
            value = 'Both'
        self._vulnerable = value

    @property
    def declarer(self) -> str:
        """
        Return the board's declarer as a string.
        Valid values are in the constant SEATS.
        """
        return self._declarer

    @declarer.setter
    def declarer(self, value: str):
        """Set the declarer property to an allowed value."""
        if value:
            assert(value in SEATS), 'invalid seat for declarer'
            declarer_index = SEATS.index(value)
            self._declarer_index = declarer_index
        self._declarer = value

    @property
    def declarer_index(self) -> int:
        """
        Return the board's declarer index as an integer.
        Valid values are in the range 0 to 3.
        """
        return self._declarer_index

    @declarer_index.setter
    def declarer_index(self, value: int):
        """Set the declarer index property to an allowed value."""
        if value in range(4):
            self._declarer_index = value
            self._declarer = SEATS[value]
        else:
            value = -1
            self._declarer = ''
        self._declarer_index = value

    @property
    def dealer(self) -> str:
        """
        Return the board's dealer as a string.
        Valid values are in the constant SEATS.
        """
        return self._dealer

    @dealer.setter
    def dealer(self, value: str):
        """Set the dealer property to an allowed value."""
        if value not in SEATS:
            self._dealer_index = -1
            self._dealer = ''
            raise ValueError (f'Not a valid seat, {value}')
        self._dealer_index = SEATS.index(value)
        self._dealer = value

    @property
    def dealer_index(self) -> int:
        """
        Return the board's dealer index as an integer.
        Valid values are in the range 0 to 3.
        """
        return self._dealer_index

    @dealer_index.setter
    def dealer_index(self, value: int):
        """Set the dealer index property to an allowed value."""
        if value in range(4):
            self._dealer = SEATS[value]
        else:
            if value:
                self._dealer = ''
                self._dealer_index = -1
                raise ValueError('Dealer index not in 0 to 3')
        self._dealer_index = value

    @property
    def auction(self) -> Auction:
        """Return the board's auction as an auction class."""
        return self._auction

    @auction.setter
    def auction(self, value: Auction):
        """Set the auction property to an allowed value."""
        self._auction = value

    @property
    def contract(self) -> Contract:
        """Assign contract property."""
        return self._contract

    @contract.setter
    def contract(self, value: Contract):
        """Set contract property."""
        self._contract = value

    @property
    def hands(self):
        """Return hands as a dict."""
        return self._hands

    @hands.setter
    def hands(self, value: List[Hand]):
        """Set the hand dicts."""
        (self._hands, self._hands_by_index, self._hands_by_seat)  = self._set_hands(value)

    @property
    def hands_by_index(self) -> Dict[int, Hand]:
        """Return a dict of hands keyed by index. 0 is N, etc."""
        return self._hands_by_index

    @property
    def hands_by_seat(self) -> Dict[str, Hand]:
        """Return a dict of hands keyed by seat. N, E,  etc."""
        return self._hands_by_seat

    @staticmethod
    def full_pack() -> List[Card]:
        """Return a list containing every card in the pack."""
        pack = []
        for suit in SUITS:
            pack.extend([Card(rank, suit) for rank in RANKS[1:]])
        return pack

    @staticmethod
    def build_fourth_hand(existing_hands: Union[Dict[object, Hand], Dict[int, Hand]]) -> Hand:
        """Build the fourth hand based on the other three hands."""
        used_cards = []
        missing_cards = []
        # Create a list of cards used by other three hands.
        for index, hand in existing_hands.items():
            del index
            for card in hand.cards:
                used_cards.append(card.name)
        # Build a hand from the cards not already used.
        for suit in reversed(SUIT_NAMES):
            for rank in reversed(RANKS[1:]):
                card = Card(rank, suit)
        for name in CARD_NAMES:
            if name not in used_cards:
                missing_cards.append(Card(name))
        fourth_hand = Hand(missing_cards)
        return fourth_hand

    def board_to_pbn(self) -> List[str]:
        """Return a board as a list of strings in pbn format."""
        output = [
            f'[Board "{self._identifier}"]',
            f'[Dealer "{self.dealer}"]'
        ]
        if self.description:
            output.append(f'[Description "{self.description}"]')
        if self.dealer:
            output.append(f'[Deal "{self.dealer}:{self.pbn_hands()}"]')
        return output

    def pbn_hands(self, delimiter: str=' ') -> str:
        """Return a board's hands as a string in pbn format."""
        hands_list = []
        dealer_index = SEATS.index(self.dealer)
        for index in range(4):
            seat = (dealer_index + index) % 4
            hand = self._hands[seat]
            hand_list = []
            for suit_name in reversed(SUIT_NAMES):
                suit_cards = []
                for rank in reversed(RANKS[1:]):
                    for card in hand.cards:
                        if card.name == ''.join([rank, suit_name]):
                            suit_cards.append(card.rank)
                hand_list.append(''.join(suit_cards))
            hands_list.append('.'.join(hand_list))
        return delimiter.join(hands_list)

    @property
    def identifier(self) -> str:
        """Return the board's identifier."""
        return self._identifier

    @identifier.setter
    def identifier(self, value: str):
        """Set the identifier value."""
        if not (isinstance(value, str) or isinstance(value, int)):
            raise TypeError('Identifier must be a string')
        self._identifier = str(value)