# coding: utf8
# contract_gen 2020-05-19 11:24:17.153908


__all__ = ["Definition"]

from ...instrument.instrument_definition import InstrumentDefinition
from ...enum_types.day_count_basis import DayCountBasis
from ._repo_underlying_contract import UnderlyingContract


class Definition(InstrumentDefinition):
    def __init__(
        self,
        *,
        instrument_tag=None,
        underlying_instruments=None,
        start_date=None,
        end_date=None,
        tenor=None,
        is_coupon_exchanged=None,
        repo_rate_percent=None,
        day_count_basis=None,
    ):
        """
        :param day_count_basis: DayCountBasis
        :param underlying_instruments: RepoUnderlyingContract
        :param end_date: str
        :param instrument_tag: str
        :param is_coupon_exchanged: bool
        :param repo_rate_percent: float
        :param start_date: str
        :param tenor: str
        """
        super().__init__()
        self.instrument_tag = instrument_tag
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.day_count_basis = day_count_basis
        self.underlying_instruments = underlying_instruments
        self.is_coupon_exchanged = is_coupon_exchanged
        self.repo_rate_percent = repo_rate_percent

    @classmethod
    def get_instrument_type(cls):
        return "Repo"

    @property
    def day_count_basis(self):
        """
        Day Count Basis convention to apply to the custom Repo rate.
        Optional, "Dcb_Actual_360" by default.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "dayCountBasis")

    @day_count_basis.setter
    def day_count_basis(self, value):
        self._set_enum_parameter(DayCountBasis, "dayCountBasis", value)

    @property
    def underlying_instruments(self):
        """
        Definition of the underlying instruments. Only Bond Contracts are supported for now, and only one Bond can be used.
        Mandatory.
        :return: list RepoUnderlyingContract
        """
        return self._get_list_parameter(UnderlyingContract, "underlyingInstruments")

    @underlying_instruments.setter
    def underlying_instruments(self, value):
        self._set_list_parameter(UnderlyingContract, "underlyingInstruments", value)

    @property
    def end_date(self):
        """
        End date of the repo, that means when the borrower repurchases the security back.
        Either EndDate or Tenor field are requested.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

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
    def is_coupon_exchanged(self):
        """
        Specifies whether or not intermediate coupons are exchanged.
        - CouponExchanged = True to specify that intermediate coupons for the underlying bond (between the repo start date and repo end date) are exchanged between the repo seller and repo buyer.
        - CouponExchanged = False to specify that no intermediate coupons are exchanged between the repo seller and repo buyer. In this case the repo instrument is like a standard loan with no intermediate coupons; the bond is only used as a warranty in case the money borrower defaults.
        Optional. True by default, which means coupon exchanged.
        :return: bool
        """
        return self._get_parameter("isCouponExchanged")

    @is_coupon_exchanged.setter
    def is_coupon_exchanged(self, value):
        self._set_parameter("isCouponExchanged", value)

    @property
    def repo_rate_percent(self):
        """
        Custom Repo Rate in percentage. If not provided in the request, it will be computed by interpolating/extrapolating a Repo Curve.
        Optional.
        :return: float
        """
        return self._get_parameter("repoRatePercent")

    @repo_rate_percent.setter
    def repo_rate_percent(self, value):
        self._set_parameter("repoRatePercent", value)

    @property
    def start_date(self):
        """
        Start date of the repo, that means when the the underlying security is exchanged.
        Mandatory.
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def tenor(self):
        """
        Tenor that defines the duration of the Repo in case no EndDate has been provided. In that case, EndDate is computed from StartDate and Tenor.
        Either EndDate or Tenor field are requested.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)
