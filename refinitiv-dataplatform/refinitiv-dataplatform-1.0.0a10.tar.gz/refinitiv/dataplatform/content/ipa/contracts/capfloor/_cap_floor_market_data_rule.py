# coding: utf8
# contract_gen 2020-06-03 11:34:39.495949

__all__ = ["CapFloorMarketDataRule"]

from ...instrument._definition import ObjectDefinition


class CapFloorMarketDataRule(ObjectDefinition):
    def __init__(
        self,
        counterparty_credit_curve_tag=None,
        discount=None,
        discount_paid=None,
        forward=None,
        self_credit_curve_tag=None,
    ):
        super().__init__()
        self.counterparty_credit_curve_tag = counterparty_credit_curve_tag
        self.discount = discount
        self.discount_paid = discount_paid
        self.forward = forward
        self.self_credit_curve_tag = self_credit_curve_tag

    @property
    def counterparty_credit_curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("counterpartyCreditCurveTag")

    @counterparty_credit_curve_tag.setter
    def counterparty_credit_curve_tag(self, value):
        self._set_parameter("counterpartyCreditCurveTag", value)

    @property
    def discount(self):
        """
        :return: str
        """
        return self._get_parameter("discount")

    @discount.setter
    def discount(self, value):
        self._set_parameter("discount", value)

    @property
    def discount_paid(self):
        """
        :return: str
        """
        return self._get_parameter("discountPaid")

    @discount_paid.setter
    def discount_paid(self, value):
        self._set_parameter("discountPaid", value)

    @property
    def forward(self):
        """
        :return: str
        """
        return self._get_parameter("forward")

    @forward.setter
    def forward(self, value):
        self._set_parameter("forward", value)

    @property
    def self_credit_curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("selfCreditCurveTag")

    @self_credit_curve_tag.setter
    def self_credit_curve_tag(self, value):
        self._set_parameter("selfCreditCurveTag", value)
