# coding: utf8


__all__ = ["CalculationParams"]

from refinitiv.dataplatform.content.ipa.instrument import InstrumentCalculationParams
from refinitiv.dataplatform.content.ipa.enum_types import BenchmarkYieldSelectionMode
from refinitiv.dataplatform.content.ipa.enum_types import PriceSide
from refinitiv.dataplatform.content.ipa.enum_types import (
    ProjectedIndexCalculationMethod,
)
from refinitiv.dataplatform.content.ipa.enum_types import RedemptionDateType
from refinitiv.dataplatform.content.ipa.enum_types import YieldType
from refinitiv.dataplatform.content.ipa.enum_types import QuoteFallbackLogic


class CalculationParams(InstrumentCalculationParams):
    """
    Bond pricing parameters
    """

    class Params(InstrumentCalculationParams.Params):
        def __init__(self):
            super().__init__()

        def with_valuation_date(self, value):
            self._with_key_parameter("ValuationDate", value)
            return self

        def with_market_data_date(self, value):
            self._with_key_parameter("MarketDataDate", value)
            return self

        def with_settlement_convention(self, value):
            self._with_key_parameter("SettlementConvention", value)
            return self

        def with_report_ccy(self, value):
            self._with_key_parameter("ReportCcy", value)
            return self

        def with_price_side(self, value):
            self._with_key_parameter("PriceSide", value)
            return self

        def with_redemption_date_type(self, value):
            self._with_key_parameter("RedemptionDateType", value)
            return self

        def with_redemption_date(self, value):
            self._with_key_parameter("RedemptionDate", value)
            return self

        def with_yield_type(self, value):
            self._with_key_parameter("YieldType", value)
            return self

        def with_tax_on_income_gain_percent(self, value):
            self._with_key_parameter("TaxOnIncomeGainPercent", value)
            return self

        def with_tax_on_capital_gain_percent(self, value):
            self._with_key_parameter("TaxOnCapitalGainPercent", value)
            return self

        def with_tax_on_yield_percent(self, value):
            self._with_key_parameter("TaxOnYieldPercent", value)
            return self

        def with_tax_on_price_percent(self, value):
            self._with_key_parameter("TaxOnPricePercent", value)
            return self

        def with_concession_fee(self, value):
            self._with_key_parameter("ConcessionFee", value)
            return self

        def with_benchmark_yield_selection_mode(self, value):
            self._with_key_parameter("BenchmarkYieldSelectionMode", value)
            return self

        def with_price(self, value):
            self._with_key_parameter("Price", value)
            return self

        def with_yield_percent(self, value):
            self._with_key_parameter("YieldPercent", value)
            return self

        def with_clean_price(self, value):
            self._with_key_parameter("CleanPrice", value)
            return self

        def with_dirty_price(self, value):
            self._with_key_parameter("DirtyPrice", value)
            return self

        def with_net_price(self, value):
            self._with_key_parameter("NetPrice", value)
            return self

        def with_cash_amount(self, value):
            self._with_key_parameter("CashAmount", value)
            return self

        def with_discount_margin_bp(self, value):
            self._with_key_parameter("DiscountMarginBp", value)
            return self

        def with_simple_margin_bp(self, value):
            self._with_key_parameter("SimpleMarginBp", value)
            return self

        def with_neutral_yield_percent(self, value):
            self._with_key_parameter("NeutralYieldPercent", value)
            return self

        def with_current_yield_percent(self, value):
            self._with_key_parameter("CurrentYieldPercent", value)
            return self

        def with_strip_yield_percent(self, value):
            self._with_key_parameter("StripYieldPercent", value)
            return self

        def with_discount_percent(self, value):
            self._with_key_parameter("DiscountPercent", value)
            return self

        def with_z_spread_bp(self, value):
            self._with_key_parameter("ZSpreadBp", value)
            return self

        def with_asset_swap_spread_bp(self, value):
            self._with_key_parameter("AssetSwapSpreadBp", value)
            return self

        def with_option_adjusted_spread_bp(self, value):
            self._with_key_parameter("OptionAdjustedSpreadBp", value)
            return self

        def with_swap_spread_bp(self, value):
            self._with_key_parameter("SwapSpreadBp", value)
            return self

        def with_swap_yield_percent(self, value):
            self._with_key_parameter("SwapYieldPercent", value)
            return self

        def with_government_spread_bp(self, value):
            self._with_key_parameter("GovernmentSpreadBp", value)
            return self

        def with_government_benchmark_curve_yield_percent(self, value):
            self._with_key_parameter("GovernmentBenchmarkCurveYieldPercent", value)
            return self

        def with_gov_country_spread_bp(self, value):
            self._with_key_parameter("GovCountrySpreadBp", value)
            return self

        def with_gov_country_benchmark_curve_yield_percent(self, value):
            self._with_key_parameter("GovCountryBenchmarkCurveYieldPercent", value)
            return self

        def with_rating_spread_bp(self, value):
            self._with_key_parameter("RatingSpreadBp", value)
            return self

        def with_rating_benchmark_curve_yield_percent(self, value):
            self._with_key_parameter("RatingBenchmarkCurveYieldPercent", value)
            return self

        def with_sector_rating_spread_bp(self, value):
            self._with_key_parameter("SectorRatingSpreadBp", value)
            return self

        def with_sector_rating_benchmark_curve_yield_percent(self, value):
            self._with_key_parameter("SectorRatingBenchmarkCurveYieldPercent", value)
            return self

        def with_edsf_spread_bp(self, value):
            self._with_key_parameter("EdsfSpreadBp", value)
            return self

        def with_edsf_benchmark_curve_yield_percent(self, value):
            self._with_key_parameter("EdsfBenchmarkCurveYieldPercent", value)
            return self

        def with_issuer_spread_bp(self, value):
            self._with_key_parameter("IssuerSpreadBp", value)
            return self

        def with_issuer_benchmark_curve_yield_percent(self, value):
            self._with_key_parameter("IssuerBenchmarkCurveYieldPercent", value)
            return self

        def with_projected_index_percent(self, value):
            self._with_key_parameter("ProjectedIndexPercent", value)
            return self

        def with_ibor_rate_percent(self, value):
            self._with_key_parameter("IborRatePercent", value)
            return self

        def with_ibor_spot_lag(self, value):
            self._with_key_parameter("IborSpotLag", value)
            return self

        def with_market_value_fees_in_deal_ccy(self, value):
            self._with_key_parameter("MarketValueFeesInDealCcy", value)
            return self

        def with_market_value_in_deal_ccy(self, value):
            self._with_key_parameter("MarketValueInDealCcy", value)
            return self

        def with_market_value_in_report_ccy(self, value):
            self._with_key_parameter("MarketValueInReportCcy", value)
            return self

        def with_rounding_parameters(self, value):
            self._with_key_parameter("RoundingParameters", value)
            return self

    #         def with_projected_index_calculation_method(self, value):
    #             self._with_key_parameter("ProjectedIndexCalculationMethod", value)
    #             return self
    #
    #         def with_compute_cash_flow_from_issue_date(self, value):
    #             self._with_key_parameter("ComputeCashFlowFromIssueDate", value)
    #             return self
    #
    #         def with_compute_cash_flow_with_report_ccy(self, value):
    #             self._with_key_parameter("ComputeCashFlowWithReportCcy", value)
    #             return self

    @classmethod
    def from_params(cls, params=None):
        if params and isinstance(params, CalculationParams.Params):
            bond_calculation_params = cls.__new__(cls)
            super(CalculationParams, bond_calculation_params).__init__()
            for (key, value) in params.parameters.items():
                bond_calculation_params._pricing_parameters[key] = value
            return bond_calculation_params

    def __init__(
        self,
        settlement_convention=None,
        price=None,
        yield_percent=None,
        adjusted_yield_percent=None,
        quoted_price=None,
        clean_price=None,
        dirty_price=None,
        adjusted_clean_price=None,
        adjusted_dirty_price=None,
        neutral_yield_percent=None,
        cash_amount=None,
        z_spread_bp=None,
        swap_spread_bp=None,
        swap_benchmark_curve_yield_percent=None,
        government_spread_bp=None,
        government_benchmark_curve_yield_percent=None,
        government_benchmark_curve_price=None,
        gov_country_spread_bp=None,
        gov_country_benchmark_curve_yield_percent=None,
        gov_country_benchmark_curve_price=None,
        edsf_spread_bp=None,
        edsf_benchmark_curve_yield_percent=None,
        rating_spread_bp=None,
        rating_benchmark_curve_yield_percent=None,
        issuer_spread_bp=None,
        issuer_benchmark_curve_yield_percent=None,
        sector_rating_spread_bp=None,
        sector_rating_benchmark_curve_yield_percent=None,
        asset_swap_spread_bp=None,
        option_adjusted_spread_bp=None,
        user_defined_spread_bp=None,
        user_defined_benchmark_yield_percent=None,
        user_defined_benchmark_price=None,
        benchmark_at_issue_price=None,
        benchmark_at_issue_yield_percent=None,
        benchmark_at_issue_spread_bp=None,
        benchmark_at_issue_ric=None,
        efp_benchmark_price=None,
        efp_benchmark_yield_percent=None,
        efp_spread_bp=None,
        efp_benchmark_ric=None,
        benchmark_at_redemption_price=None,
        benchmark_at_redemption_yield_percent=None,
        benchmark_at_redemption_spread_bp=None,
        current_yield_percent=None,
        strip_yield_percent=None,
        discount_percent=None,
        net_price=None,
        discount_margin_bp=None,
        simple_margin_bp=None,
        price_side=None,
        rounding_parameters=None,
        redemption_date_type=None,
        redemption_date=None,
        yield_type=None,
        tax_on_yield_percent=None,
        tax_on_capital_gain_percent=None,
        tax_on_coupon_percent=None,
        tax_on_price_percent=None,
        apply_tax_to_full_pricing=None,
        concession_fee=None,
        benchmark_yield_selection_mode=None,
        market_value_in_deal_ccy=None,
        market_value_in_report_ccy=None,
        projected_index_calculation_method=None,
        initial_margin_percent=None,
        haircut_rate_percent=None,
        clean_future_price=None,
        dirty_future_price=None,
        valuation_date=None,
        interpolate_missing_points=None,
        report_ccy=None,
        market_data_date=None,
        quote_fallback_logic=None,
    ):
        super().__init__()
        """
        :param trade_date: str
        :param benchmark_yield_selection_mode: BenchmarkYieldSelectionMode
        :param fx_price_side: PriceSide
        :param price_side: PriceSide
        :param projected_index_calculation_method: ProjectedIndexCalculationMethod
        :param redemption_date_type: RedemptionDateType
        :param rounding_parameters: BondRoundingParameters
        :param yield_type: YieldType
        :param adjusted_clean_price: float
        :param adjusted_dirty_price: float
        :param adjusted_yield_percent: float
        :param apply_tax_to_full_pricing: bool
        :param asset_swap_spread_bp: float
        :param benchmark_at_issue_price: float
        :param benchmark_at_issue_ric: str
        :param benchmark_at_issue_spread_bp: float
        :param benchmark_at_issue_yield_percent: float
        :param benchmark_at_redemption_price: float
        :param benchmark_at_redemption_spread_bp: float
        :param benchmark_at_redemption_yield_percent: float
        :param cash_amount: float
        :param clean_price: float
        :param concession_fee: float
        :param current_yield_percent: float
        :param dirty_price: float
        :param discount_margin_bp: float
        :param discount_percent: float
        :param edsf_benchmark_curve_yield_percent: float
        :param edsf_spread_bp: float
        :param efp_benchmark_price: float
        :param efp_benchmark_ric: str
        :param efp_benchmark_yield_percent: float
        :param efp_spread_bp: float
        :param gov_country_benchmark_curve_price: float
        :param gov_country_benchmark_curve_yield_percent: float
        :param gov_country_spread_bp: float
        :param government_benchmark_curve_price: float
        :param government_benchmark_curve_yield_percent: float
        :param government_spread_bp: float
        :param issuer_benchmark_curve_yield_percent: float
        :param issuer_spread_bp: float
        :param market_value_in_deal_ccy: float
        :param market_value_in_report_ccy: float
        :param net_price: float
        :param neutral_yield_percent: float
        :param ois_zc_benchmark_curve_yield_percent: float
        :param ois_zc_spread_bp: float
        :param option_adjusted_spread_bp: float
        :param price: float
        :param quoted_price: float
        :param rating_benchmark_curve_yield_percent: float
        :param rating_spread_bp: float
        :param redemption_date: str
        :param sector_rating_benchmark_curve_yield_percent: float
        :param sector_rating_spread_bp: float
        :param settlement_convention: str
        :param simple_margin_bp: float
        :param strip_yield_percent: float
        :param swap_benchmark_curve_yield_percent: float
        :param swap_spread_bp: float
        :param tax_on_capital_gain_percent: float
        :param tax_on_coupon_percent: float
        :param tax_on_price_percent: float
        :param tax_on_yield_percent: float
        :param use_settlement_date_from_quote: bool
        :param user_defined_benchmark_price: float
        :param user_defined_benchmark_yield_percent: float
        :param user_defined_spread_bp: float
        :param valuation_date: str
        :param yield_percent: float
        :param z_spread_bp: float
        """
        self.settlement_convention = settlement_convention
        self.price = price
        self.yield_percent = yield_percent
        self.adjusted_yield_percent = adjusted_yield_percent
        self.quoted_price = quoted_price
        self.clean_price = clean_price
        self.dirty_price = dirty_price
        self.adjusted_clean_price = adjusted_clean_price
        self.adjusted_dirty_price = adjusted_dirty_price
        self.neutral_yield_percent = neutral_yield_percent
        self.cash_amount = cash_amount
        self.z_spread_bp = z_spread_bp
        self.swap_spread_bp = swap_spread_bp
        self.swap_benchmark_curve_yield_percent = swap_benchmark_curve_yield_percent
        self.government_spread_bp = government_spread_bp
        self.government_benchmark_curve_yield_percent = (
            government_benchmark_curve_yield_percent
        )
        self.government_benchmark_curve_price = government_benchmark_curve_price
        self.gov_country_spread_bp = gov_country_spread_bp
        self.gov_country_benchmark_curve_yield_percent = (
            gov_country_benchmark_curve_yield_percent
        )
        self.gov_country_benchmark_curve_price = gov_country_benchmark_curve_price
        self.edsf_spread_bp = edsf_spread_bp
        self.edsf_benchmark_curve_yield_percent = edsf_benchmark_curve_yield_percent
        self.rating_spread_bp = rating_spread_bp
        self.rating_benchmark_curve_yield_percent = rating_benchmark_curve_yield_percent
        self.issuer_spread_bp = issuer_spread_bp
        self.issuer_benchmark_curve_yield_percent = issuer_benchmark_curve_yield_percent
        self.sector_rating_spread_bp = sector_rating_spread_bp
        self.sector_rating_benchmark_curve_yield_percent = (
            sector_rating_benchmark_curve_yield_percent
        )
        self.asset_swap_spread_bp = asset_swap_spread_bp
        self.option_adjusted_spread_bp = option_adjusted_spread_bp
        self.user_defined_spread_bp = user_defined_spread_bp
        self.user_defined_benchmark_yield_percent = user_defined_benchmark_yield_percent
        self.user_defined_benchmark_price = user_defined_benchmark_price
        self.benchmark_at_issue_price = benchmark_at_issue_price
        self.benchmark_at_issue_yield_percent = benchmark_at_issue_yield_percent
        self.benchmark_at_issue_spread_bp = benchmark_at_issue_spread_bp
        self.benchmark_at_issue_ric = benchmark_at_issue_ric
        self.efp_benchmark_price = efp_benchmark_price
        self.efp_benchmark_yield_percent = efp_benchmark_yield_percent
        self.efp_spread_bp = efp_spread_bp
        self.efp_benchmark_ric = efp_benchmark_ric
        self.benchmark_at_redemption_price = benchmark_at_redemption_price
        self.benchmark_at_redemption_yield_percent = (
            benchmark_at_redemption_yield_percent
        )
        self.benchmark_at_redemption_spread_bp = benchmark_at_redemption_spread_bp
        self.current_yield_percent = current_yield_percent
        self.strip_yield_percent = strip_yield_percent
        self.discount_percent = discount_percent
        self.net_price = net_price
        self.discount_margin_bp = discount_margin_bp
        self.simple_margin_bp = simple_margin_bp
        self.price_side = price_side
        self.rounding_parameters = rounding_parameters
        self.redemption_date_type = redemption_date_type
        self.redemption_date = redemption_date
        self.yield_type = yield_type
        self.tax_on_yield_percent = tax_on_yield_percent
        self.tax_on_capital_gain_percent = tax_on_capital_gain_percent
        self.tax_on_coupon_percent = tax_on_coupon_percent
        self.tax_on_price_percent = tax_on_price_percent
        self.apply_tax_to_full_pricing = apply_tax_to_full_pricing
        self.concession_fee = concession_fee
        self.benchmark_yield_selection_mode = benchmark_yield_selection_mode
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.market_value_in_report_ccy = market_value_in_report_ccy
        self.projected_index_calculation_method = projected_index_calculation_method
        self.initial_margin_percent = initial_margin_percent
        self.haircut_rate_percent = haircut_rate_percent
        self.clean_future_price = clean_future_price
        self.dirty_future_price = dirty_future_price
        self.valuation_date = valuation_date
        self.interpolate_missing_points = interpolate_missing_points
        self.report_ccy = report_ccy
        self.market_data_date = market_data_date
        self.quote_fallback_logic = quote_fallback_logic

    ###########################################
    ## PricingParameters properties
    ###########################################
    @property
    def settlement_convention(self):
        """
        Settlement convention for the bond.
        By default the rule is that valuationDate = marketDataDate + settlementConvention.
        Optional. By default use the settlement tenor defined in the bond structure. Only two parameters among
        "settlementConvention", "marketDataDate" and "ValuationDate" can be overriden at the same time.
        :return: string
        """
        return self._get_parameter("settlementConvention")

    @settlement_convention.setter
    def settlement_convention(self, value):
        self._set_parameter("settlementConvention", value)

    @property
    def price(self):
        """
        Price to override and that will be used as pricing analysis input. This price can be the clean price or
        dirty price depending on price type defined in bond structure.
        The currency of the price is the cash flow currency (that can be different to deal currency especially if
        "ComputeCashFlowWithReportCcy" flag has been set to true).
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("price")

    @price.setter
    def price(self, value):
        self._set_parameter("price", value)

    @property
    def yield_percent(self):
        """
        Yield (expressed in percent) to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("yieldPercent")

    @yield_percent.setter
    def yield_percent(self, value):
        self._set_parameter("yieldPercent", value)

    @property
    def adjusted_yield_percent(self):
        """
        Inflation Adjusted Yield (expressed in percent) to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("adjustedYieldPercent")

    @adjusted_yield_percent.setter
    def adjusted_yield_percent(self, value):
        self._set_parameter("adjustedYieldPercent", value)

    @property
    def quoted_price(self):
        """
        Quoted price to override and that will be used as pricing analysis input. Note that a quoted price can be
        a price, a yield, a discount margin, a spread,... depending on quotation type.
        The currency of the quoted price in case the bond is price-quoted or cash-quoted is the deal currency
        (that can be different to cash flow currency especially if "ComputeCashFlowWithReportCcy" flag has
        been set to true).
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("quotePrice")

    @quoted_price.setter
    def quoted_price(self, value):
        self._set_parameter("quotePrice", value)

    @property
    def clean_price(self):
        """
        Clean price to override and that will be used as pricing analysis input.\r\nThe currency of the clean price
        is the cash flow currency (that can be different to deal currency especially if
        "ComputeCashFlowWithReportCcy" flag has been set to true).
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cleanPrice")

    @clean_price.setter
    def clean_price(self, value):
        self._set_parameter("cleanPrice", value)

    @property
    def dirty_price(self):
        """
        Dirty price to override and that will be used as pricing analysis input.
        The currency of the dirty price is the cash flow currency (that can be different to deal currency
        especially if "ComputeCashFlowWithReportCcy" flag has been set to true).
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("dirtyPrice")

    @dirty_price.setter
    def dirty_price(self, value):
        self._set_parameter("dirtyPrice", value)

    @property
    def adjusted_clean_price(self):
        """
        Inflation Adjusted Clean price to override and that will be used as pricing analysis input.
        The currency of the clean price is the cash flow currency (that can be different to deal currency especially
         if "ComputeCashFlowWithReportCcy" flag has been set to true).\r\nOptional. No override is applied by default.
         Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("adjustedCleanPrice")

    @adjusted_clean_price.setter
    def adjusted_clean_price(self, value):
        self._set_parameter("adjustedCleanPrice", value)

    @property
    def adjusted_dirty_price(self):
        """
        Inflation Adjusted Dirty price to override and that will be used as pricing analysis input.
        The currency of the dirty price is the cash flow currency (that can be different to deal currency
        especially if "ComputeCashFlowWithReportCcy" flag has been set to true).
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("adjustedDirtyPrice")

    @adjusted_dirty_price.setter
    def adjusted_dirty_price(self, value):
        self._set_parameter("adjustedDirtyPrice", value)

    @property
    def neutral_yield_percent(self):
        """
        Neutral Yield (expressed in percent) to override and that will be used as pricing analysis input.
        This is available only for floating rate notes.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("neutralYieldPercent")

    @neutral_yield_percent.setter
    def neutral_yield_percent(self, value):
        self._set_parameter("neutralYieldPercent", value)

    @property
    def cash_amount(self):
        """
        Cash amount to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cashAmount")

    @cash_amount.setter
    def cash_amount(self, value):
        self._set_parameter("cashAmount", value)

    @property
    def z_spread_bp(self):
        """
        ZSpread to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("zSpreadBp")

    @z_spread_bp.setter
    def z_spread_bp(self, value):
        self._set_parameter("zSpreadBp", value)

    @property
    def swap_spread_bp(self):
        """
        Spread of swap benchmark to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("swapSpreadBp")

    @swap_spread_bp.setter
    def swap_spread_bp(self, value):
        self._set_parameter("swapSpreadBp", value)

    @property
    def swap_benchmark_curve_yield_percent(self):
        """
        Yield of swap benchmark to override and that will be used to compute swap spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("swapBenchmarkCurveYieldPercent")

    @swap_benchmark_curve_yield_percent.setter
    def swap_benchmark_curve_yield_percent(self, value):
        self._set_parameter("swapBenchmarkCurveYieldPercent", value)

    @property
    def government_spread_bp(self):
        """
        Spread of government benchmark to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("governmentSpreadBp")

    @government_spread_bp.setter
    def government_spread_bp(self, value):
        self._set_parameter("governmentSpreadBp", value)

    @property
    def government_benchmark_curve_yield_percent(self):
        """
        Yield of government benchmark to override and that will be used to compute government spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("governmentBenchmarkCurveYieldPercent")

    @government_benchmark_curve_yield_percent.setter
    def government_benchmark_curve_yield_percent(self, value):
        self._set_parameter("governmentBenchmarkCurveYieldPercent", value)

    @property
    def government_benchmark_curve_price(self):
        """
        Price of government benchmark to override and that will be used to compute user defined spread.
        Optional. No override is applied by default and price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("governmentBenchmarkCurvePrice")

    @government_benchmark_curve_price.setter
    def government_benchmark_curve_price(self, value):
        self._set_parameter("governmentBenchmarkCurvePrice", value)

    @property
    def gov_country_spread_bp(self):
        """
        Spread of government country benchmark to override and that will be used as pricing analysis input to
        compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("govCountrySpreadBp")

    @gov_country_spread_bp.setter
    def gov_country_spread_bp(self, value):
        self._set_parameter("govCountrySpreadBp", value)

    @property
    def gov_country_benchmark_curve_yield_percent(self):
        """
        Yield of government country benchmark to override and that will be used to compute government country spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("govCountryBenchmarkCurveYieldPercent")

    @gov_country_benchmark_curve_yield_percent.setter
    def gov_country_benchmark_curve_yield_percent(self, value):
        self._set_parameter("govCountryBenchmarkCurveYieldPercent", value)

    @property
    def gov_country_benchmark_curve_price(self):
        """
        Price of government country benchmark to override and that will be used to compute user defined spread.
        Optional. No override is applied by default and price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("govCountryBenchmarkCurvePrice")

    @gov_country_benchmark_curve_price.setter
    def gov_country_benchmark_curve_price(self, value):
        self._set_parameter("govCountryBenchmarkCurvePrice", value)

    @property
    def edsf_spread_bp(self):
        """
        Spread of Euro-Dollar future benchmark curve (Edsf) to override and that will be used as pricing analysis
        input to compute the bond price. This spread is computed for USD Bond whose maturity is under 2 Years.
        Optional. No override is applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("edsfSpreadBp")

    @edsf_spread_bp.setter
    def edsf_spread_bp(self, value):
        self._set_parameter("edsfSpreadBp", value)

    @property
    def edsf_benchmark_curve_yield_percent(self):
        """
        Yield of Euro-Dollar future benchmark curve (Edsf) to override and that will be used to compute
        Euro-Dollar (Edsf) spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("edsfBenchmarkCurveYieldPercent")

    @edsf_benchmark_curve_yield_percent.setter
    def edsf_benchmark_curve_yield_percent(self, value):
        self._set_parameter("edsfBenchmarkCurveYieldPercent", value)

    @property
    def rating_spread_bp(self):
        """
        Spread of rating benchmark to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("ratingSpreadBp")

    @rating_spread_bp.setter
    def rating_spread_bp(self, value):
        self._set_parameter("ratingSpreadBp", value)

    @property
    def rating_benchmark_curve_yield_percent(self):
        """
        Yield of rating benchmark to override and that will be used to compute rating spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("ratingBenchmarkCurveYieldPercent")

    @rating_benchmark_curve_yield_percent.setter
    def rating_benchmark_curve_yield_percent(self, value):
        self._set_parameter("ratingBenchmarkCurveYieldPercent", value)

    @property
    def issuer_spread_bp(self):
        """
        Spread of issuer benchmark to override and that will be used as pricing analysis input to compute
        the bond price. This spread is computed is for coprorate bonds.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("issuerSpreadBp")

    @issuer_spread_bp.setter
    def issuer_spread_bp(self, value):
        self._set_parameter("issuerSpreadBp", value)

    @property
    def issuer_benchmark_curve_yield_percent(self):
        """
        Yield of issuer benchmark to override and that will be used to compute issuer spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("issuerBenchmarkCurveYieldPercent")

    @issuer_benchmark_curve_yield_percent.setter
    def issuer_benchmark_curve_yield_percent(self, value):
        self._set_parameter("issuerBenchmarkCurveYieldPercent", value)

    @property
    def sector_rating_spread_bp(self):
        """
        Spread of sector rating benchmark to override and that will be used as pricing analysis input to
        compute the bond price.
        Optional. No override is applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("sectorRatingSpreadBp")

    @sector_rating_spread_bp.setter
    def sector_rating_spread_bp(self, value):
        self._set_parameter("sectorRatingSpreadBp", value)

    @property
    def sector_rating_benchmark_curve_yield_percent(self):
        """
        Yield of sector rating benchmark to override and that will be used to compute sector rating spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("sectorRatingBenchmarkCurveYieldPercent")

    @sector_rating_benchmark_curve_yield_percent.setter
    def sector_rating_benchmark_curve_yield_percent(self, value):
        self._set_parameter("sectorRatingBenchmarkCurveYieldPercent", value)

    @property
    def asset_swap_spread_bp(self):
        """
        AssetSwapSpread to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing anlysis input should be defined.
        """
        return self._get_parameter("assetSwapSpreadBp")

    @asset_swap_spread_bp.setter
    def asset_swap_spread_bp(self, value):
        self._set_parameter("assetSwapSpreadBp", value)

    @property
    def option_adjusted_spread_bp(self):
        """
        Option Adjusted Spread to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("optionAdjustedSpreadBp")

    @option_adjusted_spread_bp.setter
    def option_adjusted_spread_bp(self, value):
        self._set_parameter("optionAdjustedSpreadBp", value)

    @property
    def user_defined_spread_bp(self):
        """
        Spread of user defined instrument to override and that will be used as pricing analysis input to compute
        the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("userDefinedSpreadBp")

    @user_defined_spread_bp.setter
    def user_defined_spread_bp(self, value):
        self._set_parameter("userDefinedSpreadBp", value)

    @property
    def user_defined_benchmark_yield_percent(self):
        """
        Yield of user defined instrument to override and that will be used to compute user defined spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("userDefinedBenchmarkYieldPercent")

    @user_defined_benchmark_yield_percent.setter
    def user_defined_benchmark_yield_percent(self, value):
        self._set_parameter("userDefinedBenchmarkYieldPercent", value)

    @property
    def user_defined_benchmark_price(self):
        """
        Price of user defined instrument to override and that will be used to compute user defined spread.
        Optional. No override is applied by default and price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("userDefinedBenchmarkPrice")

    @user_defined_benchmark_price.setter
    def user_defined_benchmark_price(self, value):
        self._set_parameter("userDefinedBenchmarkPrice", value)

    @property
    def benchmark_at_issue_price(self):
        """
        Price of benchmark at issue to override and that will be used to compute benchmark at redemption spread.
        Optional. No override is applied by default and price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtIssuePrice")

    @benchmark_at_issue_price.setter
    def benchmark_at_issue_price(self, value):
        self._set_parameter("benchmarkAtIssuePrice", value)

    @property
    def benchmark_at_issue_yield_percent(self):
        """
        Yield of benchmark at issue to override and that will be used to compute benchmark at redemption spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return:
        """
        return self._get_parameter("benchmarkAtIssueYieldPercent")

    @benchmark_at_issue_yield_percent.setter
    def benchmark_at_issue_yield_percent(self, value):
        self._set_parameter("benchmarkAtIssueYieldPercent", value)

    @property
    def benchmark_at_issue_spread_bp(self):
        """
        Spread of benchmark at issue to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("benchmarkAtIssueSpreadBp")

    @benchmark_at_issue_spread_bp.setter
    def benchmark_at_issue_spread_bp(self, value):
        self._set_parameter("benchmarkAtIssueSpreadBp", value)

    @property
    def benchmark_at_issue_ric(self):
        """
        Ric of benchmark at issue to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: string
        """
        return self._get_parameter("benchmarkAtIssueRic")

    @benchmark_at_issue_ric.setter
    def benchmark_at_issue_ric(self, value):
        self._set_parameter("benchmarkAtIssueRic", value)

    @property
    def efp_benchmark_price(self):
        """
        Price of EFP benchmark to override and that will be used to compute benchmark at redemption spread
         in case the bond is an australian FRN.
         Optional. No override is applied by default and price is computed or retrieved from market data."
        :return: float
        """
        return self._get_parameter("efpBenchmarkPrice")

    @efp_benchmark_price.setter
    def efp_benchmark_price(self, value):
        self._set_parameter("efpBenchmarkPrice", value)

    @property
    def efp_benchmark_yield_percent(self):
        """
        Yield of EFP benchmark to override and that will be used to compute benchmark at redemption spread
         in case the bond is an australian FRN.
         Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("efpBenchmarkYieldPercent")

    @efp_benchmark_yield_percent.setter
    def efp_benchmark_yield_percent(self, value):
        self._set_parameter("efpBenchmarkYieldPercent", value)

    @property
    def efp_spread_bp(self):
        """
        Spread of EFP benchmark to override and that will be used as pricing analysis input to compute
        the bond price in case the bond is an australian FRN.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return:
        """
        return self._get_parameter("efpSpreadBp")

    @efp_spread_bp.setter
    def efp_spread_bp(self, value):
        self._set_parameter("efpSpreadBp", value)

    @property
    def efp_benchmark_ric(self):
        """
        RIC of EFP benchmark to override and that will be used as pricing analysis input to compute
        the bond price in case the bond is an australian FRN. Ric can be  only "YTTc1" or "YTCc1".
        Optional. Default value is "YTTc1".
        :return: string
        """
        return self._get_parameter("efpBenchmarkRic")

    @efp_benchmark_ric.setter
    def efp_benchmark_ric(self, value):
        self._set_parameter("efpBenchmarkRic", value)

    @property
    def benchmark_at_redemption_price(self):
        """
        Price of benchmark at redemption to override and that will be used to compute benchmark at redemption spread.
        Optional. No override is applied by default and price is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtRedemptionPrice")

    @benchmark_at_redemption_price.setter
    def benchmark_at_redemption_price(self, value):
        self._set_parameter("benchmarkAtRedemptionPrice", value)

    @property
    def benchmark_at_redemption_yield_percent(self):
        """
        Yield of benchmark at redemption to override and that will be used to compute benchmark at redemption spread.
        Optional. No override is applied by default and yield is computed or retrieved from market data.
        :return: float
        """
        return self._get_parameter("benchmarkAtRedemptionYieldPercent")

    @benchmark_at_redemption_yield_percent.setter
    def benchmark_at_redemption_yield_percent(self, value):
        self._set_parameter("benchmarkAtRedemptionYieldPercent", value)

    @property
    def benchmark_at_redemption_spread_bp(self):
        """
        Spread of benchmark at redemption to override and that will be used as pricing analysis input to compute the bond price.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("benchmarkAtRedemptionSpreadBp")

    @benchmark_at_redemption_spread_bp.setter
    def benchmark_at_redemption_spread_bp(self, value):
        self._set_parameter("benchmarkAtRedemptionSpreadBp", value)

    @property
    def current_yield_percent(self):
        """
        Current Yield (expressed in percent) to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("currentYieldPercent")

    @current_yield_percent.setter
    def current_yield_percent(self, value):
        self._set_parameter("currentYieldPercent", value)

    @property
    def strip_yield_percent(self):
        """
        Strip Yield (expressed in percent) to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing anlysis input should be defined.
        :return: float
        """
        return self._get_parameter("stripYieldPercent")

    @strip_yield_percent.setter
    def strip_yield_percent(self, value):
        self._set_parameter("stripYieldPercent", value)

    @property
    def discount_percent(self):
        """
        Discount (expressed in percent) to override and that will be used as pricing analysis input.
        Should be used only for bond quoted in discount.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("discountPercent")

    @discount_percent.setter
    def discount_percent(self, value):
        self._set_parameter("discountPercent", value)

    @property
    def net_price(self):
        """
        Net price to override and that will be used as pricing analysis input.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("netPrice")

    @net_price.setter
    def net_price(self, value):
        self._set_parameter("netPrice", value)

    @property
    def discount_margin_bp(self):
        """
        Discount Margin basis points to override and that will be used as pricing analysis input.
        Available only for Floating Rate Notes.
        Optional.No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("discountMarginBp")

    @discount_margin_bp.setter
    def discount_margin_bp(self, value):
        self._set_parameter("discountMarginBp", value)

    @property
    def simple_margin_bp(self):
        """
        Simple Margin basis points  to override and that will be used as pricing analysis input.
        Available only for Floating Rate Notes.
        Optional.No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("simpleMarginBp")

    @simple_margin_bp.setter
    def simple_margin_bp(self, value):
        self._set_parameter("simpleMarginBp", value)

    @property
    def price_side(self):
        """
        Quoted price side of the bond to use for pricing Analysis.
        Optional. By default the MID price of the bond is used.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def rounding_parameters(self):
        """
        Definition of rounding parameters to be applied on accrued, price or yield.
        Optional. By default, rounding parameters are the ones defined in the bond structure.
        :return: RoudingParameters
        """
        return self._get_parameter("roundingParameters")

    @rounding_parameters.setter
    def rounding_parameters(self, value):
        self._set_parameter("roundingParameters", value)

    @property
    def redemption_date_type(self):
        """
        Redemption type of the bond. It is used to compute the default redemption date:
            - RedemptionAtMaturityDate : yield and price are computed at maturity date.
            - RedemptionAtCallDate : yield and price are computed at call date (next call date by default).
            - RedemptionAtPutDate : yield and price are computed at put date (next put date by default)..
            - RedemptionAtWorstDate : yield and price are computed at the lowest yield date.
            - RedemptionAtSinkDate : yield and price are computed at sink date.
            - RedemptionAtParDate : yield and price are computed at next par.
            - RedemptionAtPremiumDate : yield and price are computed at next premium.
            - RedemptionAtMakeWholeCallDate : yield and price are computed at Make Whole Call date.
            - RedemptionAtAverageLife : yield and price are computed at average life (case of sinkable bonds)
            - RedemptionAtNextDate : yield and price are computed at next redemption date available.
        Optional. Default value is "RedemptionAtWorstDate" for callable bond, "RedemptionAtBestDate" for puttable bond or "RedemptionAtMaturityDate".
        :return: enum RedemptionDateType
        """
        return self._get_enum_parameter(RedemptionDateType, "redemptionDateType")

    @redemption_date_type.setter
    def redemption_date_type(self, value):
        self._set_enum_parameter(RedemptionDateType, "redemptionDateType", value)

    @property
    def redemption_date(self):
        """
        Redemption date that defines the end date for yield and price computation.
        Used only if redemption date type is set to "RedemptionAtCustomDate"
        :return: datetime
        """
        return self._get_parameter("redemptionDate")

    @redemption_date.setter
    def redemption_date(self, value):
        self._set_parameter("redemptionDate", value)

    @property
    def yield_type(self):
        """
        YieldType that specifies the rate structure.
        Optional. The default value is NATIVE.
        :return: enum YieldType
        """
        return self._get_enum_parameter(YieldType, "yieldType")

    @yield_type.setter
    def yield_type(self, value):
        self._set_enum_parameter(YieldType, "yieldType", value)

    @property
    def tax_on_yield_percent(self):
        """
        Tax Rate on Yield expressed in percent. Also named Tax on Yield.
        Optional. By default no tax is applied that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnYieldPercent")

    @tax_on_yield_percent.setter
    def tax_on_yield_percent(self, value):
        self._set_parameter("taxOnYieldPercent", value)

    @property
    def tax_on_capital_gain_percent(self):
        """
        Tax Rate on capital gain expressed in percent.
         Optional. By default no tax is applied that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnCapitalGainPercent")

    @tax_on_capital_gain_percent.setter
    def tax_on_capital_gain_percent(self, value):
        self._set_parameter("taxOnCapitalGainPercent", value)

    @property
    def tax_on_coupon_percent(self):
        """
        Tax Rate on Coupon  expressed in percent.
         Optional. By default no tax is applied that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnCouponPercent")

    @tax_on_coupon_percent.setter
    def tax_on_coupon_percent(self, value):
        self._set_parameter("taxOnCouponPercent", value)

    @property
    def tax_on_price_percent(self):
        """
        Tax Rate on price  expressed in percent.
         Optional. By default no tax is applied that means value is equal to 0.
        :return: float
        """
        return self._get_parameter("taxOnPricePercent")

    @tax_on_price_percent.setter
    def tax_on_price_percent(self, value):
        self._set_parameter("taxOnPricePercent", value)

    @property
    def apply_tax_to_full_pricing(self):
        """
        Tax Parameters Flag to set these tax parameters for all pricing/schedule/risk/spread.
         Optional. By default Tax Params are applied only to Muni.
        :return: bool
        """
        return self._get_parameter("applyTaxToFullPricing")

    @apply_tax_to_full_pricing.setter
    def apply_tax_to_full_pricing(self, value):
        self._set_parameter("applyTaxToFullPricing", value)

    @property
    def concession_fee(self):
        """
        Fee to apply to the bond price; It is expressed in the same unit that the bond price (percent or cash).
        :return: float
        """
        return self._get_parameter("concessionFee")

    @concession_fee.setter
    def concession_fee(self, value):
        self._set_parameter("concessionFee", value)

    @property
    def benchmark_yield_selection_mode(self):
        """
        The benchmark yield selection mode.
        Optional. Default value is INTERPOLATE.
        :return: enum BenchmarkYieldSelectionMode
        """
        return self._get_enum_parameter(
            BenchmarkYieldSelectionMode, "benchmarkYieldSelectionMode"
        )

    @benchmark_yield_selection_mode.setter
    def benchmark_yield_selection_mode(self, value):
        self._set_enum_parameter(
            BenchmarkYieldSelectionMode, "benchmarkYieldSelectionMode", value
        )

    @property
    def market_value_in_deal_ccy(self):
        """
        Market value in deal currency. This field can be used to compute notionalAmount to apply to get this market value.
        Optional. By default the value is computed from notional amount.
        NotionalAmount field, MarketValueInDealCcy field and MarketValueInReportCcy field cannot be set at defined at the same time.
        :return: float
        """
        return self._get_parameter("marketValueInDealCcy")

    @market_value_in_deal_ccy.setter
    def market_value_in_deal_ccy(self, value):
        self._set_parameter("marketValueInDealCcy", value)

    @property
    def market_value_in_report_ccy(self):
        """
        Market value in report currency. This field can be used to compute notionalAmount to apply to get this market value.
        Optional. By default the value is computed from notional amount.
        NotionalAmount field, MarketValueInDealCcy field and MarketValueInReportCcy field cannot be set at defined at the same time.
        :return: float
        """
        return self._get_parameter("marketValueInReportCcy")

    @market_value_in_report_ccy.setter
    def market_value_in_report_ccy(self, value):
        self._set_parameter("marketValueInReportCcy", value)

    @property
    def projected_index_calculation_method(self):
        """
        Flag used to define how projected index is computed.
        Optional. Default value is CONSTANT_INDEX. It is defaulted to FORWARD_INDEX for Preferreds and Brazilian Debenture bonds.
        :return: enum ProjectedIndexCalculationMethod
        """
        return self._get_enum_parameter(
            ProjectedIndexCalculationMethod, "projectedIndexCalculationMethod"
        )

    @projected_index_calculation_method.setter
    def projected_index_calculation_method(self, value):
        self._set_enum_parameter(
            ProjectedIndexCalculationMethod, "projectedIndexCalculationMethod", value
        )

    @property
    def initial_margin_percent(self):
        """
        :return: float
        """
        return self._get_parameter("initialMarginPercent")

    @initial_margin_percent.setter
    def initial_margin_percent(self, value):
        self._set_parameter("initialMarginPercent", value)

    @property
    def haircut_rate_percent(self):
        """
        Repo contract's Haircut par in percentage, for computing the transaction's Margin.
        Optional.
        :return: float
        """
        return self._get_parameter("haircutRatePercent")

    @haircut_rate_percent.setter
    def haircut_rate_percent(self, value):
        self._set_parameter("haircutRatePercent", value)

    @property
    def clean_future_price(self):
        """
        Repo Clean Future Value in percentage. It will be used to compute the Implied Repo Rate or the NPV.
        Optional.
        :return: float
        """
        return self._get_parameter("cleanFuturePrice")

    @clean_future_price.setter
    def clean_future_price(self, value):
        self._set_parameter("cleanFuturePrice", value)

    @property
    def dirty_future_price(self):
        """
        Repo Gross Future Value in percentage. It will be used to compute the Implied Repo Rate or the NPV.
        Optional.
        :return:
        """
        return self._get_parameter("dirtyFuturePrice")

    @dirty_future_price.setter
    def dirty_future_price(self, value):
        self._set_parameter("dirtyFuturePrice", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        Optional. By default, the valuation date is MarketDataDate or Today.
        :return: datetime
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)

    @property
    def interpolate_missing_points(self):
        """
        The report currency: Pricing data is computed in deal currency.
        If a report currency is set, pricing data is also computed in report currency.
        Optional.
        :return: bool
        """
        return self._get_parameter("interpolateMissingPoints")

    @interpolate_missing_points.setter
    def interpolate_missing_points(self, value):
        self._set_parameter("interpolateMissingPoints", value)

    @property
    def report_ccy(self):
        return self._get_parameter("reportCcy")

    @report_ccy.setter
    def report_ccy(self, value):
        self._set_parameter("reportCcy", value)

    @property
    def market_data_date(self):
        """
        The market data date for pricing.
        Optional. By default, the marketDataDate date is the ValuationDate or Today.
        :return: datetime
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def quote_fallback_logic(self):
        """
        Enumeration used to define the fallback logic for the quotation of the instrument. Available values are:
        - "None": it means that there's no fallback logic. For example, if the user asks for a "Ask" price and instrument is only quoted with a "Bid" price, it is an error case.
        - "BestField" : it means that there's a fallback logic to use another market data field as quoted price. For example, if the user asks for a "Ask" price and instrument is only quoted with a "Bid" price, "Bid" price can be used.
        :return: enum QuoteFallbackLogic
        """
        return self._get_enum_parameter(QuoteFallbackLogic, "quoteFallbackLogic")

    @quote_fallback_logic.setter
    def quote_fallback_logic(self, value):
        self._set_enum_parameter(QuoteFallbackLogic, "quoteFallbackLogic", value)
