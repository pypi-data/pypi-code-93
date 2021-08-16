
from bridgeobjects import Card, Suit


SUIT_SELECTION_REASON = {
    '000': 'No reason applied',
    '001': '5+ card suit with honour',
    '002': 'Best suit sequence',
    '003': 'Best long suit',
    '004': 'Long suit with most honours',
    '005': 'Only four card suit',
    '006': 'Best of 4 card suits',
    '007': 'Long_suit with no ace',
    '008': 'Strongest long suit',
    '009': '4+ card suit with touching honours',
    '010': 'Best 4 card suit with no split honours',
    '011': 'Best 4 card suit with near sequence',
    '012': 'Best 4 card suit with interior sequence',
    '013': 'Suit bid by partner',
    '014': 'Only non-deprecated suit',
    '015': 'Non-deprecated suit - 2 honours',
    '016': 'Non-deprecated suit - doubleton, no honour',
    '017': 'Non-deprecated suit - no honour',
    '018': 'Longest non-deprecated suit',
    '019': 'Unbid major',
    '020': "Partner's suit",
    '021': '5+ card suit with entries',
    '022': '3+ card suit with no honour',
    '023': 'Single honour suit headed by K',
    '024': 'Single honour suit headed by Q',
    '025': 'Single honour suit headed by J',
    '026': "Probable shortage in partner's hand",
    '027': 'Touching honours',
    '028': 'Trumps',
    '029': 'Long suit',
    '030': 'Defending slam - try to establish second trick',
    '031': 'Defending slam - partner indicated suit',
    '032': 'Defending slam - partner indicated suit: unusual double',
}

CARD_SELECTION_REASON = {
    '000': 'No reason applied',
    '001': 'Top of doubleton',
    '002': 'K from AK doubleton',
    '003': 'Top of touching honours',
    '004': 'Fourth highest',
    '005': 'Middle with no honour',
    '006': 'Fourth highest from a single honour',
    '007': 'Bottom of triplet with an honour',
    '008': 'Top of touching honours in triplet',
    '009': 'Top of internal sequence',
    '010': 'Triplet with two honours, third card',
    '011': "Bottom from QTx",
    '013': 'A from suit headed by an A',
    '014': 'Second highest from 4 rags',
    '015': 'Singleton',
    '020': 'Top of solid sequence',
    '021': 'Top of near sequence',
    '022': 'Top of internal sequence',
    '023': 'Top of touching honours',
}

class SelectedSuit(Suit):
    """An extension of the Suit class that contains a reason code for suit_selection."""

    def __init__(self, name=None, selection_reason='000', *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self._selection_reason = selection_reason

    def __str__(self):
        """Return the str value."""
        return (f'Suit("{self.name}"), {SUIT_SELECTION_REASON[self._selection_reason]}')

    @property
    def selection_reason(self):
        """Return the value of the property selection_reason."""
        return self._selection_reason

    @selection_reason.setter
    def selection_reason(self, value):
        """Set the value of the property selection_reason."""
        self._selection_reason = value

    # @property
    # def selection_reason(self):
    #     """Return the value of the property selection_reason."""
    #     return self._selection_reason()

    # def _selection_reason(self):
    #     """Generate the selection reason text."""
    #     if self._selection_reason not in SUIT_SELECTION_REASON:
    #         self._selection_reason = '000'
    #     return self.SUIT_SELECTION_REASON[self._selection_reason]


class SelectedCard(Card):
    """An extension of the Card class that contains a reason code for suit_selection."""

    def __init__(self, name, selection_reason='000', *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.selection_reason = selection_reason

    def __str__(self):
        """Return the str value."""
        return f'Card("{self.name}"), {self.selection_reason}, {CARD_SELECTION_REASON[self.selection_reason]}'