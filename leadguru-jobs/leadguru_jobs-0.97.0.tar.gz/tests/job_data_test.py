import json
import unittest
from datetime import datetime

import pydantic

from lgt_jobs import SimpleTestJob, BackgroundJobRunner, BaseBackgroundJob
from lgt_jobs.runner import datetime_converter


class JobDataTest(unittest.TestCase):
    def test_can_run_simple_job(self):
        job_type = SimpleTestJob
        data = { "name": "Kiryl", "id": 123 }

        job = job_type()
        result = job.run(data)

        self.assertEqual(f"id=123;name=Kiryl", result)

    def test_can_run_serialized_job(self):
        job_type = SimpleTestJob
        data = {"name": "Kiryl", "id": 123}

        json_data = json.dumps(BaseBackgroundJob.dumps(job_type, data))

        result = BackgroundJobRunner.run({
            "SimpleTestJob": SimpleTestJob
        }, json.loads(json_data))

        self.assertEqual(f"id=123;name=Kiryl", result)

    def test_dump_time(self):
        now = datetime.now()
        class TestModel(pydantic.BaseModel):
            time: datetime

        model = TestModel(time=now)

        json_str = json.dumps(model.dict(), ensure_ascii=False, default=datetime_converter)
        model = TestModel(**json.loads(json_str))

        self.assertEqual(model.time, now)
