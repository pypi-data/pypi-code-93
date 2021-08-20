# coding: utf8
# contract_gen 2020-05-19 11:24:17.124186

__all__ = ["AmortizationItem"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.amortization_frequency import AmortizationFrequency
from ..enum_types.amortization_type import AmortizationType


class AmortizationItem(ObjectDefinition):
    def __init__(
        self,
        start_date=None,
        end_date=None,
        amortization_frequency=None,
        amortization_type=None,
        remaining_notional=None,
        amount=None,
    ):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.amortization_frequency = amortization_frequency
        self.amortization_type = amortization_type
        self.remaining_notional = remaining_notional
        self.amount = amount

    @property
    def amortization_frequency(self):
        """
        Frequency of the Amortization
        :return: enum AmortizationFrequency
        """
        return self._get_enum_parameter(AmortizationFrequency, "amortizationFrequency")

    @amortization_frequency.setter
    def amortization_frequency(self, value):
        self._set_enum_parameter(AmortizationFrequency, "amortizationFrequency", value)

    @property
    def amortization_type(self):
        """
        Amortization type Annuity, Schedule, Linear, ....
        :return: enum AmortizationType
        """
        return self._get_enum_parameter(AmortizationType, "amortizationType")

    @amortization_type.setter
    def amortization_type(self, value):
        self._set_enum_parameter(AmortizationType, "amortizationType", value)

    @property
    def amount(self):
        """
        Amortization Amount at each Amortization Date
        :return: float
        """
        return self._get_parameter("amount")

    @amount.setter
    def amount(self, value):
        self._set_parameter("amount", value)

    @property
    def end_date(self):
        """
        End Date of an amortization section/window, or stepped rate
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def remaining_notional(self):
        """
        The Remaining Notional Amount after Amortization
        :return: float
        """
        return self._get_parameter("remainingNotional")

    @remaining_notional.setter
    def remaining_notional(self, value):
        self._set_parameter("remainingNotional", value)

    @property
    def start_date(self):
        """
        Start Date of an amortization section/window, or stepped rate
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)
