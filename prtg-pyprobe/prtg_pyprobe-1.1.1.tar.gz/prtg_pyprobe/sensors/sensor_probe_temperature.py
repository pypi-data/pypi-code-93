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
        return "Temperature (Probe)"

    @property
    def kind(self) -> str:
        return "mpprobetemperature"

    @property
    def definition(self) -> dict:
        probe_health_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Sensor used to monitor the temperature of the Python probe.",
            sensor_help="This sensor monitors the temp of the probe itself. "
            "This is always the case even if added to a different device than the Probe Device.",
            tag="mpprobetemperaturesensor",
        )

        probe_health_def.add_group(self.temperature_settings_group)
        return probe_health_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        probe_temp_data = SensorProbeData(sensor_id=task_data["sensorid"])

        try:
            uname = platform.uname()
            probe_temp_data.message = f"Temperatures on {uname.system}, everything OK"
            fahrenheit = False
            if task_data["celfar"] == "2":
                fahrenheit = True

            temperatures = self.get_system_temperatures(fahrenheit=fahrenheit)
            if temperatures:
                for name, entries in temperatures.items():
                    for entry in entries:
                        probe_temp_data.add_temperature_channel(entry.label or name, entry.current, task_data["celfar"])

            else:
                probe_temp_data.error = "Exception"
                probe_temp_data.error_code = 1
                probe_temp_data.message = (
                    "The sensor could not find temperature sensors on your probe machine." " See log for details"
                )
                logging.exception("No temperature sensors could be found by PSUtil")

        except psutil.Error:
            probe_temp_data.error = "Exception"
            probe_temp_data.error_code = 1
            probe_temp_data.message = "Probe temperature check failed. See log for details"
            logging.exception("Probe temperature could not be determined")

        await q.put(probe_temp_data.data)
        q.task_done()
