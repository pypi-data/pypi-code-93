#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import QuantLib as ql

"""
Created on Tue Jul  18 17:33:15 2021

@author: RMS671214
"""

ql_day_count = {
    'Actual/365 Fixed': ql.Actual365Fixed(), 
    'Actual/365 Fixed (Canadian)': ql.Actual365Fixed(ql.Actual365Fixed.Canadian), 
    'Actual/365 Fixed (No Leap)': ql.Actual365Fixed(ql.Actual365Fixed.NoLeap),
    'Actual/360': ql.Actual360(),
    'Actual/Actual': ql.ActualActual(),
    'Actual/Actual (ISMA)':ql.ActualActual(ql.ActualActual.ISMA),
    'Actual/Actual (Bond)':ql.ActualActual(ql.ActualActual.Bond),
    'Actual/Actual (ISDA)':ql.ActualActual(ql.ActualActual.ISDA),
    'Actual/Actual (Historical)':ql.ActualActual(ql.ActualActual.Historical),
    'Actual/Actual (Actual365)':ql.ActualActual(ql.ActualActual.Actual365),
    'Actual/Actual (AFB)':ql.ActualActual(ql.ActualActual.AFB),
    'Business252':ql.Business252(),
    'Thirty360': ql.Thirty360()
}  

ql_business_day = {
    "No Adjustment": ql.Unadjusted, 
    "Following": ql.Following, 
    "Modified Following": ql.ModifiedFollowing,
    "Preceding": ql.Preceding, 
    "Modified Preceding": ql.ModifiedPreceding
}

ql_date_generation = {
    "Forward from issue date": ql.DateGeneration.Forward,
    "Backward from maturity date": ql.DateGeneration.Backward,
    "Zero": ql.DateGeneration.Zero,
    "ThirdWednesday": ql.DateGeneration.ThirdWednesday,
    "Twentieth": ql.DateGeneration.Twentieth,
    "TwentiethIMM": ql.DateGeneration.TwentiethIMM,
    "CDS": ql.DateGeneration.CDS,
}

ql_frequency = {
    "No Frequency": ql.NoFrequency,
    "Once": ql.Once,
    "Annual": ql.Annual, 
    "Semi-Annual": ql.Semiannual, 
    "Every Four Months": ql.EveryFourthMonth,
    "Quarterly": ql.Quarterly,
    "Bi-Monthly": ql.Bimonthly,
    "Monthly": ql.Monthly,
    "Every Fourth Week": ql.EveryFourthWeek,
    "Bi-Weekly": ql.Biweekly,
    "Weekly": ql.Weekly,
    "Daily": ql.Daily
}

ql_freq_tenor = {
    "Annual": "1Y",
    "Semi-Annual": "6M",
    "Every Four Months": "4M",
    "Quarterly": "3M",
    "Bi-Monthly": "2M",
    "Monthly": "1M",
    "Every Fourth Week": "4W",
    "Bi-Weekly": "2W",
    "Weekly": "1W",
    "Daily": "1D"
}

ql_tenor = {
    "M": ql.Months,
    "Y": ql.Years,
    "W": ql.Weeks,
    "D": ql.Days
}

ql_compounding = {
    "Simple": ql.Simple,
    "Compounded": ql.Compounded,
    "Continuous": ql.Continuous,
    "SimpleThenCompounded": ql.SimpleThenCompounded,
    "CompoundedThenSimple": ql.CompoundedThenSimple
}

ql_calendar_market = {
    "Argentina": ql.Argentina(),
    "Argentina (Merval)": ql.Argentina(ql.Argentina.Merval),
    "Brazil" : ql.Brazil(),
    "Brazil (Exchange)" : ql.Brazil(ql.Brazil.Exchange),
    "Brazil (Settlement)" : ql.Brazil(ql.Brazil.Settlement),
    "Canada": ql.Canada(),
    "Canada (Settlement)": ql.Canada(ql.Canada.Settlement),
    "Canada (TSX)": ql.Canada(ql.Canada.TSX),
    "China": ql.China(),
    "China (IB)": ql.China(ql.China.IB),
    "China (SSE)": ql.China(ql.China.SSE),
    "Czech Republic" : ql.CzechRepublic(),
    "Czech Republic (PSE)" : ql.CzechRepublic(ql.CzechRepublic.PSE),
    "France" : ql.France(),
    "France (Exchange)" : ql.France(ql.France.Exchange),
    "France (Settlement)" : ql.France(ql.France.Settlement),
    "Germany" : ql.Germany(),
    "Germany (Eurex)": ql.Germany(ql.Germany.Eurex),
    "Germany (FrankfurtStockExchange)": ql.Germany(ql.Germany.FrankfurtStockExchange), 
    "Germany (Settlement)": ql.Germany(ql.Germany.Settlement),
    "Germany (Xetra)": ql.Germany(ql.Germany.Xetra),
    "Hong Kong": ql.HongKong(),
    "Hong Kong (HKEx)": ql.HongKong(ql.HongKong.HKEx),
    "Iceland": ql.Iceland(),
    "Iceland (ICEX)" : ql.Iceland(ql.Iceland.ICEX),
    "India" : ql.India(),
    "India (NSE)": ql.India(ql.India.NSE),
    "Indonesia" : ql.Indonesia(),
    "Indonesia (BEJ)": ql.Indonesia(ql.Indonesia.BEJ),
    "Indonesia (JSX)": ql.Indonesia(ql.Indonesia.JSX),
    "Israel": ql.Israel(),
    "Israel (Settlement)": ql.Israel(ql.Israel.Settlement),
    "Israel (TASE)": ql.Israel(ql.Israel.TASE),
    "Italy": ql.Italy(),
    "Italy (Exchange)": ql.Italy(ql.Italy.Exchange),
    "Italy (Settlement)": ql.Italy(ql.Italy.Settlement),
    "Mexico": ql.Mexico(),
    "Mexico (BMV)": ql.Mexico(ql.Mexico.BMV),
    "Russia": ql.Russia(),
    "Russia (MOEX)": ql.Russia(ql.Russia.MOEX),
    "Russia (Settlement)": ql.Russia(ql.Russia.Settlement),
    "Saudi Arabia": ql.SaudiArabia(),
    "Saudi Arabia (Tadawul)": ql.SaudiArabia(ql.SaudiArabia.Tadawul),
    "Singapore": ql.Singapore(),
    "Singapore (SGX)": ql.Singapore(ql.Singapore.SGX),
    "Slovakia": ql.Slovakia(),
    "Slovakia (BSSE)": ql.Slovakia(ql.Slovakia.BSSE),
    "South Korea": ql.SouthKorea(),
    "South Korea (KRX)": ql.SouthKorea(ql.SouthKorea.KRX),
    "South Korea (Settlement)": ql.SouthKorea(ql.SouthKorea.Settlement),
    "Taiwan": ql.Taiwan(),
    "Taiwan (TSEC)": ql.Taiwan(ql.Taiwan.TSEC),
    "Ukraine" : ql.Ukraine(),
    "Ukraine (USE)": ql.Ukraine(ql.Ukraine.USE),
    "United Kingdom" : ql.UnitedKingdom(),
    "United Kingdom (Exchange)": ql.UnitedKingdom(ql.UnitedKingdom.Exchange),
    "United Kingdom (Metals)": ql.UnitedKingdom(ql.UnitedKingdom.Metals),
    "United Kingdom (Settlement)": ql.UnitedKingdom(ql.UnitedKingdom.Settlement),
    "United States": ql.UnitedStates(),
    "United States (FederalReserve)": ql.UnitedStates(ql.UnitedStates.FederalReserve),
    "United States (GovernmentBond)": ql.UnitedStates(ql.UnitedStates.GovernmentBond),
    "United States (LiborImpact)": ql.UnitedStates(ql.UnitedStates.LiborImpact),
    "United States (NREC)": ql.UnitedStates(ql.UnitedStates.NERC),
    "United States (NYSE)": ql.UnitedStates(ql.UnitedStates.NYSE),
    "United States (Settlement)": ql.UnitedStates(ql.UnitedStates.Settlement) ,
    "TARGET": ql.TARGET(),
    "WeekendsOnly": ql.WeekendsOnly(),
    "NullCalendar": ql.NullCalendar()
}

ql_start_basis = { "Today": 0, "Tom": 1, "Spot": 2}


irmodels = ['Vasicek', 'BlackKarasinski', 'HullWWhite', "gsr", 'g2']


