from typing import Callable

from jetpack import _job
from jetpack._job.job import Job as _Job

_client = _job.Client()


class JobDecorator:
    def __call__(self, fn: Callable) -> Callable:
        _Job(fn)
        return fn

    @classmethod
    def launch(cls, qualified_name: str, module=""):
        _client.launch_job(qualified_name, module)


job = JobDecorator()
