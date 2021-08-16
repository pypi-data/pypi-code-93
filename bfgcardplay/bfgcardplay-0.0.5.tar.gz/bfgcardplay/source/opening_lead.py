""" Opening leads for Card Player."""

from .opening_lead_card import opening_lead_card
from .opening_lead_suit import opening_lead_suit


def opening_lead(board):
    """Return the proposed opening lead for the board."""
    if not board.contract.declarer:
        return None
    opening_suit = opening_lead_suit(board)
    cards = [card for card in board.hands[board.contract.leader].cards if card.suit == opening_suit]
    opening_card = opening_lead_card(cards, board.contract)
    return (opening_suit, opening_card)
