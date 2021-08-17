from shyft.time_series import Calendar, UtcPeriod, time, TimeAxis, min_utctime, max_utctime, UtcTimeVector, time_axis_extract_time_points_as_utctime


def create_view_time_axis(*, cal: Calendar, view_period: UtcPeriod, clip_period: UtcPeriod, dt: time) -> TimeAxis:
    """
    This function creates a time axis with the range of the view_period, clipped to clip_period if specified,
    and snaps to its calendar resolution of dt.

    An *empty* TimeAxis() is returned if:
     - the overlap is _less than_ dt or no overlap
     - overlap period contains -oo or +oo
     - dt is zero

    For all other cases a TimeAxis is returned such that:
      dt < DAY:
        TimeAxis(t_start,dt,n)
      dt >= DAY
        TimeAxis(cal,t_start,dt,n)
      where
         t_start = cal.trim(overlap.start + dt/2,dt)
         n = UtcPeriod(t_start,cal.trim(overlap.end + dt/2,dt).diff_units(cal,dt)

    Parameters
    ----------
    cal: Calendar to use for calendar semantic trim/add if dt >= DAY
    view_period: the visual view-period
    clip_period: the clip to this period)
    dt: time step of the time axis

    Returns
    -------
    time_axis: TimeAxis
    """
    overlap = UtcPeriod.intersection(view_period, clip_period) if clip_period.valid() else view_period
    if dt <= 0 or not overlap.valid() or overlap.timespan() < dt or overlap.start == min_utctime or overlap.end == max_utctime:
        return TimeAxis()
    t_start = cal.trim(overlap.start + dt/2, dt)  # the + dt/2.0 ensure calendar rounding, as opposed to trunc/trim
    n = UtcPeriod(t_start, cal.trim(overlap.end + dt/2, dt)).diff_units(cal, dt)
    return TimeAxis(t_start, dt, n) if dt < cal.DAY else TimeAxis(cal, t_start, dt, n)


def extend_time_axis(*, ta: TimeAxis, p: UtcPeriod) -> TimeAxis:
    """
    Return an extended time-axis where .total_period() is at least
    the range of period p.
    If they are already included, return the original time-axis.
    """
    if len(ta) and p.valid() and p.start != min_utctime and p.end != min_utctime and (ta.total_period().start > p.start or ta.total_period().end < p.end):
        # OPTIMIZE: check if ta is a fixed-interval (or cal fixed -interval)
        #       then if p.start == ta.start - 1*dt, adjust t_start and n
        #       similar if p.end == ta.end + 1*dt, adjust n
        #       then return a fixed (cal) interval time-axis
        r = UtcTimeVector()
        if ta.total_period().start > p.start:
            r.append(p.start)
            r.extend(time_axis_extract_time_points_as_utctime(ta))
        else:
            r = time_axis_extract_time_points_as_utctime(ta)
        if ta.total_period().end < p.end:
            r.append(p.end)
        ta = TimeAxis(r)
    return ta


class ViewTimeAxisProperties:
    """
    At the view-level, describes the visual-wanted properties of the time-series data to be presented.
    The class have no logic, just group together properties that give a consistent view of current 'view-port'.

    The data-source can use this information to adapt it's call to the underlying TsAdapter(time-axis,unit)->tsvector
    so that it is optimal with respect to performance, as well as visualization.

    Attributes
    ----------
    dt: time-step for aggregation/average, like hour, day, week etc.
    cal: calendar for calendar semantic steps, so the time-steps dt are in multiple of dt, rounded to calendar
    view_period: the current entire view-period (usually also rounded to whole calendar/dt)
    padded_view_period: a period greater/equal to the view-period, to allow for smooth pan/scrolling
    extend_mode: if True, the data-source should ensure to include its own min/max range using the extend_time_axis method
    """

    def __init__(self, *, dt: time, cal: Calendar, view_period: UtcPeriod, padded_view_period: UtcPeriod, extend_mode:bool):
        self.dt: time = dt
        self.cal: Calendar = cal
        self.view_period: UtcPeriod = view_period
        self.padded_view_period: UtcPeriod = padded_view_period
        self.extend_mode:bool = extend_mode
