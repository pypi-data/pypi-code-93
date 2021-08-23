import asyncio
import logging
import platform
import time

import psutil

from prtg_pyprobe.sensors.helpers import (
    SensorProbeData,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorPSUtilBase


class Sensor(SensorPSUtilBase):
    @property
    def name(self) -> str:
        return "Probe Health"

    @property
    def kind(self) -> str:
        return "mpprobehealth"

    @property
    def definition(self) -> dict:
        probe_health_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Sensor used to monitor the health of the system on which the python probe is running",
            default="yes",
            sensor_help="Sensor used to monitor the health of the system on which the python probe is running",
            tag="mpprobehealthsensor",
        )
        probe_health_def.add_group(self.temperature_settings_group)
        probe_health_def.add_group(self.diskspace_settings_group)
        return probe_health_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        probe_health_data = SensorProbeData(sensor_id=task_data["sensorid"])
        try:
            uname = platform.uname()
            probe_health_data.message = f"Running on {uname.system} in version {uname.version}! OK"
            cpu_load = psutil.getloadavg()
            vmemory, swapmemory = self.get_memory_usage()
            disk_partitions = psutil.disk_partitions()
            sys_uptime = psutil.boot_time()
            fahrenheit = False
            if task_data["celfar"] == "2":
                fahrenheit = True

            temperatures = self.get_system_temperatures(fahrenheit=fahrenheit)
            if temperatures:
                for name, entries in temperatures.items():
                    for entry in entries:
                        probe_health_data.add_temperature_channel(
                            entry.label or name, entry.current, task_data["celfar"]
                        )

            for partition in disk_partitions:
                part_disk_usage = self.get_partition_usage(partition)
                probe_health_data.add_disk_space_percentage_use(partition, part_disk_usage)

                if task_data["diskfull"] == "2":
                    probe_health_data.add_disk_space_details_channel("Total", partition, part_disk_usage[0])
                    probe_health_data.add_disk_space_details_channel("Used", partition, part_disk_usage[1])
                    probe_health_data.add_disk_space_details_channel("Free", partition, part_disk_usage[2])

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

            probe_health_data.add_load_avg_channel(cpu_load[0], 1)
            probe_health_data.add_load_avg_channel(cpu_load[1], 5)
            probe_health_data.add_load_avg_channel(cpu_load[2], 10)

            probe_health_data.add_channel(
                name="System Uptime", mode="float", kind="TimeSeconds", value=float(time.time() - sys_uptime)
            )
        except psutil.Error:
            probe_health_data.error = "Exception"
            probe_health_data.error_code = 1
            probe_health_data.message = "Probehealth check failed. See log for details"
            logging.exception("Probe health information could not be determined")
        await q.put(probe_health_data.data)
        q.task_done()
