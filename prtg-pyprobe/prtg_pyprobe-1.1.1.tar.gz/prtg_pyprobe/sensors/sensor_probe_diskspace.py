import asyncio
import logging
import platform

import psutil

from prtg_pyprobe.sensors.helpers import (
    SensorProbeData,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorPSUtilBase


class Sensor(SensorPSUtilBase):
    @property
    def name(self) -> str:
        return "Disk Usage (Probe)"

    @property
    def kind(self) -> str:
        return "mpprobediskusage"

    @property
    def definition(self) -> dict:
        probe_health_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Sensor used to monitor the disk space usage of the Python probe.",
            sensor_help="This sensor monitors the disk space usage of the probe itself."
            "This is always the case even if added to a different device than the Probe Device.",
            tag="mpprobediskusage",
        )

        probe_health_def.add_group(self.diskspace_settings_group)
        return probe_health_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        probe_disk_data = SensorProbeData(sensor_id=task_data["sensorid"])

        try:
            uname = platform.uname()
            disk_partitions = self.get_system_partitions()
            for partition in disk_partitions:
                part_disk_usage = self.get_partition_usage(partition)
                probe_disk_data.add_disk_space_percentage_use(partition, part_disk_usage)

                if task_data["diskfull"] == "2":
                    probe_disk_data.add_disk_space_details_channel("Total", partition, part_disk_usage[0])
                    probe_disk_data.add_disk_space_details_channel("Used", partition, part_disk_usage[1])
                    probe_disk_data.add_disk_space_details_channel("Free", partition, part_disk_usage[2])

            probe_disk_data.message = f"Disk usage on {uname.system}, everything OK"

        except psutil.Error:
            probe_disk_data.error = "Exception"
            probe_disk_data.error_code = 1
            probe_disk_data.message = "Probe disk space check failed. See log for details"
            logging.exception("Probe disk space could not be determined")

        await q.put(probe_disk_data.data)
        q.task_done()
