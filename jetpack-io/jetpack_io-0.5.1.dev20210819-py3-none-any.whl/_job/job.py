from __future__ import annotations

from typing import Callable, Dict, Optional, ValuesView

from jetpack import utils
from jetpack._remote import codec


class AlreadyExistsError(Exception):
    pass


class Job:
    jobs: Dict[str, Job] = {}

    def __init__(self, func: Callable):
        self.func = func
        Job.add_job(self)

    def name(self) -> str:
        return utils.qualified_func_name(self.func)

    def exec(self, encoded_args: str = "") -> str:
        args = []
        kwargs = {}
        if encoded_args != "":
            args, kwargs = codec.decode_args(encoded_args)
        result = self.func(*args, **kwargs)
        # for now just return encoded result, but we could send it to a redis channel
        # that the caller might be listening to.
        return codec.encode_result(result)

    @classmethod
    def add_job(cls, job: Job):
        if job.name() in cls.jobs:
            raise AlreadyExistsError(f"Job with name {job.name()} already exists")
        cls.jobs[job.name()] = job

    @classmethod
    def find_job(cls, name: str) -> Optional[Job]:
        return cls.jobs.get(name)

    @classmethod
    def defined_jobs(cls) -> ValuesView[Job]:
        return cls.jobs.values()
