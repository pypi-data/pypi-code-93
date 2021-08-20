# coding: utf8
# contract_gen 2020-06-03 11:34:39.530921

__all__ = ["FxOptionForwardStart"]

from ...instrument._definition import ObjectDefinition


class FxOptionForwardStart(ObjectDefinition):
    def __init__(
        self, forward_start_date=None, forward_start_tenor=None, strike_percent=None
    ):
        super().__init__()
        self.forward_start_date = forward_start_date
        self.forward_start_tenor = forward_start_tenor
        self.strike_percent = strike_percent

    @property
    def forward_start_date(self):
        """
        Expiry date of the Forward Start option
        :return: str
        """
        return self._get_parameter("forwardStartDate")

    @forward_start_date.setter
    def forward_start_date(self, value):
        self._set_parameter("forwardStartDate", value)

    @property
    def forward_start_tenor(self):
        """
        Tenor of the Forward Start option
        :return: str
        """
        return self._get_parameter("forwardStartTenor")

    @forward_start_tenor.setter
    def forward_start_tenor(self, value):
        self._set_parameter("forwardStartTenor", value)

    @property
    def strike_percent(self):
        """
        Strike Percent of the Forward Start date of the option
        :return: float
        """
        return self._get_parameter("strikePercent")

    @strike_percent.setter
    def strike_percent(self, value):
        self._set_parameter("strikePercent", value)
