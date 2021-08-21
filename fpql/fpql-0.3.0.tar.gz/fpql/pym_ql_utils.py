import QuantLib as ql
from typing import List
from .pymodels import *
from .ql_utils import *
from .ql_conventions import *


def deporate_2_depohelpers(depo_setting: DepoSetting, rates: List[Rate],  calendar=None ):
    if not calendar:
        cal = ql.WeekendsOnly()
    else:
        cal = calendar
    depo_helpers = []
    business_day = ql_business_day[depo_setting.business_day]
    day_count = ql_day_count[depo_setting.day_count]
    for rate in rates:
        quote_handle = ql.QuoteHandle(ql.SimpleQuote(rate.rate/100))
        ql_period = ql.Period(rate.tenor)
        dr_helper = ql.DepositRateHelper(quote_handle, ql_period, 
                    depo_setting.start_basis, cal, business_day,
                    depo_setting.eom, day_count)
        depo_helpers.append(dr_helper)
    
    return depo_helpers


def parrate_2_bondhelpers(value_date: str,  
                        parbond_setting: BondSetting, 
                        rates: List[Rate],
                        calendar=None ):
    if not calendar:
        cal = ql.WeekendsOnly()
    else:
        cal = calendar

    vdate = datestr_to_qldate(value_date)    
    ql_period = ql.Period(ql_freq_tenor[parbond_setting.frequency])
    par_value = 100
    quote_handle = ql.QuoteHandle(ql.SimpleQuote(par_value))
    
    fix_helpers = [] #list to keep individual helper
    for rate in rates:
        #Need ql.Schedule to use ql.FixedRateBondHelper
        maturity = cal.advance(vdate, ql.Period(rate.tenor),     
                                    ql_business_day[parbond_setting.business_day], 
                                    True)
        schedule = ql.Schedule(vdate, 
                            maturity, 
                            ql_period, 
                            cal, 
                            ql_business_day[parbond_setting.business_day],
                            ql_business_day[parbond_setting.terminate_business_day],
                            ql_date_generation[parbond_setting.date_gen],
                            parbond_setting.is_eom)
    
        fix_helper = ql.FixedRateBondHelper(quote_handle, 
                            parbond_setting.start_basis, 
                            par_value, 
                            schedule, 
                            [rate.rate/100],
                            ql_day_count[parbond_setting.day_count])
        fix_helpers.append(fix_helper)

    return fix_helpers


