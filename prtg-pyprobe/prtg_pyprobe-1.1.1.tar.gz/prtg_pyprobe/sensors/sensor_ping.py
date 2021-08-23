import asyncio
import ctypes
import logging
import os
import socket
import time
from statistics import mean, pstdev

import aioping

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "Ping (TCP/ICMP)"

    @property
    def kind(self) -> str:
        return "mpping"

    @property
    def definition(self) -> dict:
        ping_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors the availability of a target using TCP or ICMP",
            sensor_help="Monitors the availability of a target using TCP or ICMP",
            tag="mppingsensor",
        )
        ping_def_group_settings = SensorDefinitionGroup(name="pingsettings", caption="Ping Settings")
        ping_def_group_settings.add_field_timeout(5, 1, 300)
        ping_def_group_settings.add_field(
            field_type="integer",
            name="ping_count",
            caption="Ping Count",
            required="1",
            default=4,
            minimum=1,
            maximum=20,
            help="Enter the count of Ping requests PRTG will send to the device during an interval",
        )
        ping_def_group_settings.add_field(
            field_type="integer",
            name="target_port",
            caption="Port (TCP mode only)",
            required="1",
            default=443,
            minimum=1,
            maximum=65534,
            help="This is the port that you want to monitor if it's open or closed. Only used for TCP Ping",
        )
        ping_def_group_settings.add_field(
            field_type="radio",
            name="ping_type",
            caption="Ping Type",
            required="1",
            help="Choose your Ping type. Note that for ICMP the pyprobe must run as root!",
            options={"tcp": "TCP", "icmp": "ICMP"},
            default="tcp",
        )
        ping_def.add_group(group=ping_def_group_settings)
        return ping_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        ping_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            ping_raw_data = []
            for i in range(int(task_data["ping_count"])):
                await asyncio.sleep(0.1)
                if task_data["ping_type"] == "tcp":
                    ping_future = asyncio.open_connection(host=task_data["host"], port=task_data["target_port"])
                    start = time.time()
                    reader, writer = await asyncio.wait_for(ping_future, int(task_data["timeout"]))
                    writer.close()
                    await writer.wait_closed()
                    end = time.time()
                    time_ms = (end - start) * 1000
                    ping_raw_data.append(round(time_ms, 4))
                elif task_data["ping_type"] == "icmp":
                    if not self._is_admin():
                        raise PermissionError("The pyprobe must run as root/administrator to use ICMP Ping")
                    single_ping = await aioping.ping(
                        dest_addr=task_data["host"],
                        timeout=int(task_data["timeout"]),
                        family=socket.AddressFamily.AF_INET,
                    )
                    ping_raw_data.append(single_ping * 1000)

            ping_data.message = f"OK. Ping Mode {task_data['ping_type']}"
            ping_data.add_channel(
                name="Ping Time Min",
                mode="float",
                kind="TimeResponse",
                value=float(min(ping_raw_data)),
            )
            ping_data.add_channel(
                name="Ping Time Avg",
                mode="float",
                kind="TimeResponse",
                value=float(mean(ping_raw_data)),
            )
            ping_data.add_channel(
                name="Ping Time Max",
                mode="float",
                kind="TimeResponse",
                value=float(max(ping_raw_data)),
            )
            ping_data.add_channel(
                name="Ping Time MDEV",
                mode="float",
                kind="TimeResponse",
                value=float(pstdev(ping_raw_data)),
            )
        except ConnectionError:
            ping_data.error = "Exception"
            ping_data.error_code = 1
            ping_data.message = "Ping check failed. See log for details"
            logging.exception("There has been a connection error.")
        except asyncio.TimeoutError:
            ping_data.error = "Exception"
            ping_data.error_code = 1
            ping_data.message = "Ping Timeout. See log for details"
            logging.exception("There has been a timeout.")
        except TimeoutError:
            ping_data.error = "Exception"
            ping_data.error_code = 1
            ping_data.message = "Ping Timeout. See log for details"
            logging.exception("There has been a timeout.")
        except socket.gaierror:
            ping_data.error = "Exception"
            ping_data.error_code = 1
            ping_data.message = "Ping check failed. See log for details"
            logging.exception("There has been a connection error.")
        except PermissionError:
            ping_data.error = "Exception"
            ping_data.error_code = 1
            ping_data.message = "The pyprobe must run as root/administrator to use ICMP Ping"
            logging.exception("ICMP Ping uses RAW sockets. You must be root to use them.")
        except OSError:
            ping_data.error = "Exception"
            ping_data.error_code = 1
            ping_data.message = "Target device/port probably not available."
            logging.exception(
                "Something on the network level went wrong. " "Target host not reachable on selected port."
            )
        await q.put(ping_data.data)
        q.task_done()

    @staticmethod
    def _is_admin():
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return is_admin
