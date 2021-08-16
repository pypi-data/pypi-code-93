from pandas import DatetimeIndex

def create_datetime_index(start, end, delta_t):

    datetime_index = []

    t = start

    while t <= end:

        datetime_index.append(t)

        t += delta_t

    return DatetimeIndex(datetime_index)
