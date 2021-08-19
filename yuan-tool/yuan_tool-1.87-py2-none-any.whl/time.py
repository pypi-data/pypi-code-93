import time
import datetime


def time2date(timestamp=None, fmt='%Y-%m-%d %H:%M:%S'):
    """
    将时间戳转为字符串时间
    :param timestamp: 时间戳
    :param fmt: 时间格式
    :return:时间戳对应的时间:str
    """
    return time.strftime(fmt, time.localtime(timestamp))


def time2hms(secs):
    """
    做时间相关的加减操作
    e.g. time.time() + time2hms(seconds=5) 为未来5秒的时间
    """
    return str(datetime.timedelta(seconds=secs))


def date2time(date: str, fmt='%Y-%m-%d %H:%M:%S'):
    """
    字符串时间转为时间戳
    :param date: 字符串时间
    :param fmt: 时间格式
    :return: 时间戳
    """
    struct = time.strptime(date, fmt)
    return time.mktime(struct)


def curr_date():
    """获取当前时间"""
    return time2date(time.time())


def curr_date_obj():
    """返回一个datatime的对象"""
    return datetime.datetime.now().replace(microsecond=0)


if __name__ == '__main__':
    current_time = time.time()

    res = time2date(current_time)
    a = curr_date_obj()
    print(a)
