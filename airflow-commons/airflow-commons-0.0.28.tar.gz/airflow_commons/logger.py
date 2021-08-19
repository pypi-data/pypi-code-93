import pytz
import datetime as dt

LEVELS = {1: "ERROR", 2: "WARN", 3: "INFO"}


def LOGGER(message, level=3):
    """
    simple logger

    :param message: log statement
    :param level: level of the log
    :return:
    """
    curr_time = dt.datetime.now(pytz.timezone("Europe/Moscow")).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    print(LEVELS[level] + " - [" + curr_time + "] -", message)
