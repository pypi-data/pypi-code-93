import pandas as pd

def etl_calendar(start, end, columns = ['day','month','year','week','weekday','month_name','weekday_name'],
                    locale=None):
    calendar = pd.DataFrame(pd.date_range(start=start, end=end),columns=['date'])
    if 'day' in columns:
        calendar['day'] = calendar.date.dt.day
    if 'month' in columns:
        calendar['month'] = calendar.date.dt.month
    if 'year' in columns:
        calendar['year'] = calendar.date.dt.year
    if 'week' in columns:
        calendar['week'] = calendar.date.dt.week
    if 'weekday' in columns:
        calendar['weekday'] = calendar.date.dt.weekday
    if 'month_name' in columns:
        calendar['month_name'] = calendar.date.dt.month_name()
    if 'weekday_name' in columns:
        calendar['weekday_name'] = calendar.date.dt.day_name()
    return calendar