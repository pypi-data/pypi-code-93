import time

import src.MultiTool.time


def startStopwatch():
    """
    Stopwatch starts a timer
    :return:
    """
    time.time()

def wait(sec):
    """
    Waits for example 10 seconds
    :param sec: Seconds
    :type sec: int
    :return:
    """
    time.sleep(sec)

def localNormal(sec=int(None)):
    """
    returns the time
    :param sec: Seconds
    :type sec: int
    :return:
    """
    try:
        x = time.localtime(sec)
    except Exception:
        x = time.localtime(src.MultiTool.time.startStopwatch())
    x1 = ""
    if x[1] == 1: x1 = "January"
    if x[1] == 2: x1 = "Fabruary"
    if x[1] == 3: x1 = "March"
    if x[1] == 4: x1 = "April"
    if x[1] == 5: x1 = "May"
    if x[1] == 6: x1 = "June"
    if x[1] == 7: x1 = "July"
    if x[1] == 8: x1 = "August"
    if x[1] == 9: x1 = "September"
    if x[1] == 10: x1 = "October"
    if x[1] == 11: x1 = "November"
    if x[1] == 12: x1 = "December"



    return f"{x1} {x[2]} {x[3]}:{x[4]}:{x[5]} {x[0]}"

def localHard(sec):
    """
    returns the time on a hard way
    :param sec: Seconds
    :type sec: int
    :return:
    """
    x = time.localtime(sec)

    return x