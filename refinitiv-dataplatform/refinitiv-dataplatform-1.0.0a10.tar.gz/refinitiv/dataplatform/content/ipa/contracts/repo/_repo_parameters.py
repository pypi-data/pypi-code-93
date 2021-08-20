# coding: utf8
# contract_gen 2020-05-19 11:08:13.654235

__all__ = ["RepoParameters"]

from ...instrument._definition import ObjectDefinition


class RepoParameters(ObjectDefinition):
    def __init__(
        self,
        coupon_paid_at_horizon=None,
        haircut_rate_percent=None,
        initial_margin_percent=None,
    ):
        super().__init__()
        self.coupon_paid_at_horizon = coupon_paid_at_horizon
        self.haircut_rate_percent = haircut_rate_percent
        self.initial_margin_percent = initial_margin_percent

    @property
    def coupon_paid_at_horizon(self):
        """
        Flag that defines wether couponis paid at horizon.  This has no impact on pricing.
        :return: bool
        """
        return self._get_parameter("couponPaidAtHorizon")

    @coupon_paid_at_horizon.setter
    def coupon_paid_at_horizon(self, value):
        self._set_parameter("couponPaidAtHorizon", value)

    @property
    def haircut_rate_percent(self):
        """
        Repo contract's haircut par in percentage, for computing the transaction's Margin. InitialMargin = 1/ 1-Haircut.
        Optional. Either HairCut or Initial Marging field can be bet.
        :return: float
        """
        return self._get_parameter("haircutRatePercent")

    @haircut_rate_percent.setter
    def haircut_rate_percent(self, value):
        self._set_parameter("haircutRatePercent", value)

    @property
    def initial_margin_percent(self):
        """
        Repo contract's initial margin in percentage.
        :return: float
        """
        return self._get_parameter("initialMarginPercent")

    @initial_margin_percent.setter
    def initial_margin_percent(self, value):
        self._set_parameter("initialMarginPercent", value)
