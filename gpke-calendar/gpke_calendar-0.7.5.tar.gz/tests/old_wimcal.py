from datetime import date
""" This data was generated from the GPKE Calendar.
    Every date in the middle of a tuple represents one day, and the two
    tuples surrounding it are each 9 workdays into the future rspcly. past.
    To generate new tuples for the upcoming year you need to go through 
    a few steps.
    1. Find newest GPKE Calendar.
    2. Convert GPKE Calendar to XLS with tool of choice.
    3. Hand curate the resulting XLS to give you a column that contains
       a TRUE for all workdays and FALSE for weekend and holiday.
    4. Write a small script that iterates over each day and counta up
       and down based on that boolean column.

    Alternatively: Write GPKE for machine readable version :)
"""
dateList = [
    (date(2018, 9, 11), date(2018, 9, 24), date(2018, 10, 8)),
    (date(2018, 9, 12), date(2018, 9, 25), date(2018, 10, 9)),
    (date(2018, 9, 13), date(2018, 9, 26), date(2018, 10, 10)),
    (date(2018, 9, 14), date(2018, 9, 27), date(2018, 10, 11)),
    (date(2018, 9, 17), date(2018, 9, 28), date(2018, 10, 12)),
    (date(2018, 9, 18), date(2018, 9, 29), date(2018, 10, 12)),
    (date(2018, 9, 18), date(2018, 9, 30), date(2018, 10, 12)),
    (date(2018, 9, 18), date(2018, 10, 1), date(2018, 10, 15)),
    (date(2018, 9, 19), date(2018, 10, 2), date(2018, 10, 16)),
    (date(2018, 9, 20), date(2018, 10, 3), date(2018, 10, 16)),
    (date(2018, 9, 20), date(2018, 10, 4), date(2018, 10, 17)),
    (date(2018, 9, 21), date(2018, 10, 5), date(2018, 10, 18)),
    (date(2018, 9, 24), date(2018, 10, 6), date(2018, 10, 18)),
    (date(2018, 9, 24), date(2018, 10, 7), date(2018, 10, 18)),
    (date(2018, 9, 24), date(2018, 10, 8), date(2018, 10, 19)),
    (date(2018, 9, 25), date(2018, 10, 9), date(2018, 10, 22)),
    (date(2018, 9, 26), date(2018, 10, 10), date(2018, 10, 23)),
    (date(2018, 9, 27), date(2018, 10, 11), date(2018, 10, 24)),
    (date(2018, 9, 28), date(2018, 10, 12), date(2018, 10, 25)),
    (date(2018, 10, 1), date(2018, 10, 13), date(2018, 10, 25)),
    (date(2018, 10, 1), date(2018, 10, 14), date(2018, 10, 25)),
    (date(2018, 10, 1), date(2018, 10, 15), date(2018, 10, 26)),
    (date(2018, 10, 2), date(2018, 10, 16), date(2018, 10, 29)),
    (date(2018, 10, 4), date(2018, 10, 17), date(2018, 10, 30)),
    (date(2018, 10, 5), date(2018, 10, 18), date(2018, 11, 2)),
    (date(2018, 10, 8), date(2018, 10, 19), date(2018, 11, 5)),
    (date(2018, 10, 9), date(2018, 10, 20), date(2018, 11, 5)),
    (date(2018, 10, 9), date(2018, 10, 21), date(2018, 11, 5)),
    (date(2018, 10, 9), date(2018, 10, 22), date(2018, 11, 6)),
    (date(2018, 10, 10), date(2018, 10, 23), date(2018, 11, 7)),
    (date(2018, 10, 11), date(2018, 10, 24), date(2018, 11, 8)),
    (date(2018, 10, 12), date(2018, 10, 25), date(2018, 11, 9)),
    (date(2018, 10, 15), date(2018, 10, 26), date(2018, 11, 12)),
    (date(2018, 10, 16), date(2018, 10, 27), date(2018, 11, 12)),
    (date(2018, 10, 16), date(2018, 10, 28), date(2018, 11, 12)),
    (date(2018, 10, 16), date(2018, 10, 29), date(2018, 11, 13)),
    (date(2018, 10, 17), date(2018, 10, 30), date(2018, 11, 14)),
    (date(2018, 10, 18), date(2018, 10, 31), date(2018, 11, 14)),
    (date(2018, 10, 18), date(2018, 11, 1), date(2018, 11, 14)),
    (date(2018, 10, 18), date(2018, 11, 2), date(2018, 11, 15)),
    (date(2018, 10, 19), date(2018, 11, 3), date(2018, 11, 15)),
    (date(2018, 10, 19), date(2018, 11, 4), date(2018, 11, 15)),
    (date(2018, 10, 19), date(2018, 11, 5), date(2018, 11, 16)),
    (date(2018, 10, 22), date(2018, 11, 6), date(2018, 11, 19)),
    (date(2018, 10, 23), date(2018, 11, 7), date(2018, 11, 20)),
    (date(2018, 10, 24), date(2018, 11, 8), date(2018, 11, 22)),
    (date(2018, 10, 25), date(2018, 11, 9), date(2018, 11, 23)),
    (date(2018, 10, 26), date(2018, 11, 10), date(2018, 11, 23)),
    (date(2018, 10, 26), date(2018, 11, 11), date(2018, 11, 23)),
    (date(2018, 10, 26), date(2018, 11, 12), date(2018, 11, 26)),
    (date(2018, 10, 29), date(2018, 11, 13), date(2018, 11, 27)),
    (date(2018, 10, 30), date(2018, 11, 14), date(2018, 11, 28)),
    (date(2018, 11, 2), date(2018, 11, 15), date(2018, 11, 29)),
    (date(2018, 11, 5), date(2018, 11, 16), date(2018, 11, 30)),
    (date(2018, 11, 6), date(2018, 11, 17), date(2018, 11, 30)),
    (date(2018, 11, 6), date(2018, 11, 18), date(2018, 11, 30)),
    (date(2018, 11, 6), date(2018, 11, 19), date(2018, 12, 3)),
    (date(2018, 11, 7), date(2018, 11, 20), date(2018, 12, 4)),
    (date(2018, 11, 8), date(2018, 11, 21), date(2018, 12, 4)),
    (date(2018, 11, 8), date(2018, 11, 22), date(2018, 12, 5)),
    (date(2018, 11, 9), date(2018, 11, 23), date(2018, 12, 6)),
    (date(2018, 11, 12), date(2018, 11, 24), date(2018, 12, 6)),
    (date(2018, 11, 12), date(2018, 11, 25), date(2018, 12, 6)),
    (date(2018, 11, 12), date(2018, 11, 26), date(2018, 12, 7)),
    (date(2018, 11, 13), date(2018, 11, 27), date(2018, 12, 10)),
    (date(2018, 11, 14), date(2018, 11, 28), date(2018, 12, 11)),
    (date(2018, 11, 15), date(2018, 11, 29), date(2018, 12, 12)),
    (date(2018, 11, 16), date(2018, 11, 30), date(2018, 12, 13)),
    (date(2018, 11, 19), date(2018, 12, 1), date(2018, 12, 13)),
    (date(2018, 11, 19), date(2018, 12, 2), date(2018, 12, 13)),
    (date(2018, 11, 19), date(2018, 12, 3), date(2018, 12, 14)),
    (date(2018, 11, 20), date(2018, 12, 4), date(2018, 12, 17)),
    (date(2018, 11, 22), date(2018, 12, 5), date(2018, 12, 18)),
    (date(2018, 11, 23), date(2018, 12, 6), date(2018, 12, 19)),
    (date(2018, 11, 26), date(2018, 12, 7), date(2018, 12, 20)),
    (date(2018, 11, 27), date(2018, 12, 8), date(2018, 12, 20)),
    (date(2018, 11, 27), date(2018, 12, 9), date(2018, 12, 20)),
    (date(2018, 11, 27), date(2018, 12, 10), date(2018, 12, 21)),
    (date(2018, 11, 28), date(2018, 12, 11), date(2018, 12, 27)),
    (date(2018, 11, 29), date(2018, 12, 12), date(2018, 12, 28))
]

plus9_plus18 = {e: (m, l) for e, m, l in dateList}
minus9_plus9 = {m: (e, l) for e, m, l in dateList}
