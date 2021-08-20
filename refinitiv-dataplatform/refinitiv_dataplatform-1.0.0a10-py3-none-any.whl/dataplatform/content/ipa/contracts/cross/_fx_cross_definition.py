# coding: utf8
# contract_gen 2020-05-18 08:30:59.277856


__all__ = ["Definition"]

from ...instrument.instrument_definition import InstrumentDefinition
from ...enum_types.fx_cross_type import FxCrossType
from ._fx_cross_leg_definition import LegDefinition


class Definition(InstrumentDefinition):
    def __init__(
        self,
        *,
        instrument_tag=None,
        fx_cross_code=None,
        fx_cross_type=None,
        traded_cross_rate=None,
        traded_swap_points=None,
        reference_spot_rate=None,
        reference_swap_points=None,
        ndf_fixing_settlement_ccy=None,
        legs=None,
    ):
        super().__init__()
        self.instrument_tag = instrument_tag
        self.fx_cross_code = fx_cross_code
        self.fx_cross_type = fx_cross_type
        self.traded_cross_rate = traded_cross_rate
        self.traded_swap_points = traded_swap_points
        self.reference_spot_rate = reference_spot_rate
        self.reference_swap_points = reference_swap_points
        self.ndf_fixing_settlement_ccy = ndf_fixing_settlement_ccy
        self.legs = legs

    @classmethod
    def get_instrument_type(cls):
        return "FxCross"

    @property
    def fx_cross_type(self):
        """
        The type of the Fx Cross instrument :  'FxSpot', 'FxForward', 'FxNonDeliverableForward', 'FxSwap', 'MultiLeg' or 'FxForwardForward'.
        Mandatory.
        :return: enum FxCrossType
        """
        return self._get_enum_parameter(FxCrossType, "fxCrossType")

    @fx_cross_type.setter
    def fx_cross_type(self, value):
        self._set_enum_parameter(FxCrossType, "fxCrossType", value)

    @property
    def legs(self):
        """
        Extra parameters to describe further the contract.
        1 leg is mandatory for Forwards and NDFs contracts.
        2 legs are required for Swaps, and FwdFwdSwaps contracts.
        Optional for Spot contracts.
        :return: list FxCrossLegDefinition
        """
        return self._get_list_parameter(LegDefinition, "legs")

    @legs.setter
    def legs(self, value):
        self._set_list_parameter(LegDefinition, "legs", value)

    @property
    def fx_cross_code(self):
        """
        The ISO code of the cross currency (e.g. 'EURCHF').
        Mandatory.
        :return: str
        """
        return self._get_parameter("fxCrossCode")

    @fx_cross_code.setter
    def fx_cross_code(self, value):
        self._set_parameter("fxCrossCode", value)

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output results to the instrument definition.
        Only alphabetic, numeric and '- _.#=@' characters are supported.
        Optional.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        self._set_parameter("instrumentTag", value)

    @property
    def ndf_fixing_settlement_ccy(self):
        """
        In case of a NDF contract, the ISO code of the settlement currency (e.g. 'EUR' ).
        Optional.
        :return: str
        """
        return self._get_parameter("ndfFixingSettlementCcy")

    @ndf_fixing_settlement_ccy.setter
    def ndf_fixing_settlement_ccy(self, value):
        self._set_parameter("ndfFixingSettlementCcy", value)

    @property
    def reference_spot_rate(self):
        """
        Contractual Spot Rate the counterparties agreed.
        It is used to compute the TradedCrossRate as 'ReferenceSpotRate + TradedSwapPoints / FxSwapPointScalingFactor'.
        In the case of a "FxSwap" contract, it is also used to compute  nearLeg.ContraAmount from nearLeg.DealAmount as  'nearLeg.ContraAmount = nearLeg.DealAmount *  (ReferenceSpotRate / FxCrossScalingFactor)'.
        Optional. Default value is null. In that case TradedCrossRate and Leg ContraAmount may not be computed.
        :return: float
        """
        return self._get_parameter("referenceSpotRate")

    @reference_spot_rate.setter
    def reference_spot_rate(self, value):
        self._set_parameter("referenceSpotRate", value)

    @property
    def traded_cross_rate(self):
        """
        The contractual exchange rate agreed by the two counterparties.
        It is used to compute the ContraAmount if the amount is not filled.
        In the case of a 'FxForward' and 'FxNonDeliverableForward' contract : ContraAmount is computed as 'DealAmount x TradedCrossRate / FxCrossScalingFactor'.
        In the case of a 'FxSwap' contract : farLeg.ContraAmount is computed as 'nearLeg.DealAmount x TradedCrossRate / FxCrossScalingFactor'.
        Optional. Default value is null. It emans that if both ContraAmount and TradedCrossRate are sot set, market value cannot be computed.
        :return: float
        """
        return self._get_parameter("tradedCrossRate")

    @traded_cross_rate.setter
    def traded_cross_rate(self, value):
        self._set_parameter("tradedCrossRate", value)

    @property
    def traded_swap_points(self):
        """
        Contractual forward points agreed by the two counterparties.
        It is used to compute the TradedCrossRate as 'ReferenceSpotRate + TradedSwapPoints / FxSwapPointScalingFactor'.
        Optional. Default value is null. In that case TradedCrossRate and Leg ContraAmount may not be computed.
        :return: float
        """
        return self._get_parameter("tradedSwapPoints")

    @traded_swap_points.setter
    def traded_swap_points(self, value):
        self._set_parameter("tradedSwapPoints", value)

    @property
    def reference_swap_points(self):
        """
        This is the contractual swap points the counterparties agreed to use to calculate the outright, in case of a Forward/Forward contract.
        :return: float
        """
        return self._get_parameter("referenceSwapPoints")

    @reference_swap_points.setter
    def reference_swap_points(self, value):
        self._set_parameter("referenceSwapPoints", value)
