import json
from datetime import date, datetime
import os

import requests
from workdays import networkdays, workday

SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = "data"
excludes = ["Gründonnerstag", "Augsburger Friedensfest"]
include_always = ["12-24", "12-31"]
include_yearly = {
    2020: ["05-08"], # Einmaliger Feiertag zum 75. Jubiläum des Kriegsendes
}


def get_next_date(start: date, offset=0):
    if not start:
        raise ValueError("no date")

    holidays = get_holidays_for_year(start.year)
    return workday(start, days=offset, holidays=set(holidays))

def get_workdays_between(start: date, end: date):
    holidays = get_holidays_for_year(start.year)
    return networkdays(start, end, holidays)

def get_holidays_for_year(year):
    holidays = get_holiday_list(year-1)
    holidays.extend(get_holiday_list(year))
    holidays.extend(get_holiday_list(year + 1))
    return holidays

def get_holiday_list(year):
    if year < 2007:
        raise ValueError("date to old")

    if year > 2049:
        raise ValueError("date to new")

    rel_path = get_filename(year)
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)
    with open(abs_file_path) as json_file:
        hollyday_data = json.load(json_file)
        dates = [datetime.strptime(ve.get('datum'), '%Y-%m-%d').date() for k, v in hollyday_data.items() for ke, ve in v.items() if ke not in excludes]
        for inc_date in include_always+include_yearly.get(year, []):
            date_str = "%s-%s" % (year, inc_date)
            dates.append(datetime.strptime(date_str, '%Y-%m-%d').date())
 
        return sorted(set(dates))


def get_filename(year):
    return "{}/{}.json".format(DATA_DIR, year)


def download_json():
    for year in range(2019, 2050):
        r = requests.get('https://feiertage-api.de/api/?jahr={}'.format(year))
        json_str = json.dumps(r.json())

        with open(get_filename(year), 'w') as f:
            f.write(json_str)


if __name__ == '__main__':
    download_json()
