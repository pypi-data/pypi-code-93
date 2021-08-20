# coding: utf8


__all__ = [
    "get_bond_analytics",
    "get_option_analytics",
    "get_swap_analytics",
    "get_cds_analytics",
    "get_cross_analytics",
    "get_repo_analytics",
    "get_capfloor_analytics",
    "get_swaption_analytics",
    "get_term_deposit_analytics",
    "get_surface",
    "get_curve",
]

from .contracts._financial_contracts import FinancialContracts
from .surface._surfaces_class import Surfaces
from .curve._curves_class import Curves


def get_instrument_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
    on_response=None,
    closure=None,
    session=None,
):
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    _fin = FinancialContracts(session=session, on_response=on_response)
    result = _fin.get_instrument_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
        closure=closure,
    )
    ContentFactory._last_result = result
    if result.is_success and result.data and result.data.df is not None:
        return result.data.df
    else:
        ContentFactory._last_error_status = result.status
        return None


def get_bond_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request to price a Bond contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Bond Futures you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> df = rdp.get_bond_analytics(
    ...    universe=[
    ...        "US1YT=RR",
    ...        "US5YT=RR",
    ...        "US10YT=RR"
    ...    ],
    ...    fields=[
    ...        "InstrumentCode",
    ...        "MarketDataDate",
    ...        "YieldPercent",
    ...        "GovernmentSpreadBp",
    ...        "GovCountrySpreadBp",
    ...        "RatingSpreadBp",
    ...        "SectorRatingSpreadBp",
    ...        "EdsfSpreadBp",
    ...        "IssuerSpreadBp"
    ...    ],
    ...    calculation_params=ipa.bond.CalculationParams(
    ...        valuation_date="2019-07-05",
    ...        price_side=ipa.enum_types.PriceSide.BID
    ...    )
    ...)
    """
    result = FinancialContracts.get_bond_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    ContentFactory._last_result = result
    if result.is_success and result.data and result.data.df is not None:
        return result.data.df
    else:
        ContentFactory._last_error_status = result.status
        return None


def get_option_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for an Option contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Option you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> df = rdp.get_option_analytics(
    ...     universe=rdp.ipa.option.Definition(
    ...         instrument_code="FCHI560000L1.p",
    ...         underlying_type=ipa.financial_contracts.option.UnderlyingType.ETI
    ...     ),
    ...     outputs=[
    ...         "Data",
    ...         "Headers"
    ...     ],
    ...     fields=[
    ...         "MarketValueInDealCcy",
    ...         "DeltaPercent",
    ...         "GammaPercent",
    ...         "RhoPercent",
    ...         "ThetaPercent",
    ...         "VegaPercent"
    ...     ]
    ... )
    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    result = FinancialContracts.get_option_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )
    ContentFactory._last_result = result
    if result.is_success and result.data and result.data.df is not None:
        return result.data.df
    else:
        ContentFactory._last_error_status = result.status
        return None


def get_swap_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to price an Interest Rate Swap contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of IR Swap you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> from refinitiv.dataplatform.content.ipa import AmortizationItem
    >>> df = rdp.get_swap_analytics(
    ...     universe=ipa.swap.Definition(
    ...         instrument_tag="user-defined GBP IRS",
    ...         start_date="2019-05-21T00:00:00Z",
    ...         tenor="10Y",
    ...         legs=[
    ...             ipa.swap.LegDefinition(
    ...                 direction=Direction.PAID,
    ...                 notional_amount="10000000",
    ...                 notional_ccy="GBP",
    ...                 interest_type=InterestType.FIXED,
    ...                 interest_payment_frequency=Frequency.ANNUAL,
    ...                 interest_calculation_method=DayCountBasis.DCB_30_360,
    ...                 payment_business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
    ...                 payment_roll_convention=DateRollingConvention.SAME,
    ...                 payment_business_days="UKG",
    ...                 amortization_schedule=[
    ...                     AmortizationItem(
    ...                         remaining_notional=200000,
    ...                         amortization_frequency=AmortizationFrequency.EVERY_COUPON,
    ...                         amortization_type=AmortizationType.LINEAR
    ...                     )
    ...                 ]
    ...             ),
    ...             ipa.swap.LegDefinition(
    ...                 direction=Direction.RECEIVED,
    ...                 notional_amount="10000000",
    ...                 notional_ccy="GBP",
    ...                 interest_type=InterestType.FLOAT,
    ...                 interest_payment_frequency=Frequency.SEMI_ANNUAL,
    ...                 index_reset_frequency=Frequency.SEMI_ANNUAL,
    ...                 interest_calculation_method=DayCountBasis.DCB_ACTUAL_360,
    ...                 payment_business_day_convention=BusinessDayConvention.MODIFIED_FOLLOWING,
    ...                 payment_roll_convention=DateRollingConvention.SAME,
    ...                 payment_business_days="UKG",
    ...                 spread_bp=20,
    ...                 index_name="LIBOR",
    ...                 index_tenor="6M",
    ...                 index_reset_type=IndexResetType.IN_ADVANCE,
    ...                 amortization_schedule=[
    ...                     AmortizationItem(
    ...                         remaining_notional=200000,
    ...                         amortization_frequency=AmortizationFrequency.EVERY2ND_COUPON,
    ...                         amortization_type=AmortizationType.LINEAR
    ...                     )
    ...                 ]
    ...             )
    ...         ]
    ...     ),
    ...     calculation_params=ipa.swap.CalculationParams(discounting_tenor="ON"),
    ...     fields=[
    ...         "InstrumentTag",
    ...         "InstrumentDescription",
    ...         "FixedRate",
    ...         "MarketValueInDealCcy",
    ...         "PV01Bp",
    ...         "DiscountCurveName",
    ...         "ForwardCurveName",
    ...         "CashFlowDatesArray",
    ...         "CashFlowTotalAmountsInDealCcyArray",
    ...         "CashFlowDiscountFactorsArray",
    ...         "CashFlowResidualAmountsInDealCcyArray",
    ...         "ErrorMessage"
    ...     ],
    ...     outputs=[
    ...         "Data",
    ...         "Headers"
    ...     ]
    ... )
    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    result = FinancialContracts.get_swap_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_cds_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to price a Credit Default Swap (CDS) contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of CDS you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> from refinitiv.dataplatform.content.ipa import AmortizationItem
    >>> df = rdp.get_cds_analytics(
    ...    universe=rdp.ipa.cds.Definition(
    ...        instrument_tag="Cds1_InstrumentCode",
    ...        instrument_code="BNPP5YEUAM=R",
    ...        cds_convention=rdp.ipa.enum_types.CdsConvention.ISDA,
    ...        trade_date="2019-05-21T00:00:00Z",
    ...        step_in_date="2019-05-22T00:00:00Z",
    ...        start_date="2019-05-20T00:00:00Z",
    ...        end_date_moving_convention=rdp.ipa.enum_types.BusinessDayConvention.NO_MOVING,
    ...        adjust_to_isda_end_date=True,
    ...    ),
    ...    calculation_params=rdp.ipa.cds.CalculationParams(
    ...        market_data_date="2020-01-01"
    ...    ),
    ...    outputs=[
    ...        "Data",
    ...        "Headers"
    ...    ],
    ...    fields=[
    ...        "InstrumentTag",
    ...        "ValuationDate",
    ...        "InstrumentDescription",
    ...        "StartDate",
    ...        "EndDate",
    ...        "SettlementDate",
    ...        "UpfrontAmountInDealCcy",
    ...        "CashAmountInDealCcy",
    ...        "AccruedAmountInDealCcy",
    ...        "AccruedBeginDate",
    ...        "NextCouponDate",
    ...        "UpfrontPercent",
    ...        "ConventionalSpreadBp",
    ...        "ParSpreadBp",
    ...        "AccruedDays",
    ...        "ErrorCode",
    ...        "ErrorMessage"
    ...    ]
    ...)
    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    result = FinancialContracts.get_cds_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_cross_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to price a FX Cross contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of FX Cross contract you want to price.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> from refinitiv.dataplatform.content.ipa import AmortizationItem
    >>> df = rdp.get_cross_analytics(
    ...    universe=[
    ...        ipa.cross.Definition(
    ...            fx_cross_type=ipa.enum_types.FxCrossType.FX_NON_DELIVERABLE_FORWARD,
    ...            fx_cross_code="USDINR",
    ...            legs=[
    ...                ipa.cross.LegDefinition(
    ...                    deal_amount=1000000,
    ...                    contra_amount=65762500,
    ...                    deal_ccy_buy_sell=ipa.enum_types.BuySell.BUY,
    ...                    tenor="4Y"
    ...                )
    ...            ],
    ...        ),
    ...    ],
    ...    calculation_params=ipa.cross.CalculationParams(
    ...        valuation_date="2017-11-15T00:00:00Z"
    ...    ),
    ...    fields=[
    ...        "ValuationDate",
    ...        "InstrumentDescription",
    ...        "EndDate",
    ...        "FxSwapsCcy1Ccy2",
    ...        "MarketValueInReportCcy",
    ...        "DeltaAmountInReportCcy",
    ...        "RhoContraCcyAmountInReportCcy",
    ...        "RhoDealCcyAmountInReportCcy"
    ...    ],
    ...    outputs=[
    ...        "Data",
    ...        "Headers"
    ...    ]
    ...)
    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    result = FinancialContracts.get_cross_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_repo_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Repo contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Repo definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> df = rdp.get_repo_analytics(
    ...     universe=rdp.ipa.repo.Definition(
    ...         start_date="2019-11-27",
    ...         tenor="1M",
    ...         underlying_instruments=[
    ...             rdp.ipa.repo.UnderlyingContract(
    ...                 instrument_type="Bond",
    ...                 instrument_definition=ipa.bond.Definition(
    ...                     instrument_code="US191450264="
    ...                 )
    ...             )
    ...         ]
    ...     ),
    ...     calculation_params=rdp.ipa.repo.CalculationParams(
    ...         market_data_date="2019-11-25"
    ...     )
    ... )
    """
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    result = FinancialContracts.get_repo_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_capfloor_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Cap Floor contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Cap Floor definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> from refinitiv.dataplatform.content.ipa import AmortizationItem
    >>> df = rdp.get_capfloor_analytics(
     ...   universe=rdp.ipa.capfloor.Definition(
     ...       notional_ccy="EUR",
     ...       start_date="2019-02-11",
     ...       amortization_schedule=[
     ...           AmortizationItem(
     ...               start_date="2021-02-11",
     ...               end_date="2022-02-11",
     ...               amount=100000,
     ...               amortization_type="Schedule"
     ...           ),
     ...           AmortizationItem(
     ...               start_date="2022-02-11",
     ...               end_date="2023-02-11",
     ...               amount=-100000,
     ...               amortization_type="Schedule"
     ...           ),
     ...       ],
     ...       tenor="5Y",
     ...       buy_sell="Sell",
     ...       notional_amount=10000000,
     ...       interest_payment_frequency="Monthly",
     ...       cap_strike_percent=1
     ...   ),
     ...   calculation_params=rdp.ipa.capfloor.CalculationParams(
     ...       skip_first_cap_floorlet=True,
     ...       valuation_date="2020-02-07"
     ...   ),
     ...   fields=[
     ...       "InstrumentTag",
     ...       "InstrumentDescription",
     ...       "FixedRate",
     ...       "MarketValueInDealCcy",
     ...       "MarketValueInReportCcy",
     ...       "ErrorMessage"
     ...   ],
     ...   outputs=[
     ...       "Data",
     ...       "Headers"
     ...   ]
     ...)
    """
    result = FinancialContracts.get_capfloor_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_swaption_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Swaption contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Swaption definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> from refinitiv.dataplatform.content.ipa.contracts.swap import Definition as SwapDefinition
    >>> from refinitiv.dataplatform.content.ipa.contracts.swaption import *
    >>> df = rdp.get_swaption_analytics(
    ...    universe=ipa.swaption.Definition(
    ...        instrument_tag="BermudanEURswaption",
    ...        settlement_type=SwaptionSettlementType.CASH,
    ...        tenor="7Y",
    ...        strike_percent=2.75,
    ...        buy_sell=BuySell.BUY,
    ...        call_put=CallPut.CALL,
    ...        exercise_style=ExerciseStyle.BERM,
    ...        bermudan_swaption_definition=BermudanSwaptionDefinition(
    ...            exercise_schedule_type=ExerciseScheduleType.FLOAT_LEG,
    ...            notification_days=0
    ...        ),
    ...        underlying_definition=SwapDefinition(
    ...            tenor="3Y",
    ...            template="EUR_AB6E"
    ...        )
    ...    ),
    ...    calculation_params=ipa.swaption.CalculationParams(valuation_date="2020-04-24", nb_iterations=80),
    ...    outputs=[
    ...        "Data",
    ...        "Headers",
    ...        "MarketData"
    ...    ]
    ...)
    """
    result = FinancialContracts.get_swaption_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_term_deposit_analytics(
    universe,
    fields=None,
    calculation_params=None,
    outputs=None,
):
    """
    This function describes the properties that you can use a request
    to get the results for a Term Deposits contract.

    Parameters
    ----------
    universe: str, list, object
        contains the list of Term Deposits definitions.
    fields: list, optional
        contains the list of Analytics that the quantitative analytic service will compute.
    calculation_params: object, optional
        contains the properties that may be used to control the calculation.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> from refinitiv.dataplatform.content.ipa.enum_types import *
    >>> from refinitiv.dataplatform.content.ipa.contracts.swap import Definition as SwapDefinition
    >>> from refinitiv.dataplatform.content.ipa.contracts.swaption import *
    >>> df = rdp.get_term_deposit_analytics(
    ...     universe=ipa.term_deposit.Definition(
    ...         instrument_tag="AED_AM1A",
    ...         tenor="5Y",
    ...         notional_ccy="GBP"
    ...     ),
    ...     calculation_params=ipa.term_deposit.CalculationParams(valuation_date="2018-01-10T00:00:00Z"),
    ...     fields=[
    ...         "InstrumentTag",
    ...         "InstrumentDescription",
    ...         "FixedRate",
    ...         "MarketValueInDealCcy",
    ...         "MarketValueInReportCcy",
    ...         "ErrorMessage"
    ...     ],
    ...     outputs=[
    ...         "Data",
    ...         "Headers"
    ...     ]
    ... )
    """
    result = FinancialContracts.get_term_deposit_analytics(
        universe=universe,
        fields=fields,
        calculation_params=calculation_params,
        outputs=outputs,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = {
            "error_code": result.error_code,
            "error_message": result.error_message,
        }
        retval = None

    ContentFactory._last_result = result

    return retval


def get_surface(
    universe,
    outputs=None,
):
    """
    The Volatility Surfaces API provides you with an easy way to:

    - Compute the volatility level for a specific expiry and strike.
    - Derive volatility slices based on specific strikes or expiries.
    - Analyze the volatility surface of an asset.

    To compute a volatility surface, all you need to do is define the underlying instrument.
    For more advanced usage, you can easily apply different calculation parameters or
    adjust the surface layout to match your needs.

    Parameters
    ----------
    universe: list, object
        contains the list of Surface definitions.
    outputs: list, optional
        these values will be distributed depending on the available input data and the type of volatility.

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> df = ipa.get_surface(
    ...    universe=[
    ...        ipa.surface.eti.Definition(
    ...            tag="1",
    ...            instrument_code="BNPP.PA@RIC",
    ...            calculation_params=ipa.surface.eti.CalculationParams(
    ...                price_side=ipa.enum_types.PriceSide.MID,
    ...                volatility_model=ipa.enum_types.VolatilityModel.SVI,
    ...                x_axis=ipa.enum_types.Axis.DATE,
    ...                y_axis=ipa.enum_types.Axis.STRIKE,
    ...            ),
    ...            layout=ipa.surface.SurfaceOutput(
    ...                format=ipa.enum_types.Format.MATRIX,
    ...                y_point_count=10
    ...            ),
    ...        ),
    ...        ipa.surface.eti.Definition(
    ...            tag="222",
    ...            instrument_code="BNPP.PA@RIC",
    ...            calculation_params=ipa.surface.eti.CalculationParams(
    ...                price_side=ipa.enum_types.PriceSide.MID,
    ...                volatility_model=ipa.enum_types.VolatilityModel.SVI,
    ...                x_axis=ipa.enum_types.Axis.DATE,
    ...                y_axis=ipa.enum_types.Axis.STRIKE,
    ...            ),
    ...            layout=ipa.surface.SurfaceOutput(
    ...                format=ipa.enum_types.Format.MATRIX,
    ...                y_point_count=10
    ...            ),
    ...        )
    ...    ]
    ...)
    """
    result = Surfaces.get_surface(
        universe=universe,
        outputs=outputs,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval


def get_curve(
    universe,
    outputs=None,
):
    """
    Parameters
    ----------
    universe: str, list, object
        contains the list of Curve definitions.
    outputs: list, optional
        contains the sections that will be returned by the API

    Returns
    -------
    Dataframe or None
        Dataframe if successful, None otherwise.

    Examples
    --------
    >>> import refinitiv.dataplatform as rdp
    >>> from refinitiv.dataplatform.content import ipa
    >>> response = ipa.curve.Curves().get_curve(
    ...    universe=[
    ...        ipa.curve.ForwardCurve(
    ...            curve_definition=ipa.curve.SwapZcCurveDefinition(
    ...                currency="EUR",
    ...                index_name="EURIBOR",
    ...                discounting_tenor="OIS"
    ...            ),
    ...            forward_curve_definitions=[
    ...                ipa.curve.ForwardCurveDefinition(
    ...                    index_tenor="3M",
    ...                    forward_curve_tag="ForwardTag",
    ...                    forward_start_date="2021-02-01",
    ...                    forward_curve_tenors=[
    ...                        "0D",
    ...                        "1D",
    ...                        "2D",
    ...                        "3M",
    ...                        "6M",
    ...                        "9M",
    ...                        "1Y",
    ...                        "2Y",
    ...                        "3Y",
    ...                        "4Y",
    ...                        "5Y",
    ...                        "6Y",
    ...                        "7Y",
    ...                        "8Y",
    ...                        "9Y",
    ...                        "10Y",
    ...                        "15Y",
    ...                        "20Y",
    ...                        "25Y"
    ...                    ]
    ...                )
    ...            ]
    ...        )
    ...    ],
    ...    outputs=[
    ...        "Constituents"
    ...    ]
    ...)
    """
    result = Curves.get_curve(
        universe=universe,
        outputs=outputs,
    )
    from refinitiv.dataplatform.factory.content_factory import ContentFactory

    if result.is_success and result.data and result.data.df is not None:
        retval = result.data.df
    else:
        ContentFactory._last_error_status = result.status
        retval = None

    ContentFactory._last_result = result

    return retval
