from typing import List, Optional
from .pymodels import *
from .ql_conventions import *
import QuantLib as ql


def create_calendar(description: str, holidays:List[Holiday] = [], mycal = None):

    cal = ql.BespokeCalendar(description)
    qldates = [datestr_to_qldate(holiday.date) for holiday in holidays]
    for qldate in qldates:
        cal.addHoliday(qldate)
    
    if not mycal:
        calendar = ql.JointCalendar(cal, ql.WeekendsOnly())
    else:
        calendar = ql.JointCalendar(cal, mycal)
    
    return calendar
    

def datestr_to_qldate(datestr):
    vdate = datestr.split("-")
    vdt = [int(vdat) for vdat in vdate]
    return ql.Date(vdt[2], vdt[1], vdt[0])


def get_qlPeriod(tenor:str):
    prd = tenor[-1]
    number = int(tenor[:len(tenor)-1])
    return  ql.Period(number, ql_tenor[prd])


def qlSchedule(issue_date: str, 
            maturity: str, 
            period: ql.QuantLib.Period, 
            ql_calendar,
            business_day: BusinessDay, 
            maturity_business_day: BusinessDay,
            date_gen: DateGeneration, 
            eom: bool = False):
    """
    Creates list of dates. 

        Parameters:
            issue_date (str): if date_gen is DateGeneration.backward, issue_date can 
                be treated as the value date, otherwise please use issue date for 
                accurate dates.
            maturity (str): maturity of the instrument.
            frequency (str): frequency of coupon payment
            ql_calendar: ql.Calendar relevant for the currency.
            business_day (str): business day convention for the dates.
            maturity_business_day (str): business day convention for the 
                maturity of the instrument
            date_gen (str): manner in which dates are generated.
            eom (bool): if the start date is at the end of the month, whether 
                other dates are required to be scheduled at the end of the month
                (except the last date).

        Returns:
            list of ql.Dates()
    """
    vdate = datestr_to_qldate(issue_date)
    mdate = datestr_to_qldate(maturity)
    
    schedule = ql.Schedule(vdate, 
                mdate, 
                period, 
                ql_calendar, 
                ql_business_day[business_day],
                ql_business_day[maturity_business_day], 
                ql_date_generation[date_gen], 
                eom)
    return schedule


def qlMakeScedule(issue_date: str, maturity: str, frequency:str, ql_calendar = None,
                business_day: Optional[BusinessDay] = None, 
                maturity_business_day: Optional[BusinessDay] = None,
                date_gen: Optional[DateGeneration] = None, eom: bool = False):

    vdate = datestr_to_qldate(issue_date)
    mdate = datestr_to_qldate(maturity)
    freq = ql.Period(frequency)
    if business_day:
        ql_bus_day = ql_business_day[business_day]
    if maturity_business_day:
        ql_mat_bus_day = ql_business_day[maturity_business_day]
    if date_gen:
        ql_date_gen = ql_date_generation[date_gen]
    schedule = ql.MakeSchedule(vdate, mdate, freq)
    return schedule


