import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import UnknownTimeZoneError, utc
import convo.shared.utils.io

__schedule_jobs = None

log = logging.getLogger(__name__)


async def schedule_jobs() -> AsyncIOScheduler:
    """Thread global scheduler to handle all recurring tasks.

    If no scheduler exists yet, this will instantiate one."""

    global __schedule_jobs

    if not __schedule_jobs:
        try:
            __schedule_jobs = AsyncIOScheduler(event_loop=asyncio.get_event_loop())
            __schedule_jobs.start()
            return __schedule_jobs
        except UnknownTimeZoneError:
            convo.shared.utils.io.raising_warning(
                "apscheduler could not find a timezone and is "
                "defaulting to utc. This is probably because "
                "your system timezone is not set. "
                'Set it with e.g. echo "Europe/Berlin" > '
                "/etc/timezone"
            )
            __schedule_jobs = AsyncIOScheduler(
                event_loop=asyncio.get_event_loop(), timezone=utc
            )
            __schedule_jobs.start()
            return __schedule_jobs
    else:
        # scheduler already created, make sure it is running on
        # the correct loop
        # noinspection PyProtectedMember
        if not __schedule_jobs._eventloop == asyncio.get_event_loop():
            raise RuntimeError(
                "Detected inconsistent loop usage. "
                "Trying to schedule a task on a new event "
                "loop, but scheduler was created with a "
                "different event loop. Make sure there "
                "is only one event loop in use and that the "
                "scheduler is running on that one."
            )
        return __schedule_jobs


def destory_scheduler() -> None:
    """Terminate the scheduler if started.

    Another call to `scheduler` will create a new scheduler."""

    global __schedule_jobs

    if __schedule_jobs:
        __schedule_jobs.shutdown()
        __schedule_jobs = None
