import QuantLib as ql
from .ql_enums import *
from .ql_utils import *
from .pymodels import *
from .ql_conventions import *


def create_fixratestructure(thebond: FixedRateBond,
                            ql_calendar ):
    setting = thebond.settings
    
    period = ql.Period(ql_freq_tenor[setting.frequency])

    schedule = qlSchedule(thebond.issue_date, 
                            thebond.maturity, 
                            period,
                            ql_calendar,
                            setting.business_day, 
                            setting.business_day,
                            setting.date_gen, 
                            eom= True)
    interests = ql.FixedRateLeg(schedule, 
                            ql_day_count[setting.day_count],
                            [thebond.face_value], 
                            [thebond.coupon/100])
    no_of_interests = len(interests)
    structures = []
    for i in range(no_of_interests):
        if i == no_of_interests - 1:
            thestructure = {"start_date": schedule[i].ISO(),
                            "end_date": interests[i].date().ISO(),
                            "face_value": thebond.face_value,
                            "coupon": thebond.coupon,
                            "face_value_flow": thebond.face_value,
                            "interest": interests[i].amount(),
                            "cashflow": thebond.face_value + interests[i].amount()} 
        else:
            thestructure = {"start_date": schedule[i].ISO(),
                            "end_date": interests[i].date().ISO(),
                            "face_value": thebond.face_value,
                            "coupon": thebond.coupon,
                            "interest": interests[i].amount(),
                            "cashflow": interests[i].amount()}
        structure = Structure(**thestructure)  
        structures.append(structure)  
    
    return structures


def testapis():
    print("TEST APIS")

    
    