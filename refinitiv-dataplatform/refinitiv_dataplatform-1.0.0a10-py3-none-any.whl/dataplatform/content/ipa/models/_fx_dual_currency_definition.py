# coding: utf8
# contract_gen 2020-05-19 11:24:17.149212

__all__ = ["FxDualCurrencyDefinition"]

from ..instrument._definition import ObjectDefinition


class FxDualCurrencyDefinition(ObjectDefinition):
    def __init__(self, deposit_start_date=None, margin_percent=None):
        super().__init__()
        self.deposit_start_date = deposit_start_date
        self.margin_percent = margin_percent

    @property
    def deposit_start_date(self):
        """
        Deposit Start Date for the DualCurrencyDeposit option
        :return: str
        """
        return self._get_parameter("depositStartDate")

    @deposit_start_date.setter
    def deposit_start_date(self, value):
        self._set_parameter("depositStartDate", value)

    @property
    def margin_percent(self):
        """
        Margin for the DualCurrencyDeposit option
        :return: float
        """
        return self._get_parameter("marginPercent")

    @margin_percent.setter
    def margin_percent(self, value):
        self._set_parameter("marginPercent", value)
