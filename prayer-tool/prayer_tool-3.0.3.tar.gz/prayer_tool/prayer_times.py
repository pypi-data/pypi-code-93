"""This is where the magic happens ;). The main file."""
from datetime import time
from datetime import datetime
import requests

##Declaring needed variables
URL_TODAY = "https://api.pray.zone/v2/times/today.json"
URL_THIS_MONTH = "https://api.pray.zone/v2/times/this_month.json"

class Prayer:
    """Individual prayer object"""
    def __init__(self, name, time):
        self.name = name
        self.time = time

class Day:
    """Day object, list of Prayer objects"""
    def __init__(self, fajr, dhor, asr, maghreb, icha, date):
        self.fajr = Prayer("fajr", fajr)
        self.dhor = Prayer("dhor", dhor)
        self.asr = Prayer("asr", asr)
        self.maghreb = Prayer("maghreb", maghreb)
        self.icha = Prayer("icha", icha)
        self.date = date
    
    def to_string(self):
        """Returns a string to show the daily prayers"""
        string = f"Date : {self.date} \n{self.fajr.name} : {self.fajr.time}",
        f" \n{self.fajr.name} : {self.dhor.time} \n{self.fajr.name} : {self.asr.time}\n",
        f"{self.fajr.name} : {self.maghreb.time} \n{self.fajr.name} : {self.icha.time}"
        return string

    def next_prayer(self):
        """Returns an object of the next prayer, based on current time of the system"""
        time = datetime.now().time()
        if time <= self.fajr.time:
            return self.fajr
        elif time <= self.dhor.time:
            return self.dhor
        elif time <= self.asr.time:
            return self.asr
        elif time <= self.maghreb.time:
            return self.maghreb
        elif time <= self.icha.time:
            return self.icha
        else:
            return None

def request_builder(city, school, juristic, timeformat, url):
    """Creates the request with correct url and parameters"""
    params = {'city': city, 'school': school, 'juristic':juristic, 'timeformat': timeformat}
    request = requests.get(url = url, params=params)
    return request

def format_time(temp_salat):
    """Format string hours to time object"""
    (hour, minut) = temp_salat.split(':')
    salat = time(hour=int(hour), minute=int(minut))
    return salat

def get_today_prayer(request):
    """Returns today prayer"""
    data = request.json()
    times = data["results"]["datetime"][0]["times"]
    dates = data["results"]["datetime"][0]["date"]["gregorian"]
    return parse_day_prayer(times, dates)

def string_to_date(date_str):
    """Parse date string in date object"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj

def parse_day_prayer(day_object, dates):
    """Returns a Day object with given parameters"""
    day_date = string_to_date(dates)
    prayer = Day(format_time(day_object["Fajr"]), format_time(day_object["Dhuhr"]),
        format_time(day_object["Asr"]), format_time(day_object["Maghrib"]),
        format_time(day_object["Isha"]), day_date)
    return prayer

def get_month_prayer(request):
    """Returns a list of the monthly prayers as a list of days"""
    month_list = []
    data = request.json()
    month = data["results"]["datetime"]
    for day in month:
        month_list.append(parse_day_prayer(day["times"], day["date"]["gregorian"]))
    return month_list

class PrayerTimes:
    """Prayer times API implementation class

    You have to create an instance of Prayer_times to use this API. For more information : https://pypi.org/project/prayer-tool/

    :param CITY: The city from where you need the calendar.
                         For example ``Brussels``
    :type service_urls: string

    :param SCHOOL: Every school have a different calculation, we use 3 by default (Muslim World League).
                         For example 3
    :type SCHOOL: int

    :param JURISTIC: 0 for Shafii (or the standard way), 1 for Hanafi. If you leave this empty, it defaults to Shafii.
                         For example 0
    :type JURISTIC: int
    """
    def __init__(self,city="Brussels", school=3, juristic=0):
        self.city = city
        self.school = school
        self.juristic = juristic
        self.timeformat = 0

    def today(self):
        """returns today prayer"""
        request = request_builder(self.city, self.school, self.juristic, self.timeformat, URL_TODAY)
        return get_today_prayer(request)

    def this_month(self):
        """returns prayer list of whole month"""
        request = request_builder(self.city, self.school, self.juristic, self.timeformat, URL_THIS_MONTH)
        return get_month_prayer(request)
