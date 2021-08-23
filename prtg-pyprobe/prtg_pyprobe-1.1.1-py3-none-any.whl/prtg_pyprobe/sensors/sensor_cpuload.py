import asyncio
import logging

import psutil

from prtg_pyprobe.sensors.helpers import (
    SensorProbeData,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorPSUtilBase


class Sensor(SensorPSUtilBase):
    @property
    def name(self) -> str:
        return "CPU Load (Probe)"

    @property
    def kind(self) -> str:
        return "mpcpuload"

    @property
    def definition(self) -> dict:
        cpu_load_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors CPU load avg on the system the pyprobe is running on.",
            sensor_help="Monitors CPU load avg on the system the pyprobe is running on."
            "This is always the case even if added to a different device than the Probe Device.",
            tag="mpprobehealthsensor",
        )
        return cpu_load_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        cpu_load_data = SensorProbeData(sensor_id=task_data["sensorid"])
        try:
            cpu_load = self.get_cpu_load()
            cpu_load_data.add_load_avg_channel(cpu_load[0], 1)
            cpu_load_data.add_load_avg_channel(cpu_load[1], 5)
            cpu_load_data.add_load_avg_channel(cpu_load[2], 10)
            cpu_load_data.message = "OK"
        except psutil.Error:
            cpu_load_data.error = "Exception"
            cpu_load_data.error_code = 1
            cpu_load_data.message = "CPU Load check failed. See log for details"
            logging.exception("CPU Load avg could not be determined")
        await q.put(cpu_load_data.data)
        q.task_done()
