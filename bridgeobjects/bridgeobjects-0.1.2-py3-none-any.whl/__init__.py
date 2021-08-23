

"""
    The bridgeobjects package exposes the following classes:
    (inspect the individual modules to see their APIs):

    constants: various constants used throughout the package, e.g. SEATS = ['N', 'E', 'S', 'W'];
    board: represents a board of 4 hands;
    hand: holds the 13 cards dealt to tht hand;
    card: a single card in a hand, board or trick;
    suit: one of Spades, Hearts, Clubs or diamonds;
    denomination: the name of a call in the auction or contract, it includes the four suits and NT;
    auction: the calls made on a particular board
    contract: the contract reach on a board;
    call: an individual call made to reach a contract
    event: the match or competition at which the boards are played:
    trick: four  cards played which one pair wins:
    file_operations: a module to load or save events in a PBN, RBN or LIN format.
"""

from bridgeobjects.source.constants import *
from bridgeobjects.source.board import *
from bridgeobjects.source.hand import *
from bridgeobjects.source.card import *
from bridgeobjects.source.suit import *
from bridgeobjects.source.auction import *
from bridgeobjects.source.contract import *
from bridgeobjects.source.call import *
from bridgeobjects.source.event import *
from bridgeobjects.source.trick import *
from bridgeobjects.source.file_operations import *
from bridgeobjects.source.denomination import * # type: ignore

from ._version import __version__
VERSION = __version__
