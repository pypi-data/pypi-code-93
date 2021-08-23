import asyncio
import logging

import psutil

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "Traffic (Probe)"

    @property
    def kind(self) -> str:
        return "mptraffic"

    @property
    def definition(self) -> dict:
        traffic_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors traffic on the host the probe is running on.",
            sensor_help="Monitors traffic on the host the probe is running on. "
            "This is always the case even if added to a different device than the Probe Device.",
            tag="mptrafficsensor",
        )
        traffic_def_group_sensor_specific = SensorDefinitionGroup(name="sensor_specific", caption="Sensor Specific")
        traffic_def_group_sensor_specific.add_field(
            field_type="edit",
            name="iface_name",
            caption="Interface Name",
            required="1",
            help="Provide the interface name to monitor.",
        )
        traffic_def.add_group(traffic_def_group_sensor_specific)
        return traffic_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        traffic_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            traffic_data.message = f"Interface {task_data['iface_name']}"
            traffic_total = psutil.net_io_counters(pernic=True)
            iface_traffic = traffic_total[task_data["iface_name"]]
            traffic_data.add_channel(
                name="Traffic out",
                mode="counter",
                kind="BytesBandwidth",
                value=iface_traffic.bytes_sent,
            )
            traffic_data.add_channel(
                name="Traffic in",
                mode="counter",
                kind="BytesBandwidth",
                value=iface_traffic.bytes_recv,
            )
            traffic_data.add_channel(
                name="Errors in",
                mode="integer",
                kind="Custom",
                customunit="",
                value=iface_traffic.errin,
            )
            traffic_data.add_channel(
                name="Errors out",
                mode="integer",
                kind="Custom",
                customunit="",
                value=iface_traffic.errout,
            )
            traffic_data.add_channel(
                name="Dropped in",
                mode="integer",
                kind="Custom",
                customunit="",
                value=iface_traffic.dropin,
            )
            traffic_data.add_channel(
                name="Dropped out",
                mode="integer",
                kind="Custom",
                customunit="",
                value=iface_traffic.dropout,
            )
        except KeyError:
            traffic_data.error_code = 1
            traffic_data.error = "Exception"
            traffic_data.message = f"Interface {task_data['iface_name']} not found"
            logging.exception("Interface not found.")
        await q.put(traffic_data.data)
        q.task_done()
