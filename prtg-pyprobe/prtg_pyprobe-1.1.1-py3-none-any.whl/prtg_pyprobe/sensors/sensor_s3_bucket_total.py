import time

import aioboto3
import logging
from asyncio import Queue

from botocore.exceptions import ClientError

from prtg_pyprobe.sensors.helpers import SensorDefinition, SensorDefinitionGroup, SensorData
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "S3 Bucket Total"

    @property
    def kind(self) -> str:
        return "mps3buckettotal"

    @property
    def definition(self) -> dict:
        s3_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Sensor for monitoring the total amount of your S3 buckets.",
            sensor_help="This returns the total amount of buckets in your AWS account.",
            tag="mps3buckettotal",
        )
        s3_def_group = SensorDefinitionGroup(name="s3_bucket_total", caption="S3 Bucket Sensor Settings")
        s3_def_group.add_field(field_type="edit", name="aws_access_key", caption="AWS Access Key ID")
        s3_def_group.add_field(field_type="password", name="aws_secret_key", caption="AWS Secret Key")
        s3_def.add_group(s3_def_group)
        return s3_def.data

    async def work(self, task_data: dict, q: Queue) -> None:
        s3_bucket_data = SensorData(sensor_id=task_data["sensorid"])

        try:
            start = time.time()
            async with aioboto3.resource(
                "s3", aws_access_key_id=task_data["aws_access_key"], aws_secret_access_key=task_data["aws_secret_key"]
            ) as s3:
                all_buckets = s3.buckets.all()
                i = 0
                async for _ in all_buckets:
                    i += 1

                s3_bucket_data.add_channel(
                    name="Total Buckets", mode="integer", kind="Custom", customunit="buckets", value=i
                )

                s3_bucket_data.message = f"Your AWS account has {i} buckets."

                end = (time.time() - start) * 1000
                s3_bucket_data.add_channel(name="Total Query Time", mode="float", kind="TimeResponse", value=end)

        except ClientError:
            s3_bucket_data.error = "Exception"
            s3_bucket_data.error_code = 1
            s3_bucket_data.message = "S3 bucket sensor failed. See log for details"
            logging.exception("The S3 bucket sensor couldn't contact AWS properly")

        await q.put(s3_bucket_data.data)
        q.task_done()
