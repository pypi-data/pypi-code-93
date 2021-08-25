from .bonds import get_qlfixedratebond
import QuantLib as ql 
from .ql_enums import *
from .pymodels import *
from .ql_utils import *
from .ql_conventions import *
from .termstructure import *

def sample_piecewise(value_date):
    rates, depo_setting, parrates, par_setting = sample_curveinfo()

    return curve_piecewise(value_date, 
                            depo_setting, 
                            rates, 
                            par_setting, 
                            parrates)


def sample_curveinfo():
    depo_rates = [
        {"tenor": "1M", "rate": 2.00},
        {"tenor": "2M", "rate": 2.05}, 
        {"tenor": "3M", "rate": 2.10},
        {"tenor": "6M", "rate": 2.20}
    ]

    rates = []
    for depo_rate in depo_rates:
        rate = Rate(**depo_rate)
        rates.append(rate)

    depo_sett = {
        "start_basis": StartBasis.today, 
        "business_day": BusinessDay.mod_following,
        "day_count": DayCount.act_act_act365,
        "eom": False
        }
    depo_setting = DepoSetting(**depo_sett)

    par_rates = [
        {"tenor": "1Y", "rate": 2.30},
        {"tenor": "2Y", "rate": 2.40}, 
        {"tenor": "3Y", "rate": 2.50},
        {"tenor": "5Y", "rate": 2.70},
        {"tenor": "7Y", "rate": 2.80},
        {"tenor": "10Y", "rate": 2.90},
        {"tenor": "20Y", "rate": 3.00},
        {"tenor": "30Y", "rate": 3.10}
    ]

    parrates = []
    for par_rate in par_rates:
        rate = Rate(**par_rate)
        parrates.append(rate)

    par_sett = {
        "frequency": "Semi-Annual",
        "start_basis": 2,
        "day_count": "Actual/Actual (ISMA)",
        "business_day": "Modified Following",
        "terminate_business_day": "Modified Following",
        "date_gen": "Backward from maturity date",
        "is_eom":  False
    }
    par_setting = BondSetting(**par_sett)

    return rates, depo_setting, parrates, par_setting


def sample_spreadinfo():
    spread_rates = [
        {"tenor": "1M", "rate": 0.4},
        {"tenor": "2M", "rate": 0.45}, 
        {"tenor": "3M", "rate": 0.5},
        {"tenor": "6M", "rate": 0.55},
        {"tenor": "1Y", "rate": 0.6},
        {"tenor": "2Y", "rate": 0.65}, 
        {"tenor": "3Y", "rate": 0.75},
        {"tenor": "5Y", "rate": 0.85},
        {"tenor": "7Y", "rate": 0.95},
        {"tenor": "10Y", "rate": 1.1},
        {"tenor": "20Y", "rate": 1.3},
        {"tenor": "30Y", "rate": 1.5}
    ]
    rates = []
    for depo_rate in spread_rates:
        rate = Rate(**depo_rate)
        rates.append(rate)
    return rates


#NOTE: changing business_day to no_adjustment will not give
#      clean price of 100 even on issue date.
def sample_bondinfo():
    bondsetting = {
        "frequency":Frequency.semi_annual,
        "start_basis": StartBasis.today,
        "day_count": DayCount.act_act_isma,
        "business_day": BusinessDay.no_adjustment,
        "terminate_business_day": BusinessDay.no_adjustment,
        "date_gen": DateGeneration.backward,
        "is_eom":  True
        }

    setting = BondSetting(**bondsetting)

    bonddata = {"issue_date": "2021-08-18", 
                "maturity": "2025-08-18", 
                "settings": setting, 
                "coupon": 5.00,
                "face_value": 10_000_000
                }
    thebond = FixedRateBond(**bonddata)

    return thebond, setting


# NOTE: it is possible but yet to be tested to have multiple coupons
# for a fixed rate bond since the argument accepts list of coupons
def sample_fixedratebond():
    thebond, setting = sample_bondinfo()
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    #print(ql_period)
    #1. Create Schedule
    schedule = ql.Schedule(datestr_to_qldate(thebond.issue_date), 
                        datestr_to_qldate(thebond.maturity), 
                        ql_period, 
                        ql.WeekendsOnly(), 
                        ql_business_day[setting.business_day],
                        ql_business_day[setting.terminate_business_day],
                        ql_date_generation[setting.date_gen],
                        setting.is_eom)
    fixbond = ql.FixedRateBond(setting.start_basis, 
                thebond.face_value, 
                schedule, 
                [thebond.coupon/100], 
                ql_day_count[setting.day_count])
    return fixbond


def sample_index(setting: BondSetting):
    # Create and index for Floating Rate
    ff = ql.FlatForward(setting.start_basis, 
                        ql.WeekendsOnly(), 
                        0.05,
                        ql_day_count[setting.day_count],
                        ql.Simple, 
                        ql_frequency[setting.frequency])
    
    #yts = ql.RelinkableYieldTermStructureHandle() 
    #yts.linkTo(ff)
    ff_handle = ql.YieldTermStructureHandle(ff)
    frb_engine = ql.DiscountingBondEngine(ff_handle)

    myr_br_index = ql.IborIndex('MYR-BR', 
                        ql.Period('6M'), 
                        0, 
                        ql.MYRCurrency(), 
                        ql.WeekendsOnly(), 
                        ql.ModifiedFollowing, 
                        True, 
                        ql.ActualActual(ql.ActualActual.Actual365),
                        ff_handle)
    #historical fixing is required for the active coupon period
    myr_br_index.addFixing(ql.Date(5,1,2021),0.05)

    return myr_br_index, frb_engine


def sample_FRB():
    thebond, setting = sample_bondinfo()
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    schedule = ql.Schedule(datestr_to_qldate(thebond.issue_date), 
                        datestr_to_qldate(thebond.maturity), 
                        ql_period, 
                        ql.WeekendsOnly(), 
                        ql_business_day[setting.business_day],
                        ql_business_day[setting.terminate_business_day],
                        ql_date_generation[setting.date_gen],
                        setting.is_eom)

    index, engine = sample_index(setting)
    frb = ql.FloatingRateBond(setting.start_basis, 
                            thebond.face_value, 
                            schedule, 
                            index, 
                            ql.ActualActual(ql.ActualActual.Actual365), 
                            spreads=[0.005])
    # Note changing the engine doesnt seem to have an effect
    # presumably bcoz index is set in ql.FloatingRateBond
    frb.setPricingEngine(engine)

    return frb


# NOTE: it is possible but yet to be tested to have multiple coupons
# and face value for a  bond since the argument accepts list of coupons
# and face values. However, the face value can only be amortising which is 
# equivalent to using ql.AmortizingFixedRateBond
def sample_qlbond():
    thebond, setting = sample_bondinfo()
    abond = get_qlfixedratebond(thebond, setting,ql.WeekendsOnly())
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    #print(ql_period)
    #1. Create Schedule
    schedule = ql.Schedule(datestr_to_qldate(thebond.issue_date), 
                        datestr_to_qldate(thebond.maturity), 
                        ql_period, 
                        ql.WeekendsOnly(), 
                        ql_business_day[setting.business_day],
                        ql_business_day[setting.terminate_business_day],
                        ql_date_generation[setting.date_gen],
                        setting.is_eom)
    interest = ql.FixedRateLeg(schedule, 
                                ql_day_count[setting.day_count], 
                                [thebond.face_value], 
                                [thebond.coupon/100])

    bond = ql.Bond(0, ql.WeekendsOnly(), 
                    datestr_to_qldate(thebond.issue_date),
                    interest)
    return bond


def sample_bondrisk(thebond, ql_irate):

    clean_price = ql.BondFunctions.cleanPrice(thebond, ql_irate)
    accrued = ql.BondFunctions.accruedAmount(thebond)
    bps = ql.BondFunctions.bps(thebond, ql_irate)
    duration = ql.BondFunctions.duration(thebond, ql_irate, ql.Duration.Macaulay)
    modified_duration = ql.BondFunctions.duration(thebond, ql_irate, ql.Duration.Modified)
    convexity = ql.BondFunctions.convexity(thebond, ql_irate)
    basis_point_value = ql.BondFunctions.basisPointValue(thebond, ql_irate)
    yield_value_basis_point = ql.BondFunctions.yieldValueBasisPoint(thebond, ql_irate)
    stats = {"accrued":  accrued,
            "clean_price": clean_price,
            "bps": bps,
            "duration": duration,
            "modified_duration": modified_duration,
            "convexity": convexity,
            "basis_point_value": basis_point_value,
            "yield_value_basis_point": yield_value_basis_point}
    bondrisk = BondRisk(**stats)
    return bondrisk


def sample_structuredloaninfo():
    loan_setting = {
        "frequency":Frequency.monthly,
        "start_basis": StartBasis.today,
        "day_count": DayCount.act_act_act365,
        "business_day": BusinessDay.mod_following,
        "terminate_business_day": BusinessDay.mod_following,
        "date_gen": DateGeneration.forward,
        "is_eom":  True
    }

    setting = BondSetting(**loan_setting)
    
    loan_data = {"issue_date": "2021-01-05", 
                "maturity": "2024-01-05", 
                "settings": setting, 
                }
    theloan = StructuredBond(**loan_data)

    return theloan, setting


def sample_fixrate_structuredloan():
    theloan, setting  = sample_structuredloaninfo()
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    schedule = ql.Schedule(datestr_to_qldate(theloan.issue_date), 
                        datestr_to_qldate(theloan.maturity), 
                        ql_period, 
                        ql.WeekendsOnly(), 
                        ql_business_day[setting.business_day],
                        ql_business_day[setting.terminate_business_day],
                        ql_date_generation[setting.date_gen],
                        setting.is_eom)
    
    # Create the loan rate structure which increase by 0.25%
    # info is used by ql.FixedRateLeg
    loan_rates = []
    rate_initial = 5.00
    step = 0.00
    step_size = 0.25
    for i in range(1, len(schedule)):
        loan_rates.append((rate_initial + step)/100)
        step += step_size

    # Setting the array of face values which increases by 200,000
    # info is used by ql.FixedRateLeg
    face_values = []
    fv_initial = 10_000_000.00
    step = 0.00
    fv_step_size = 200_000.00
    for i in range(1, len(schedule)):
        face_values.append(fv_initial + step)
        step += fv_step_size
    #print(face_values)
    interests = ql.FixedRateLeg(schedule, ql_day_count[setting.day_count], 
                face_values, loan_rates)

    cashflows = []
    no_of_cfs = len(face_values)
    fvflows = [-fv_step_size for i in range(no_of_cfs - 1)]
    #print(no_of_cfs)
    for i in range(no_of_cfs):
        if i == no_of_cfs - 1:
            cashflow = face_values[i] - sum(fvflows) +interests[i].amount()
            #print(interests[i].date(), face_values[i], sum(fvflows), interests[i].amount() )
        else:
            cashflow = fvflows[i] + interests[i].amount()
            #print(interests[i].date(), fvflows[i], interests[i].amount() )
        simple_cash_flow = ql.SimpleCashFlow(cashflow, interests[i].date())
        cashflows.append(simple_cash_flow)

    loanleg = ql.Leg(cashflows)

    return loanleg


def sample_floatingrate_structuredloan():
    theloan, setting  = sample_structuredloaninfo()
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    schedule = ql.Schedule(datestr_to_qldate(theloan.issue_date), 
                        datestr_to_qldate(theloan.maturity), 
                        ql_period, 
                        ql.WeekendsOnly(), 
                        ql_business_day[setting.business_day],
                        ql_business_day[setting.terminate_business_day],
                        ql_date_generation[setting.date_gen],
                        setting.is_eom)
    
    
    # Setting the array of face values which increases by 200,000
    # info is used by ql.FixedRateLeg
    face_values = []
    fv_initial = 10_000_000.00
    step = 0.00
    fv_step_size = 200_000.00
    for i in range(1, len(schedule)):
        face_values.append(fv_initial + step)
        step += fv_step_size
    
    index, engine = sample_index(setting)
    loanleg = ql.IborLeg(face_values, 
                schedule, 
                index, 
                ql.Actual360(), 
                ql.ModifiedFollowing, 
                fixingDays=[0])

    return loanleg


def callable_bondinfo():
    bondsetting = {
        "frequency":Frequency.semi_annual,
        "start_basis": StartBasis.today,
        "day_count": DayCount.act_act_isma,
        "business_day": BusinessDay.no_adjustment,
        "terminate_business_day": BusinessDay.no_adjustment,
        "date_gen": DateGeneration.backward,
        "is_eom":  True
        }

    setting = BondSetting(**bondsetting)

    bonddata = {"issue_date": "2021-08-18", 
                "maturity": "2031-08-18", 
                "settings": setting, 
                "coupon": 5.00,
                "face_value": 10_000_000
                }
    thebond = FixedRateBond(**bonddata)

    return thebond, setting


def curve_with_spread(value_date: str):
    vdate = datestr_to_qldate(value_date) 
    calendar = ql.WeekendsOnly()
    rates, depo_setting, parrates, par_setting = sample_curveinfo()
    t_structure = curve_piecewise(value_date, 
                                depo_setting, 
                                rates,
                                par_setting, 
                                parrates)
    curve_handle = ql.YieldTermStructureHandle(t_structure)
    spreads = sample_spreadinfo()
    spread_handles = []
    spread_dates = []
    spread_quotes = []

    for spread in spreads:
        spread_quote = ql.SimpleQuote(spread.rate/100)
        spread_quotes.append(spread_quote)
        spread_handle = ql.QuoteHandle(spread_quote)
        spread_handles.append(spread_handle)
        maturity = calendar.advance(vdate, get_qlPeriod(spread.tenor))
        spread_dates.append(maturity)

    spread_curve = ql.SpreadedLinearZeroInterpolatedTermStructure(
                            curve_handle,
                            spread_handles,
                            spread_dates)
    spread_curve_handle = ql.YieldTermStructureHandle(spread_curve)
    return spread_curve_handle