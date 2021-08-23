import asyncio
import logging
import time

from pysnmp.error import PySnmpError
from pysnmp.hlapi.asyncio import SnmpEngine, UsmUserData, CommunityData

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorSNMPBase


class Sensor(SensorSNMPBase):
    @property
    def name(self) -> str:
        return "SNMP Traffic"

    @property
    def kind(self) -> str:
        return "mpsnmptraffic"

    @property
    def definition(self) -> dict:
        snmp_traffic_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors Traffic on provided interface using SNMP",
            sensor_help="Monitors Traffic on provided interface using SNMP",
            tag="mpsnmptrafficsensor",
        )
        snmp_traffic_def_group_sensor_specific = SensorDefinitionGroup(
            name="sensor_specific", caption="Sensor Specific"
        )
        snmp_traffic_def_group_sensor_specific.add_field(
            field_type="edit",
            name="ifindex",
            caption="Interface Index (ifindex)",
            required="1",
            help="Please enter the ifIndex of the interface to be monitored.",
        )
        snmp_traffic_def.add_group(snmp_traffic_def_group_sensor_specific)
        snmp_traffic_def.add_group(self.snmp_specific_settings_group)
        return snmp_traffic_def.data

    async def work(self, task_data: dict, q: asyncio.Queue, snmp_engine: SnmpEngine):
        snmp_traffic_data = SensorData(sensor_id=task_data["sensorid"])
        creds = UsmUserData(userName=task_data["community"])
        if task_data["snmp_version"] == "0" or task_data["snmp_version"] == "1":
            creds = CommunityData(task_data["community"], mpModel=int(task_data["snmp_version"]))
        try:
            oids = [f"1.3.6.1.2.1.31.1.1.1.6.{task_data['ifindex']}", f"1.3.6.1.2.1.31.1.1.1.10.{task_data['ifindex']}"]
            if task_data["snmp_version"] == "0":
                oids = [f"1.3.6.1.2.1.2.2.1.10.{task_data['ifindex']}", f"1.3.6.1.2.1.2.2.1.16.{task_data['ifindex']}"]
            start_time = time.time()
            results = await self.get(
                target=task_data["host"],
                port=int(task_data["port"]),
                credentials=creds,
                oids=oids,
                engine=snmp_engine,
            )
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            for result in results:
                if self.cast(result[1]) == "":
                    raise PySnmpError("Returned value empty. Probably no such value/object")
            snmp_traffic_data.message = f"Interface with ifindex {task_data['ifindex']}. OK!"
            snmp_traffic_data.add_channel(
                name="Traffic In", mode="counter", unit="BytesBandwidth", value=self.cast(results[0][1])
            )
            snmp_traffic_data.add_channel(
                name="Traffic Out", mode="counter", unit="BytesBandwidth", value=self.cast(results[1][1])
            )
            snmp_traffic_data.add_channel(
                name="Traffic Total",
                mode="counter",
                unit="BytesBandwidth",
                value=self.cast(int(results[1][1]) + int(results[0][1])),
            )
            snmp_traffic_data.add_channel(
                name="Response Time",
                mode="float",
                kind="TimeResponse",
                value=float(response_time),
            )
        except PySnmpError:
            snmp_traffic_data.error = "Exception"
            snmp_traffic_data.error_code = 1
            snmp_traffic_data.message = "SNMP Query failed. See logs for details"
            logging.exception("There has been an error in PySNMP.")
        await q.put(snmp_traffic_data.data)
        q.task_done()
