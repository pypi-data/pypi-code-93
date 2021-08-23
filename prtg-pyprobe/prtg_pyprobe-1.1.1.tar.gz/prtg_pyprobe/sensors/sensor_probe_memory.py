import asyncio
import logging
import platform

import psutil

from prtg_pyprobe.sensors.helpers import SensorProbeData, SensorDefinition, SensorDefinitionGroup
from prtg_pyprobe.sensors.sensor import SensorPSUtilBase


class Sensor(SensorPSUtilBase):
    @property
    def name(self) -> str:
        return "Memory (Probe)"

    @property
    def kind(self) -> str:
        return "mpprobememory"

    @property
    def definition(self) -> dict:
        probe_health_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Sensor used to monitor the memory usage of the system on which the python probe is running.",
            sensor_help="Sensor used to monitor the memory usage of the system on which the python probe is running."
            "This is always the case even if added to a different device than the Probe Device.",
            tag="mpprobememorysensor",
        )
        memory_group = SensorDefinitionGroup(name="probe_memory", caption="Probe Memory")
        probe_health_def.add_group(memory_group)
        return probe_health_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        probe_health_data = SensorProbeData(sensor_id=task_data["sensorid"])
        try:
            uname = platform.uname()
            probe_health_data.message = f"Memory usage on {uname.system}, everything OK"
            vmemory, swapmemory = self.get_memory_usage()

            probe_health_data.add_channel(name="Memory Total", mode="integer", kind="BytesMemory", value=vmemory.total)
            probe_health_data.add_channel(
                name="Memory Available",
                mode="integer",
                kind="BytesMemory",
                value=vmemory.available,
            )
            probe_health_data.add_channel(
                name="Swap Total",
                mode="integer",
                kind="BytesMemory",
                value=swapmemory.total,
            )
            probe_health_data.add_channel(name="Swap Free", mode="integer", kind="BytesMemory", value=swapmemory.free)

        except psutil.Error:
            probe_health_data.error = "Exception"
            probe_health_data.error_code = 1
            probe_health_data.message = "Probe memory check failed. See log for details"
            logging.exception("Probe memory information could not be determined")
        await q.put(probe_health_data.data)
        q.task_done()
