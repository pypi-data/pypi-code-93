"""Constants used in many bridgeobjects modules."""

__all__ = ['SEATS', 'ROLES', 'VULNERABLE', 'CALLS', 'CONTRACTS', 'SUIT_NAMES',  'RANKS',
           'SUITS', 'BALANCED_SHAPES', 'SEMI_BALANCED_SHAPES',
           'SHAPES', 'SHAPE_PROBABILITIES', 'HONOUR_POINTS', 'CARD_NAMES',
           'DISPLAY_SUIT_ORDER']

from typing import List

from .suit import Clubs, Diamonds, Hearts, Spades

#: valid seats names at the bridge table
SEATS = ['N', 'E', 'S', 'W']

#: valid roles for players
ROLES = {'Opener': 0,
         'Responder': 1,
         'Overcaller': 2,
         'Advancer': 3,
         0: 'Opener',
         1: 'Responder',
         2: 'Overcaller',
         3: 'Advancer',
    }

#: valid vulnerable values
VULNERABLE = ['None', 'NS', 'EW', 'Both', 'All']

#: valid call names (P=Pass, D=Double, R=Redouble, A=All pass)
CALLS = ['1C', '1D', '1H', '1S', '1NT',
         '2C', '2D', '2H', '2S', '2NT',
         '3C', '3D', '3H', '3S', '3NT',
         '4C', '4D', '4H', '4S', '4NT',
         '5C', '5D', '5H', '5S', '5NT',
         '6C', '6D', '6H', '6S', '6NT',
         '7C', '7D', '7H', '7S', '7NT',
         'P', 'D', 'R', 'A']


def _make_contracts():
    """Generate valid contract names from CALLS."""
    contracts = [call for call in CALLS if call[0].isnumeric()]
    contracts.extend([''.join([call, 'X']) for call in CALLS if call[0].isnumeric()])
    contracts.extend([''.join([call, 'XX']) for call in CALLS if call[0].isnumeric()])
    return contracts


#: valid contract names
CONTRACTS = _make_contracts()

#: Suit names list
SUIT_NAMES = ['C', 'D', 'H', 'S']

#: card ranks
RANKS = ['x', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

#: Suits dictionary
SUITS = {'C': Clubs(), 'D': Diamonds(), 'H': Hearts(), 'S': Spades()}

DISPLAY_SUIT_ORDER = 'SHCD'


def _make_cards_names() -> List[str]:
    """Return a list of cards."""
    card_names = []
    for rank in RANKS[1:]:
        for suit in SUITS:
            card_names.append(''.join([rank, suit]))
    return card_names


CARD_NAMES = _make_cards_names()


#: balanced hand shapes
BALANCED_SHAPES = [[4, 3, 3, 3], [4, 4, 3, 2], [5, 3, 3, 2]]

#: semi-balanced hand shapes
SEMI_BALANCED_SHAPES = [[5, 4, 2, 2], [5, 4, 3, 1], [6, 3, 2, 2]]

#: the relative probability (per 10,000 hands) of having the number of high card points given by the index.
# (e.g. the probability of being dealt a hand with 1 high card point is 79/1000 = 0.079).
# N.B. Highest point count catered for is 26.
POINTS_PROBABILITIES = [36, 79, 136, 246, 385, 519, 655, 803, 889, 936,
                        941, 894, 803, 691, 569, 442, 331, 236, 161, 104,
                        64, 38, 21, 11, 6, 3, 1]

#: possible hand shapes (shapes with a probability of less than 1 in 10,000 of occurring have been omitted).
SHAPES = [[4, 4, 3, 2], [5, 3, 3, 2], [5, 4, 3, 1], [5, 4, 2, 2],
          [4, 3, 3, 3], [6, 3, 2, 2], [6, 4, 2, 1], [6, 3, 3, 1],
          [5, 5, 2, 1], [4, 4, 4, 1], [7, 3, 2, 1], [6, 4, 3, 0],
          [5, 4, 4, 0], [5, 5, 3, 0], [6, 5, 1, 1], [6, 5, 2, 0],
          [7, 2, 2, 2], [7, 4, 1, 1], [7, 4, 2, 0], [7, 3, 3, 0],
          [8, 2, 2, 1], [8, 3, 1, 1], [7, 5, 1, 0], [8, 3, 2, 0],
          [6, 6, 1, 0], [8, 4, 1, 0], [9, 2, 1, 1], [9, 3, 1, 0],
          [9, 2, 2, 0], [7, 6, 0, 0]]

#: the 30 most common hand shapes and their relative probability (per 10,000 hands).
# (Shapes with a probability of occurring of less than 1 in 10,000 have been omitted.)
SHAPE_PROBABILITIES = {"4432": 2155,
                       "5332": 1552,
                       "5431": 1293,
                       "5422": 1058,
                       "4333": 1054,
                       "6322": 564,
                       "6421": 470,
                       "6331": 345,
                       "5521": 317,
                       "4441": 299,
                       "7321": 188,
                       "6430": 133,
                       "5440": 124,
                       "5530": 90,
                       "6511": 71,
                       "6520": 65,
                       "7222": 51,
                       "7411": 39,
                       "7420": 36,
                       "7330": 27,
                       "8221": 19,
                       "8311": 12,
                       "7510": 11,
                       "8320": 11,
                       "6610": 7,
                       "8410": 5,
                       "9211": 2,
                       "9310": 1,
                       "9220": 1,
                       "7600": 1
                       }

#: the Milton Work points count for an honour.
HONOUR_POINTS = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}
