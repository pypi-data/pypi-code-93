# coding: utf8
# contract_gen 2020-06-16 10:12:54.863244

__all__ = ["Definition"]

from .._base_definition import BaseDefinition
from ._eti_calculation_params import CalculationParams
from ...enum_types.underlying_type import UnderlyingType
from ...instrument._definition import ObjectDefinition


class EtiUnderlyingDefinition(ObjectDefinition):
    def __init__(
        self,
        instrument_code=None,
        clean_instrument_code=None,
        exchange=None,
        is_future_underlying=None,
    ):
        super().__init__()
        self.instrument_code = instrument_code
        self.clean_instrument_code = clean_instrument_code
        self.exchange = exchange
        self.is_future_underlying = is_future_underlying

    @property
    def clean_instrument_code(self):
        """
        :return: str
        """
        return self._get_parameter("cleanInstrumentCode")

    @clean_instrument_code.setter
    def clean_instrument_code(self, value):
        self._set_parameter("cleanInstrumentCode", value)

    @property
    def exchange(self):
        """
        Specifies the exchange to be used to retrieve the underlying data.
        :return: str
        """
        return self._get_parameter("exchange")

    @exchange.setter
    def exchange(self, value):
        self._set_parameter("exchange", value)

    @property
    def instrument_code(self):
        """
        The code (RIC for equities and indices and RICROOT for Futures.) that represents the instrument.
        The format for equities and indices is xxx@RIC (Example: VOD.L@RIC)
        The format for Futures is xx@RICROOT (Example: CL@RICROOT)
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def is_future_underlying(self):
        """
        :return: bool
        """
        return self._get_parameter("isFutureUnderlying")

    @is_future_underlying.setter
    def is_future_underlying(self, value):
        self._set_parameter("isFutureUnderlying", value)


class Definition(BaseDefinition):
    def __init__(
        self,
        *,
        instrument_code=None,
        clean_instrument_code=None,
        exchange=None,
        is_future_underlying=None,
        tag,
        layout,
        calculation_params,
    ):
        super().__init__(tag=tag, layout=layout, underlying_type=UnderlyingType.ETI)
        self.calculation_params = calculation_params
        self.underlying_definition = EtiUnderlyingDefinition(
            instrument_code=instrument_code,
            clean_instrument_code=clean_instrument_code,
            exchange=exchange,
            is_future_underlying=is_future_underlying,
        )

    @property
    def calculation_params(self):
        """
        The section that contains the properties that define how the volatility surface is generated
        :return: object EtiSurfaceParameters
        """
        return self._get_object_parameter(CalculationParams, "surfaceParameters")

    @calculation_params.setter
    def calculation_params(self, value):
        self._set_object_parameter(CalculationParams, "surfaceParameters", value)

    @property
    def underlying_definition(self):
        """
        The section that contains the properties that define the underlying instrument
        :return: object EtiSurfaceDefinition
        """
        return self._get_object_parameter(
            EtiUnderlyingDefinition, "underlyingDefinition"
        )

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(
            EtiUnderlyingDefinition, "underlyingDefinition", value
        )
