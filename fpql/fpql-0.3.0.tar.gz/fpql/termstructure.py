from typing import List
from .pymodels import *
import QuantLib as ql
from .pym_ql_utils import *
from .ql_utils import *
from .ql_conventions import *


def curve_piecewise(value_date: str, 
                depo_setting: DepoSetting, 
                depo_rates: List[Rate], 
                par_setting:BondSetting, 
                par_rates: List[Rate], 
                cal = None, 
                method: PiecewiseMethods = PiecewiseMethods.logcubicdiscount):
    
    vdate = datestr_to_qldate(value_date) 
    ql.Settings.instance().evaluationDate = vdate
    if not cal:
        calendar = ql.WeekendsOnly()
    else:
        calendar = ql.WeekendsOnly()
    
    depo_helpers = deporate_2_depohelpers(depo_setting, depo_rates)
    bond_helpers = parrate_2_bondhelpers(value_date, par_setting, par_rates)

    rate_helpers = depo_helpers + bond_helpers
    
    if method == PiecewiseMethods.loglineardiscount:
        t_structure = ql.PiecewiseLogLinearDiscount(vdate,
                                                rate_helpers,
                                                ql_day_count[par_setting.day_count])
    elif method == PiecewiseMethods.linearforward:
        t_structure = ql.PiecewiseLinearForward(vdate,
                                                rate_helpers,
                                                ql_day_count[par_setting.day_count])
    elif method == PiecewiseMethods.linearzero:
        t_structure = ql.PiecewiseLinearZero(vdate,
                                            rate_helpers,
                                            ql_day_count[par_setting.day_count])
    elif method == PiecewiseMethods.cubiczero:
        t_structure = ql.PiecewiseCubicZero(vdate,
                                            rate_helpers,
                                            ql_day_count[par_setting.day_count])
    elif method == PiecewiseMethods.splinecubicdiscount:
        t_structure = ql.PiecewiseSplineCubicDiscount(vdate,
                                                rate_helpers,
                                                ql_day_count[par_setting.day_count])
    else:
        t_structure = ql.PiecewiseLogCubicDiscount(vdate,
                                                rate_helpers,
                                                ql_day_count[par_setting.day_count])
    #return the term structure
    return t_structure


def calc_curve(value_date: str, 
                depo_setting: DepoSetting, 
                depo_rates: List[Rate], 
                par_setting:BondSetting, 
                par_rates: List[Rate], 
                country = None, 
                method: str = "LogCubicDiscount" ):
        
    if country:
        try:
            calendar = ql_calendar_market[country]
        except:
            calendar = None
    t_structure = curve_piecewise(value_date, 
                depo_setting, 
                depo_rates, 
                par_setting, 
                par_rates, 
                cal = calendar,
                method= method)

    day_count = ql_day_count[par_setting.day_count]
    tenors = ["1D", "1W", "2W", "3W"]
    tenors_monthly = [ "".join([str(no + 1),"M"]) for no in range(360)]
    all_tenors = tenors + tenors_monthly

    vdate = datestr_to_qldate(value_date)
    dates = []
    dfs = []
    rates = []
    days = []
    maxDate = t_structure.maxDate()
    for atenor in all_tenors:
        adate = ql.NullCalendar().advance(vdate, 
                                        ql.Period(atenor),     
                                        ql_business_day[par_setting.business_day], 
                                        False)
        if adate <= maxDate:
            day = adate - vdate
            yrs = day_count.yearFraction(vdate, adate)
            compounding = ql.Compounded
            freq = ql_frequency[par_setting.frequency]
            
            zero_rate = t_structure.zeroRate(yrs, compounding, freq)
            tenors.append(yrs)
            eq_rate = zero_rate.equivalentRate(day_count,
                                            compounding,
                                            freq,
                                            vdate,
                                            adate)
            therate = eq_rate.rate()
            df = t_structure.discount(yrs,True)
            rates.append(therate*100)
            dfs.append(df)
            dates.append(adate.ISO())
            days.append(day)
        else:
            break

    zero_set = {"value_date": value_date, "day_count": par_setting.day_count, 
                "compound": "Compounded", "frequency": par_setting.frequency,
                "days": days, "dates": dates, "rates": rates}
    zerocurve = ZeroCurve(**zero_set)

    df_set = {"value_date": value_date, "day_count": par_setting.day_count, 
            "days": days, "dates": dates, "dfs": dfs}
    discountcurve = DiscountCurve(**df_set)

    return zero_set, df_set
    

def calc_qlzerorate(from_date: str, to_date: str, day_count: DayCount,
                    t_structure: ql.QuantLib.TermStructure, compounding,
                    frequency: Frequency):

    fdate = datestr_to_qldate(from_date)
    tdate = datestr_to_qldate(to_date)
    ql_dc = ql_day_count[day_count]
    yrs = ql_dc.yearFraction(fdate, tdate)
    zero_rate = t_structure.zeroRate(yrs, 
                                    ql_compounding[compounding], 
                                    ql_frequency[frequency])
    return zero_rate


def calc_equiv_rate(from_date: str, 
                    to_date: str,
                    qlrate: ql.QuantLib.InterestRate,
                    day_count: DayCount,
                    compounding,
                    frequency: Frequency):
    fdate = datestr_to_qldate(from_date)
    tdate = datestr_to_qldate(to_date)
    rate = qlrate.equivalentRate(ql_day_count[day_count],
                                ql_compounding[compounding],
                                ql_frequency[frequency],
                                fdate,
                                tdate).rate()
    return rate

    
def ql_spread_handle(value_date: str, 
                    t_structure, 
                    spreads: List[Rate],
                    calendar = None):
    vdate = datestr_to_qldate(value_date)
    ts_handle = ql.YieldTermStructureHandle(t_structure)
    
    if calendar == None:
        qlcalendar = ql.WeekendsOnly()
    else:
        qlcalendar = calendar

    spread_handles = []
    spread_dates = []
    spread_quotes = []

    for spread in spreads:
        spread_quote = ql.SimpleQuote(spread.rate/100)
        spread_quotes.append(spread_quote)
        spread_handle = ql.QuoteHandle(spread_quote)
        spread_handles.append(spread_handle)
        maturity = qlcalendar.advance(vdate, get_qlPeriod(spread.tenor))
        spread_dates.append(maturity)

    spread_curve = ql.SpreadedLinearZeroInterpolatedTermStructure(
                            ts_handle,
                            spread_handles,
                            spread_dates)
    spread_curve_handle = ql.YieldTermStructureHandle(spread_curve)

    return spread_curve_handle
    






