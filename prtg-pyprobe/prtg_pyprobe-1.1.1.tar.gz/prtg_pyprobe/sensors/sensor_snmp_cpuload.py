import asyncio
import logging
import time

from pysnmp.error import PySnmpError
from pysnmp.hlapi.asyncio import SnmpEngine, UsmUserData, CommunityData
from pysnmp.smi.error import NoSuchObjectError

from prtg_pyprobe.sensors.helpers import SensorData, SensorDefinition
from prtg_pyprobe.sensors.sensor import SensorSNMPBase


class Sensor(SensorSNMPBase):
    @property
    def name(self) -> str:
        return "SNMP CPU Load Avg"

    @property
    def kind(self) -> str:
        return "mpsnmpcpuloadavg"

    @property
    def definition(self) -> dict:
        snmp_cpu_load_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors Load Avg via SNMP.",
            sensor_help="This sensor monitors the load avg of a given target via SNMP.",
            tag="mpsnmpcpuloadavg",
        )
        snmp_cpu_load_def.add_group(self.snmp_specific_settings_group)
        return snmp_cpu_load_def.data

    async def work(self, task_data: dict, q: asyncio.Queue, snmp_engine: SnmpEngine):
        snmp_cpu_load_data = SensorData(sensor_id=task_data["sensorid"])
        creds = UsmUserData(userName=task_data["community"])
        if task_data["snmp_version"] == "0" or task_data["snmp_version"] == "1":
            creds = CommunityData(task_data["community"], mpModel=int(task_data["snmp_version"]))
        try:
            start_time = time.time()
            results = await self.get(
                target=task_data["host"],
                port=int(task_data["port"]),
                credentials=creds,
                oids=[
                    ".1.3.6.1.4.1.2021.10.1.3.1",
                    ".1.3.6.1.4.1.2021.10.1.3.2",
                    ".1.3.6.1.4.1.2021.10.1.3.3",
                ],
                engine=snmp_engine,
            )
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            for result in results:
                k, v = str(result[0]), self.cast(result[1])
                if v == "":
                    raise PySnmpError("Returned value empty. Probably no such value/object")
                if "1.3.1" in k:
                    k = "Load Avg 1 min"
                elif "1.3.2" in k:
                    k = "Load Avg 5min"
                elif "1.3.3" in k:
                    k = "Load Avg 10 min"
                snmp_cpu_load_data.add_channel(
                    name=k,
                    mode="float",
                    unit="Custom",
                    customunit="",
                    value=v,
                )
            snmp_cpu_load_data.add_channel(
                name="Response Time",
                mode="float",
                kind="TimeResponse",
                value=float(response_time),
            )
            snmp_cpu_load_data.message = "OK"
        except NoSuchObjectError:
            snmp_cpu_load_data.error = "Exception"
            snmp_cpu_load_data.error_code = 1
            snmp_cpu_load_data.message = "The OID is wrong."
            logging.exception("No such object. Probably the given OID is wrong.")
        except PySnmpError:
            snmp_cpu_load_data.error = "Exception"
            snmp_cpu_load_data.error_code = 1
            snmp_cpu_load_data.message = "SNMP Query failed. See logs for details"
            logging.exception("There has been an error in PySNMP.")
        except RuntimeError:
            snmp_cpu_load_data.error = "Exception"
            snmp_cpu_load_data.error_code = 1
            snmp_cpu_load_data.message = "SNMP Query failed. See logs for details"
            logging.exception("There has been an error.")
        except ValueError:
            snmp_cpu_load_data.error = "Exception"
            snmp_cpu_load_data.error_code = 1
            snmp_cpu_load_data.message = "The SNMP Query did return a not supported value type."
            logging.exception("The SNMP query probably returned an unsupported value.")
        await q.put(snmp_cpu_load_data.data)
        q.task_done()
