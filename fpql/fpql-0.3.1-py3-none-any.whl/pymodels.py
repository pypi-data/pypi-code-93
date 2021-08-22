from .ql_enums import *
from .ql_conventions import *

from pydantic import BaseModel, validator
from typing import List, Optional
from numpy import datetime64 as dt64


class Rate(BaseModel):
    tenor: str
    rate: float

    @validator('tenor')
    def valid_tenor(cls, v):
        prd = v[-1]
        number = v[:len(v)-1]
        if prd not in ['d', 'D', 'w', 'W', 'm', 'M', "y", "Y"]:
            raise ValueError('not a valid period')
        else:
            try:
                x = int(number)
            except:
                raise ValueError('not a valid period')
        return  v

    @validator('rate')
    def valid_rate(cls, v):
        
        try:
            x = float(v)
        except:
            raise ValueError('rate must be a number')
        return  v


class Holiday(BaseModel):
    date: str

    @validator('date')
    def valid_rate(cls, v): 
        try:
            thedate = dt64(v)
        except:
            raise ValueError('not a valid date format for Holidays')
        return  v


class DepoSetting(BaseModel):
    start_basis: StartBasis = StartBasis.today
    business_day: BusinessDay = BusinessDay.no_adjustment
    day_count: DayCount = DayCount.act_act_act365
    eom: bool = False


class BondSetting(BaseModel):
    frequency: Frequency = Frequency.semi_annual
    start_basis: StartBasis = StartBasis.today
    day_count: DayCount = DayCount.act_act_act365
    #pmt_day_count: DayCount = DayCount.act_act_act365
    business_day: BusinessDay = BusinessDay.no_adjustment
    terminate_business_day: BusinessDay = BusinessDay.mod_following
    date_gen: DateGeneration = DateGeneration.backward
    is_eom: bool = False


    @validator('day_count')
    def valid_day_count(cls, v): 
        if v not in ql_day_count.keys():
            raise ValueError
        return  v

    @validator('business_day')
    def valid_business_day(cls, v): 
        if v not in ql_business_day.keys():
            raise ValueError
        return  v

    @validator('frequency')
    def valid_frequency(cls, v): 
        if v not in ql_frequency.keys():
            raise ValueError
        return  v

    @validator('date_gen')
    def valid_date_gen(cls, v): 
        if v not in ql_date_generation.keys():
            raise ValueError
        return  v


class Structure(BaseModel):
    start_date: str 
    end_date: str 
    payment_date: Optional[str] = None
    face_value: float 
    coupon: float 
    dcf: Optional[float]= None
    interest: Optional[float] = None
    face_value_flow: float = 0
    cashflow: Optional[float]= None

    @validator('start_date', 'end_date')
    def valid_issue_date(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v


    @validator('face_value', 'coupon', 'face_value_flow')
    def valid_float(cls, v): 
        try:
            anumber = float(v)
        except:
            raise ValueError
        return  v


class DiscountCurve(BaseModel):
    value_date: str
    day_count: DayCount
    dates: List[str] = []
    days: List[int] = []
    dfs: List[float] = []


    @validator('value_date')
    def valid_value_date(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v


class ZeroCurve(BaseModel):
    value_date: str
    day_count: DayCount
    compound: Compounding
    frequency: Frequency
    dates: List[str] = []
    days: List[int] = []
    rates: List[float] = []


    @validator('value_date')
    def valid_value_date(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v


    @validator('day_count')
    def valid_day_count(cls, v): 
        if v not in ql_day_count.keys():
            raise ValueError
        return  v


    @validator('compound')
    def valid_compound(cls, v): 
        if v not in ql_compounding.keys():
            raise ValueError
        return  v


    @validator('frequency')
    def valid_frequency(cls, v): 
        if v not in ql_frequency.keys():
            raise ValueError
        return  v


class FixedRateBond(BaseModel):
    issue_date: Optional[str] = None
    maturity: str
    settings: BondSetting
    face_value: Optional[float] = 100.00
    coupon: float 
    structure: Optional[List[Structure]] = None

    @validator('face_value', 'coupon')
    def valid_float(cls, v): 
        try:
            anumber = float(v)
        except:
            raise ValueError
        return  v

    @validator('issue_date', 'maturity')
    def valid_date(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v


class StructuredBond(BaseModel):
    issue_date: Optional[str] = None
    maturity: str
    settings: BondSetting
    structure: List[Structure] = []

    @validator('maturity')
    def valid_maturity(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v

    @validator('issue_date')
    def valid_issue_date(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v


class CouponInspector(BaseModel):
    previous_coupon_rate: float
    next_coupon_rate: float 
    accrual_start_date: str
    accrual_end_date: str
    accrual_period: float
    accrual_days: float
    accrued_period: float
    accrued_days: float
    accrued_amount: float


class CashFlowInspector(BaseModel):
    previous_cashflow_date: str
    previous_cashflow_amount: float
    next_cashflow_date: float
    next_cashflow_amount: float


class BondRisk(BaseModel):
    accrued: Optional[float] = None
    ytm: Optional[float] = None
    clean_price: Optional[float] = None
    bps: Optional[float] = None
    duration: Optional[float] = None
    modified_duration: Optional[float] = None
    convexity: Optional[float] = None
    basis_point_value: Optional[float] = None
    yield_value_basis_point: Optional[float] = None
    

class BondRisk2(BondRisk):
    value: Optional[float] = None
    value_after_shift: Optional[float] = None


class CashFlow(BaseModel):
    date: str 
    amount: float

    @validator('date')
    def valid_date(cls, v): 
        try:
            adate = dt64(v)
        except:
            raise ValueError
        return  v

    @validator('amount')
    def valid_float(cls, v): 
        try:
            anumber = float(v)
        except:
            raise ValueError
        return  v


class CallabilityPrice(BaseModel):
    price_type: BondPriceType = BondPriceType.clean
    price: float
    date: str
    option_type: OptionType = OptionType.calloption

