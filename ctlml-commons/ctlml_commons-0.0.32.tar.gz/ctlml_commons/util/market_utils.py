from datetime import datetime, time, timedelta
from logging import Logger
from typing import Optional

from ctlml_commons.util.date_utils import is_holiday, is_weekend, to_est, tz_localize

PRE_MARKET_OPEN_TIME: time = time(hour=9, minute=0, second=0, microsecond=0)
OPEN_TIME: time = time(hour=9, minute=30, second=0, microsecond=0)
CLOSE_TIME: time = time(hour=16, minute=0, second=0, microsecond=0)
POST_MARKET_CLOSE_TIME: time = time(hour=18, minute=00, second=0, microsecond=0)
MARKET_CLOSING_WINDOW: int = 3


def is_market_open(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    """Is the market open?

    Args:
        a_time: current date/time
        logger: logger

    Returns: if the market time window is open, not a holiday and not a weekend
    """
    if logger:
        logger.info(
            f"is_market_open: {a_time} -> all[in_market_time_window({in_market_time_window(a_time, logger)}), "
            + f"not is_holiday({not is_holiday(a_time=a_time, logger=logger)}), "
            + f"not is_weekend({not is_weekend(a_time=a_time, logger=logger)})]"
        )
    return all([in_market_time_window(a_time=a_time), not is_holiday(a_time=a_time), not is_weekend(a_time=a_time)])


def is_extended_hours_market_open(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    """Is market extended-hours open?

    Args:
        a_time: current date/time
        logger: logger

    Returns: if the extended-hours market time window is open, not a holiday and not a weekend
    """
    if logger:
        logger.info(
            f"is_extended_hours_market_open: {a_time} ->  "
            + f"all[in_extended_hours_market_time_window({in_extended_hours_market_time_window(a_time, logger)}), "
            + f"not is_holiday({not is_holiday(a_time=a_time, logger=logger)}), "
            + f"not is_weekend({not is_weekend(a_time=a_time, logger=logger)})]"
        )

    return all(
        [
            in_extended_hours_market_time_window(a_time=a_time),
            not is_holiday(a_time=a_time),
            not is_weekend(a_time=a_time),
        ]
    )


def time_til_open(
    a_date: datetime = to_est(), extended_hours: bool = False, logger: Optional[Logger] = None
) -> timedelta:
    """How long until the market will be open?

    Args:
        a_date: a datetime
        extended_hours: determine time based on extended hours window
        logger: logger

    Returns: next time the market will be open as a time offset
    """
    if logger:
        logger.info(
            f"time_til_open: {a_date}, extended: {extended_hours} - "
            + f"time_til_extended_open({time_til_extended_open(a_date)}) -  "
            + f"time_til_regular_open({time_til_regular_open(a_date)})"
        )
    return time_til_extended_open(a_date=a_date) if extended_hours else time_til_regular_open(a_date=a_date)


def time_til_close(
    a_date: datetime = to_est(), extended_hours: bool = False, logger: Optional[Logger] = None
) -> timedelta:
    """How long until the market is closed?

    Args:
        a_date: a datetime
        extended_hours: determine time based on extended hours window
        logger: logger

    Returns: time until the market will close as a time offset
    """
    if logger:
        logger.info(
            f"time_til_close: {a_date}, extended: {extended_hours} - "
            + f"time_til_extended_close({time_til_extended_close(a_date)}) - "
            + f"time_til_regular_close({time_til_regular_close(a_date)})"
        )
    return time_til_extended_close(a_date=a_date) if extended_hours else time_til_regular_close(a_date=a_date)


def within_close_threshold(
    a_date: datetime = to_est(),
    extended_hours: bool = False,
    closing_window_mins: int = MARKET_CLOSING_WINDOW,
    logger: Optional[Logger] = None,
) -> bool:
    """Within the closing threshold of the market for the given day.

    Args:
        a_date: a datetime
        extended_hours:  determine time based on extended hours window
        closing_window_mins: closing window in minutes
        logger: logger

    Returns: if the market will close within the closing window
    """
    time_left = time_til_close(a_date=a_date, extended_hours=extended_hours)

    if logger:
        logger.info(
            f"within_close_threshold: {a_date}, extended: {extended_hours},  "
            + f"closing_window_mins: {closing_window_mins} - time_left:  "
            + f"time_til_close({time_til_close(a_date=a_date, extended_hours=extended_hours, logger=logger)}) "
            + f"time_left < closing_window_mins: {time_left < timedelta(minutes=closing_window_mins)}"
        )
    return time_left < timedelta(minutes=closing_window_mins)


# Aux methods that only care about time windows regardless of date context


def in_market_time_window(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    """Is the market open?
       Logic: Between 09:30-16:00 EST/EDT

        Args:
            a_time: a time
            logger: logger

    Returns: if in regular market hours
    """
    if logger:
        logger.info(
            f"in_market_time_window: {a_time} - not  "
            + f"any([in_pre_market_time_window({in_pre_market_time_window(a_time=a_time, logger=logger)}), "
            + f"in_post_market_time_window({in_post_market_time_window(a_time=a_time, logger=logger)})])"
        )
    return not any([in_pre_market_time_window(a_time=a_time), in_post_market_time_window(a_time=a_time)])


def in_pre_market_time_window(
    a_time: datetime = to_est(), extended_hours: bool = False, logger: Optional[Logger] = None
) -> bool:
    """If the time is in pre-market, i.e. market is closed.
       Logic: Before 09:30 EST/EDT

        Args:
            a_time: a time
            extended_hours: use extended hour start time?
            logger: logger

    Returns: if before the market is open
    """
    time_compare = PRE_MARKET_OPEN_TIME if extended_hours else OPEN_TIME

    if logger:
        logger.info(
            f"in_pre_market_time_window: {a_time}, extended: {extended_hours} - time_compare: {time_compare} "
            + f"a_time.time() {a_time.time()} < time_compare: {a_time.time() < time_compare}"
        )
    return a_time.time() < time_compare


def in_post_market_time_window(
    a_time: datetime = to_est(), extended_hours: bool = False, logger: Optional[Logger] = None
) -> bool:
    """If the time is in post-market, i.e. market is closed.
       Logic: After 16:00 EST/EDT

        Args:
            a_time: a time
            extended_hours: use extended hour end time?
            logger: logger

    Returns: if after the market is closed
    """
    time_compare = POST_MARKET_CLOSE_TIME if extended_hours else CLOSE_TIME

    if logger:
        logger.info(
            f"in_post_market_time_window: {a_time}, extended: {extended_hours} - time_compare: {time_compare} "
            + f"a_time.time() {a_time.time()} > time_compare: {a_time.time() > time_compare}"
        )
    return a_time.time() > time_compare


def in_extended_hours_market_time_window(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    """If in pre/open/post market.
       Logic: After 09:00, but before 18:00 EST/EDT

        Args:
            a_time: a time
            logger: logger

    Returns: if extended and regular hours are open
    """
    if logger:
        logger.info(
            f"in_extended_hours_market_time_window: {a_time} - any([in_pre_extended_hours_market_time_window("
            f"{in_pre_extended_hours_market_time_window(a_time=a_time, logger=logger)}), "
            f"in_post_extended_hours_market_time_window("
            f"{in_post_extended_hours_market_time_window(a_time=a_time, logger=logger)}), in_market_time_window("
            f"{in_market_time_window(a_time=a_time, logger=logger)})])"
        )
    return any(
        [
            in_pre_extended_hours_market_time_window(a_time=a_time),
            in_post_extended_hours_market_time_window(a_time=a_time),
            in_market_time_window(a_time=a_time),
        ]
    )


def in_pre_extended_hours_market_time_window(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    """If in pre-market, i.e. market is closed, but extended hours trades pre-market are available.
       Logic: After 09:00, but before 09:30 EST/EDT

        Args:
            a_time: a time
            logger: logger

    Returns: if in pre-market time
    """
    if logger:
        logger.info(
            f"in_pre_extended_hours_market_time_window: {a_time}: {PRE_MARKET_OPEN_TIME} < {a_time.time()} < "
            + f"{OPEN_TIME}"
        )
    return PRE_MARKET_OPEN_TIME < a_time.time() < OPEN_TIME


def in_post_extended_hours_market_time_window(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    """If in post-market, i.e. market is closed, but extended hours trades post-market are available.
       Logic: After 16:00, but before 18:00 EST/EDT

        Args:
            a_time: a time
            logger: logger

    Returns: if in post-market time
    """
    if logger:
        logger.info(
            f"in_post_extended_hours_market_time_window: {a_time}: {CLOSE_TIME} < {a_time.time()} < "
            + f"{POST_MARKET_CLOSE_TIME}"
        )
    return CLOSE_TIME < a_time.time() < POST_MARKET_CLOSE_TIME


def time_til_regular_close(a_date: datetime = to_est(), logger: Optional[Logger] = None) -> timedelta:
    """Time until close of regular market hours.

    Args:
        a_date: date/time
        logger: logger

    Returns: time offset until regular market close
    """
    if logger:
        logger.info(
            f"time_til_regular_close: {a_date} - if not "
            + f"is_market_open({is_market_open(a_time=a_date, logger=logger)}) then {timedelta.max}"
        )

    if not is_market_open(a_time=a_date):
        return timedelta.max

    close_time = tz_localize(datetime.combine(date=a_date.date(), time=CLOSE_TIME))
    if logger:
        logger.info(f"time_til_regular_close: {a_date} - else calc({close_time}) = {close_time - a_date}")
    return close_time - a_date


def time_til_extended_close(a_date: datetime = to_est(), logger: Optional[Logger] = None) -> timedelta:
    """Time until close of extended-trading hours.

    Args:
        a_date: date/time
        logger: logger

    Returns: time offset until extended-trading market close
    """
    if logger:
        logger.info(
            f"time_til_extended_close: {a_date} - if not "
            + f"is_extended_hours_market_open({is_extended_hours_market_open(a_time=a_date, logger=logger)}) "
            + f"then {timedelta.max}"
        )
    if not is_extended_hours_market_open(a_time=a_date):
        return timedelta.max

    close_time = tz_localize(datetime.combine(date=a_date.date(), time=POST_MARKET_CLOSE_TIME))
    if logger:
        logger.info(f"time_til_extended_close: {a_date} - else calc({close_time}) = {close_time - a_date}")

    return close_time - a_date


def time_til_regular_open(a_date: datetime = to_est(), logger: Optional[Logger] = None) -> timedelta:
    """Time until regular trading hours opens again.

    Args:
        a_date: date/time
        logger: logger

    Returns: time offset until regular market open
    """
    if logger:
        logger.info(
            f"time_til_regular_open: {a_date} - if is_market_open({is_market_open(a_time=a_date, logger=logger)}) "
            f"then {timedelta.min}"
        )
    if is_market_open(a_time=a_date):
        return timedelta.min

    # Calculate days to skip for holidays and weekends based on that start of that day
    base_date = a_date.replace(hour=0, minute=0, second=0, microsecond=0)
    if is_weekend(a_time=base_date) or is_holiday(a_time=base_date):
        while is_weekend(a_time=base_date) or is_holiday(a_time=base_date):
            base_date += timedelta(days=1)
    else:
        # If after market close, add a day
        if in_post_market_time_window(a_time=a_date):
            base_date += timedelta(days=1)

    open_time = tz_localize(datetime.combine(date=base_date.date(), time=OPEN_TIME))

    if logger:
        logger.info(f"time_til_regular_open: {a_date} - else calc({base_date}) -> {open_time} = {open_time - a_date}")

    return open_time - a_date


def time_til_extended_open(a_date: datetime = to_est(), logger: Optional[Logger] = None) -> timedelta:
    """Time until extended trading hours opens again.

    Args:
        a_date: date/time
        logger: logger

    Returns: time offset until extended-hours open
    """
    if logger:
        logger.info(
            f"time_til_extended_open: {a_date}, if "
            + f"in_extended_hours_market_time_window("
            + f"{in_extended_hours_market_time_window(a_time=a_date, logger=logger)}) -> {timedelta.min}"
        )
    if in_extended_hours_market_time_window(a_time=a_date):
        return timedelta.min

    # Calculate days to skip for holidays and weekends based on that start of that day
    base_date = a_date.replace(hour=0, minute=0, second=0, microsecond=0)
    if is_weekend(a_time=base_date) or is_holiday(a_time=base_date):
        while is_weekend(a_time=base_date) or is_holiday(a_time=base_date):
            base_date += timedelta(days=1)
    else:
        # If after extended-hours close, add a day
        if in_post_market_time_window(a_time=a_date, extended_hours=True):
            base_date += timedelta(days=1)

    open_time = tz_localize(datetime.combine(base_date.date(), PRE_MARKET_OPEN_TIME))

    if logger:
        logger.info(f"time_til_extended_open: {a_date}, else calc({base_date}) -> {open_time} = {open_time - a_date}")

    return open_time - a_date
