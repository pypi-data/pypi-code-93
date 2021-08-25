import datetime
from time import time

from firstimpression.constants import APIS
from firstimpression.file import update_directories_api
from firstimpression.scala import variables, Log

##################################################################################################
# LOGGING
##################################################################################################

script = 'Countdown'

info = Log('INFO', script)
debug = Log('DEBUG', script)
warn = Log('WARN', script)
error = Log('ERROR', script)

##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['countdown']

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def check_api(end_year, end_month, end_day, end_hour, end_minute, end_second):
    debug.log('folder name: {}'.format(NAME))
    update_directories_api(NAME)
    svars = variables()
    end_date = datetime.datetime(end_year,
                                 end_month,
                                 end_day,
                                 end_hour,
                                 end_minute,
                                 end_second
                                 )
    current_date = datetime.datetime.now()

    debug.log('end_date: {} - current_date: {}'.format(end_date, current_date))

    if current_date > end_date:
        warn.log('current_date is past the end date')
        svars['skipscript'] = True
    else:
        svars['skipscript'] = False
        time_delta = end_date - current_date

        debug.log('time difference in timedelta: {}'.format(time_delta))

        days_remaining = time_delta.days
        years_remaining = days_remaining//365
        days_remaining -= years_remaining * 365
        weeks_remaining = days_remaining//7
        days_remaining -= weeks_remaining * 7

        seconds_remaining = time_delta.seconds
        hours_remaining = seconds_remaining//3600
        seconds_remaining -= hours_remaining * 3600
        minutes_remaining = seconds_remaining//60
        seconds_remaining -= minutes_remaining * 60

        debug.log('years: {} - weeks: {} - days: {} - hours: {} - minutes: {} - seconds: {}'.format(years_remaining,
                  weeks_remaining, days_remaining, hours_remaining, minutes_remaining, seconds_remaining))

        svars['remaining_year'] = years_remaining
        svars['remaining_week'] = weeks_remaining
        svars['remaining_day'] = days_remaining
        svars['remaining_hour'] = hours_remaining
        svars['remaining_minute'] = minutes_remaining
        svars['remaining_second'] = seconds_remaining


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
