import asyncio
import logging
import time

from pysnmp.error import PySnmpError
from pysnmp.hlapi.asyncio import SnmpEngine, UsmUserData, CommunityData
from pysnmp.smi.error import NoSuchObjectError

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorSNMPBase


class Sensor(SensorSNMPBase):
    @property
    def name(self) -> str:
        return "SNMP Custom"

    @property
    def kind(self) -> str:
        return "mpsnmpcustom"

    @property
    def definition(self) -> dict:
        snmp_custom_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors a numerical value returned by a specific OID using SNMP",
            sensor_help="Monitors a numerical value returned by a specific OID using SNMP",
            tag="mpsnmpcustomsensor",
        )
        snmp_custom_def_group_sensor_specific = SensorDefinitionGroup(name="sensor_specific", caption="Sensor Specific")
        snmp_custom_def_group_sensor_specific.add_field(
            field_type="edit",
            name="custom_oid",
            caption="Custom OID",
            required="1",
            help="Provide an OID which is returning a numeric value",
        )
        snmp_custom_def_group_sensor_specific.add_field(
            field_type="edit",
            name="custom_unit",
            caption="Custom Unit",
            required="1",
            help="Provide an unit to be shown with the value.",
        )
        snmp_custom_def_group_sensor_specific.add_field(
            field_type="radio",
            name="value_type",
            caption="Value Type",
            required="1",
            help="Select 'Gauge' if you want to see absolute values (e.g. for temperature value) or 'Delta' for "
            "counter differences divided by time period (e.g. for bandwidth values)",
            options={"integer": "Gauge", "counter": "Delta"},
            default="integer",
        )
        snmp_custom_def.add_group(snmp_custom_def_group_sensor_specific)
        snmp_custom_def.add_group(self.snmp_specific_settings_group)
        return snmp_custom_def.data

    async def work(self, task_data: dict, q: asyncio.Queue, snmp_engine: SnmpEngine):
        snmp_custom_data = SensorData(sensor_id=task_data["sensorid"])
        creds = UsmUserData(userName=task_data["community"])
        if task_data["snmp_version"] == "0" or task_data["snmp_version"] == "1":
            creds = CommunityData(task_data["community"], mpModel=int(task_data["snmp_version"]))
        try:
            start_time = time.time()
            results = await self.get(
                target=task_data["host"],
                port=int(task_data["port"]),
                credentials=creds,
                oids=[task_data["custom_oid"]],
                engine=snmp_engine,
            )
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            for result in results:
                k, v = str(result[0]), self.cast(result[1])
                if v == "":
                    raise PySnmpError("Returned value empty. Probably no such value/object")
                snmp_custom_data.add_channel(
                    name=k,
                    mode=task_data["value_type"],
                    unit="Custom",
                    customunit=task_data["custom_unit"],
                    value=v,
                )
            snmp_custom_data.add_channel(
                name="Response Time",
                mode="float",
                kind="TimeResponse",
                value=float(response_time),
            )
            snmp_custom_data.message = "OK"
        except NoSuchObjectError:
            snmp_custom_data.error = "Exception"
            snmp_custom_data.error_code = 1
            snmp_custom_data.message = "The OID is wrong."
            logging.exception("No such object. Probably the given OID is wrong.")
        except PySnmpError:
            snmp_custom_data.error = "Exception"
            snmp_custom_data.error_code = 1
            snmp_custom_data.message = "SNMP Query failed. See logs for details"
            logging.exception("There has been an error in PySNMP.")
        except RuntimeError:
            snmp_custom_data.error = "Exception"
            snmp_custom_data.error_code = 1
            snmp_custom_data.message = "SNMP Query failed. See logs for details"
            logging.exception("There has been an error.")
        except ValueError:
            snmp_custom_data.error = "Exception"
            snmp_custom_data.error_code = 1
            snmp_custom_data.message = "The SNMP Query did return a not supported value type."
            logging.exception("The SNMP query probably returned an unsupported value.")
        await q.put(snmp_custom_data.data)
        q.task_done()
