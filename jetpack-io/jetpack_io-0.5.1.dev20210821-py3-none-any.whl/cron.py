import os
from functools import wraps

import cronitor
import schedule
from jetpack import utils
from schedule import every  # Use this to whitelist what we allow

cronjob_suffix = os.environ.get("JETPACK_CRONJOB_SUFFIX", "-missing-suffix")


def repeat(repeat_pattern):
    def wrapper(func):
        job_name = utils.qualified_func_name(func) + cronjob_suffix
        cronitor_wrapped_func = cronitor.job(job_name)(func)
        schedule.repeat(repeat_pattern)(cronitor_wrapped_func)

    return wrapper
