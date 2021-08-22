from typing import Callable

import schedule


def job_name(job: schedule.Job) -> str:
    return qualified_func_name(job.job_func.func)


def qualified_func_name(func: Callable) -> str:
    return f"{func.__module__}.{func.__name__}"
