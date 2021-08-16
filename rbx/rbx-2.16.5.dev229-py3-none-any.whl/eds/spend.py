from decimal import Decimal
from typing import NamedTuple


class CostFragment(NamedTuple):
    """Cost Fragment."""

    cost_type: str
    currency: str
    rate_card_currency: str
    value: Decimal

    @staticmethod
    def from_formula(formula):
        """Returns a CostFragment from a cost formula.

        The cost formula is expected to be a string containing value, currency +
        rate card currency and cost type each separated by an underscore:
        > `{value}_{currency}{rate_card_currency}_{cost_type}`
        """
        try:
            value, currencies, cost_type = tuple(formula.split('_'))
        except ValueError:
            raise SpendException(f'Invalid cost formula: {formula}')

        if len(currencies) != 6:
            raise SpendException(f'Invalid cost currency: {formula}')

        return CostFragment(cost_type=cost_type, currency=currencies[:3],
                            rate_card_currency=currencies[3:6], value=Decimal(value))


class Spend:
    """Calculate spend from a cost formula."""

    def __init__(self, cost_formula):
        self.fragments = []
        self.currency = None
        self.rate_card_currency = None

        if cost_formula:
            for formula in cost_formula.split('+'):
                fragment = CostFragment.from_formula(formula=formula)

                if self.currency is None:
                    self.currency = fragment.currency
                if self.rate_card_currency is None:
                    self.rate_card_currency = fragment.rate_card_currency

                if self.currency != fragment.currency:
                    raise SpendException(f'Currencies do not match: {cost_formula}')
                if self.rate_card_currency != fragment.rate_card_currency:
                    raise SpendException(f'Rate Card currencies do not match: {cost_formula}')

                self.fragments.append(fragment)


class SpendException(Exception):
    """Raised when an exception occurs in Spend."""
