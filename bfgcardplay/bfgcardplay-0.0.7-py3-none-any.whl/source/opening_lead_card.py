"""
    Opening leads for Card Player class.

    Returns  a card_player_components PlayedCard which includes
    name: str
    reason: str
"""

from typing import List, Union

from bridgeobjects import Card, Contract
from .card_player_components import SelectedCard


def opening_lead_card(suit_cards: List[Card], contract: Contract) -> SelectedCard:
    """Return the opening lead from a list of cards given the contract."""
    cards = sorted(suit_cards, key=lambda x: x.order, reverse=True)
    for card in cards:
        if card.value == 9:  # T is regarded as an honour
            card.is_honour = True

    try:
        selected_card = _select_card_from_suit(cards, contract)
    except:
        raise ValueError(f'No card selected from {cards}')
    return selected_card

def _are_adjacent(card_1: Card, card_2: Card) -> bool:
    """Return True if the cards are adjacent."""
    if abs(card_1.value - card_2.value) == 1:
        return True
    return False

def _select_card_from_suit(cards: List[Card], contract: Contract) -> SelectedCard:
    """Return the correct card from the selected suit."""
    # Suits with 3 cards
    if len(cards) == 3:
        return _select_card_from_triplet(cards, contract)

    # Doubleton
    if len(cards) == 2:
        return _select_card_from_doubleton(cards)

    # Singleton
    if len(cards) == 1:
        return SelectedCard(cards[0], '015')

    # Suits with 4 or more cards headed by an honour
    if len(cards) >= 4 and cards[0].is_honour:
        if contract.is_nt:
            return _select_card_for_nt_contract(cards)
        return _select_card_for_suit_contract(cards)

    # Second highest from four rags
    if len(cards) == 4:
        return SelectedCard(cards[1], '014')

    # Fourth highest from five or more rags
    return SelectedCard(cards[3], '004')

def _select_card_for_suit_contract(cards: List[Card]) -> SelectedCard:
    """Return the correct card for suit contract with four or more cards."""

    # NB Klinger's Guide to better cardplay overrides Basic Bridge for 4 card suits

    # Suit headed by an A
    if cards[0].rank == 'A':
        return SelectedCard(cards[0], '013')

    top_of_solid_sequence = is_solid_sequence(cards)
    if top_of_solid_sequence:
        return SelectedCard(top_of_solid_sequence, '020')

    top_of_near_sequence = is_near_sequence(cards)
    if top_of_near_sequence:
        return SelectedCard(top_of_near_sequence, '021')

    top_of_interior_sequence = is_interior_sequence(cards)
    if top_of_interior_sequence:
        return SelectedCard(top_of_interior_sequence, '022')

    top_of_touching_honours = touching_honours(cards)
    if top_of_touching_honours:
        return SelectedCard(top_of_touching_honours, '023')

    # Lead fourth highest from an honour
    return SelectedCard(cards[3], '004')

def _select_card_for_nt_contract(cards: List[Card]) -> SelectedCard:
    """Return the correct card in a NT contract with four or more cards."""

    top_of_solid_sequence = is_solid_sequence(cards)
    if top_of_solid_sequence:
        return SelectedCard(top_of_solid_sequence, '020')

    top_of_near_sequence = is_near_sequence(cards)
    if top_of_near_sequence:
        return SelectedCard(top_of_near_sequence, '021')

    top_of_interior_sequence = is_interior_sequence(cards)
    if top_of_interior_sequence:
        return SelectedCard(top_of_interior_sequence, '022')

    # Lead fourth highest from an honour
    return SelectedCard(cards[3], '004')

def _select_card_from_triplet(cards: List[Card], contract: Contract) -> SelectedCard:
    """Return the correct card from a three card suit."""

    # Suit headed by A and no K in a NT contract
    if contract.is_nt:
        if cards[0].rank == 'A' and cards[1].rank != 'K':
            return SelectedCard(cards[2], '007')

    if cards[0].rank == 'A':
        return SelectedCard(cards[0], '013')

    # Suit headed by an honour and are_adjacent card
    if cards[0].is_honour and _are_adjacent(cards[0], cards[1]):
        return SelectedCard(cards[0], '003')

    # Suit headed by an honour: top of two touching cards
    if (cards[1].is_honour and _are_adjacent(cards[1], cards[2])):
        return SelectedCard(cards[1], '008')

    # Suit headed by two honours
    if (cards[0].is_honour and cards[1].is_honour):
        return SelectedCard(cards[2], '010')

    # Suit headed by a single honour
    if (cards[0].is_honour and not cards[1].is_honour):
        return SelectedCard(cards[2], '007')

    # Return middle card
    return SelectedCard(cards[1], '005')

def _select_card_from_doubleton(cards: List[Card]) -> SelectedCard:
    """Return the correct card from a two card suit."""
    if cards[0].rank == 'A' and cards[1].rank == 'K':
        return SelectedCard(cards[1], '002')
    return SelectedCard(cards[0], '001')

def is_solid_sequence(cards: List[Card]) -> Union[SelectedCard, None]:
    """Returns the top of the solid sequence if there is one, or None."""
    if len(cards) < 3:
        return None
    for index in range(len(cards)-2):
        if (cards[index].value == cards[index+1].value + 1 and
            cards[index+1].value == cards[index+2].value + 1 and
            cards[index].value >= 9):
            return cards[index]
    return None

def is_near_sequence(cards: List[Card]) -> Union[SelectedCard, None]:
    """ Returns the top of a near sequence if there is one, or None.

        Definition taken from Klinger's Guide to better Card Play p7
    """
    if len(cards) < 3:
        return None

    for index in range(len(cards)-2):
        if (cards[index].is_honour and
                cards[index].value == cards[index+1].value + 1 and
                cards[index+1].value == cards[index+2].value + 2):
            return cards[index]
    return None

def is_interior_sequence(cards: List[Card]) -> Union[SelectedCard, None]:
    """ Returns the top of an interior sequence if there is one, or None.

        Definition taken from Klinger's Guide to better Card Play p7
    """
    if len(cards) < 3:
        return None

    for index in range(len(cards)-3):
        if (cards[index+1].is_honour and
                cards[index].value > cards[index+1].value + 1 and
                cards[index+1].value == cards[index+2].value + 1):
            return cards[index+1]
    return None

def touching_honours(cards: List[Card]) -> Union[SelectedCard, None]:
    """Returns the top of the touching honours if there is one, or None."""
    if len(cards) < 3:
        return None
    for index in range(len(cards)-1):
        if (cards[index].value == cards[index+1].value + 1 and
            cards[index].value >= 12):
            return cards[index]
    return None