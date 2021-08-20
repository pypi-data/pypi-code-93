"""
  ===== Reference ====
  
  URL: https://docs.python.org/3/library/time.html
  
  %a -> Locale’s abbreviated weekday name.
  %A -> Locale’s full weekday name.

  %b -> Locale’s abbreviated month name.
  %B -> Locale’s full month name.

  %c -> Locale’s appropriate date and time representation.
  %d -> Day of the month as a decimal number [01,31].
  %H -> Hour (24-hour clock) as a decimal number [00,23].
  %I -> Hour (12-hour clock) as a decimal number [01,12].
  %j -> Day of the year as a decimal number [001,366].

  %m -> Month as a decimal number [01,12].
  %M -> Minute as a decimal number [00,59].

  %p -> Locale’s equivalent of either AM or PM.
  %S -> Second as a decimal number [00,61].
  %U -> Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0.

  %w -> Weekday as a decimal number [0(Sunday),6].
  %W -> Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0.

  %x -> Locale’s appropriate date representation.
  %X -> Locale’s appropriate time representation.

  %y -> Year without century as a decimal number [00,99].
  %Y -> Year with century as a decimal number.

  %z -> Time zone offset indicating a positive or negative time difference from UTC/GMT of the form +HHMM or -HHMM, where H represents decimal hour digits and M represents decimal minute digits [-23:59, +23:59].
  %Z -> Time zone name (no characters if no time zone exists).

  %% -> A literal '%' character.

"""

import time
import datetime
import math


LOCAL_TIMEZONE            = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
LOCAL_TIMEZONE_OFFSET     = - time.timezone
DEFAULT_TIMESTAMP_FORMAT  = "%Y-%m-%d %H:%M:%S"
ISO_TIMESTAMP_FORMAT      = "%Y-%m-%dT%H:%M:%S"




def get_timestamp(fmt=DEFAULT_TIMESTAMP_FORMAT, epoch_time = None, iso_format=False , timezone=LOCAL_TIMEZONE) :
  assert timezone==LOCAL_TIMEZONE or  timezone=="UTC", "Only support UTC or local timezone"
  if epoch_time is not None : 
    digits = int(math.log10(epoch_time))+1
    if digits > 10 :  epoch_time = int(str(epoch_time)[:10])
  else:
    epoch_time = time.time()

  if timezone == "UTC" :
    time_struct = 	time.gmtime(epoch_time)
  else:
    time_struct = 	time.localtime(epoch_time)
  
  if iso_format :
    fmt = ISO_TIMESTAMP_FORMAT
    
  return  (time.strftime(fmt, time_struct))


def parse_timestamp(ts_str, fmt=DEFAULT_TIMESTAMP_FORMAT, timezone=LOCAL_TIMEZONE):
  # timezone is the timezone of input ts_str, NOT the output
  time_struct   = time.strptime(ts_str, fmt)
  epoc_time     = time.mktime(time_struct)
  
  if timezone == "UTC" :
    epoc_time = epoc_time + LOCAL_TIMEZONE_OFFSET
    
  return int(epoc_time)



def timer_start():
  start = time.time()
  return (start)  
  
def timer_check(start):
  return(time.time() - start)   


def readable_duration(seconds):
  day = seconds // (24 * 3600)
  seconds %= (24 * 3600)
  
  hour = seconds // 3600
  seconds %= 3600
  
  minutes = seconds // 60
  seconds %= 60
  
  return(day, hour, minutes, seconds)

def cal_ts_diff(ts1=None, ts2=None):
  assert ts1 is None or type(ts1).__name__ == "int", 'Timestamp ts1 needs to be in epoch seconds.'
  assert ts2 is None or type(ts2).__name__ == "int", 'Timestamp ts1 needs to be in epoch seconds.'
  
  if ts1 is None:   ts1 = time.time()
  if ts2 is None:   ts2 = time.time()

  
  return ts2 - ts1




if __name__ == "__main__":
  #print (get_timestamp(fmt=DEFAULT_TIMESTAMP_FORMAT, epoch_time=1579046194))
  #print (get_epoch(get_timestamp()))
  #print (time.time())
  
  #print (parse_ts_str('2020-07-02T02:57:24.331Z'))
  #print (parse_ts_str(ts_str='2020-07-02T02:57:24.331Z', fmt="%Y-%m-%dT%H:%M:%S.%fZ"))
  #dt1= parse_ts_str(ts_str='2020-07-02T02:57:24.331Z', fmt="%Y-%m-%dT%H:%M:%S.%fZ")
  
  #print (cal_days_diff(dt1='2020-07-02T02:57:24.331Z',fmt="%Y-%m-%dT%H:%M:%S.%fZ")) 
  
  
  
  #LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone()
  #print (LOCAL_TIMEZONE)
  #LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo
  #print (LOCAL_TIMEZONE)
  
  #ts = '2020-07-02T02:57:24.331Z'
  #print (time.time())
  #print (get_timestamp())
  #print (get_timestamp(timezone="UTC"))
  
  #print(parse_timestamp(ts_str=ts, fmt="%Y-%m-%dT%H:%M:%S.%fZ", timezone="UTC"))

  #print (cal_ts_diff(ts2=parse_timestamp(ts_str=ts, fmt="%Y-%m-%dT%H:%M:%S.%fZ", timezone="UTC")))
  print (readable_duration(120202))
  pass
  