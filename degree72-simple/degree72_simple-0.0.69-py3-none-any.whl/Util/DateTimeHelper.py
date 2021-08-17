from threading import Timer
from requests.exceptions import Timeout
import sys
import datetime
import time

try:
    import thread
except ImportError:
    # for py3
    import _thread as thread


class OUT_TIME(object):
    req_timeout = 30

    @property
    def out_time(self):
        return self.req_timeout

    @out_time.setter
    def out_time(self, timeout):
        self.req_timeout = timeout


def accident_protected(PType):
    def warps(func):
        def deco(*args, **kwargs):
            result = None
            try:
                result = func(*args, **kwargs)
            except PType:
                import traceback
                print("Error in protected")
                print(traceback.format_exc())
            finally:
                return result

        return deco

    return warps


def time_out(interval):
    def wraps(func):
        def quite_function(fn_name):
            # print('{0} took too long'.format(fn_name), sys.stderr)
            thread.interrupt_main()  # raises KeyboardInterrupt

        def deco(*args, **kwargs):
            outer = interval.out_time
            timer = Timer(outer, quite_function, args=(func.__name__,))
            timer.start()
            try:
                resp = func(*args, **kwargs)
            except KeyboardInterrupt:
                raise Timeout("Request time out, max time:[%ss]" % outer)
            finally:
                timer.cancel()
            return resp

        return deco

    return wraps


standard_format_str = "%Y-%m-%d %H:%M:%S"


def add_days(run_date, days):
    new_date = run_date + datetime.timedelta(days=days)
    return new_date


def timestamp_to_datetime(timestamp):
    time_local = time.localtime(timestamp)
    dt = time.strftime(standard_format_str, time_local)
    return dt


def datetime_to_timestamp(date_time):
    return time.mktime(date_time.timetuple())


def string_to_datetime(string, format_str):
    try:
        return datetime.datetime.strptime(string, format_str)
    except Exception:
        return None


def date_format(date, format_str):
    return date.strftime(format_str)


def now():
    t = datetime.datetime.now()
    st = date_format(t, standard_format_str)
    r = datetime.datetime.strptime(st, standard_format_str)

    return r


def time_see(func):
    def deco(*args, **kwargs):
        b = time.time()
        result = func(*args, **kwargs)
        a = time.time()

        utime = round(a - b, 3)
        print("----Use: %ss" % utime)
        return result

    return deco


def loop_through_date_range(start_date, end_date, step=1):
    delta = end_date - start_date  # as timedelta
    days = []
    for i in range(delta.days + step):
        day = start_date + datetime.timedelta(days=i)
        days.append(day)

    return days

if __name__ == '__main__':
    start_date = datetime.datetime(2020, 1, 2)
    end_date = datetime.datetime(2020, 3, 2)
    print(loop_through_date_range(start_date, end_date))
