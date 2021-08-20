import mylogging
import warnings


def warn_outside(message):
    mylogging.warn(message)


def traceback_outside(message):
    try:
        print(10 / 0)
    except Exception:
        mylogging.traceback(message)


def info_outside(message):
    mylogging.info(message)


def warn_to_be_filtered():
    warnings.warn("It mean of empty slice it is")
