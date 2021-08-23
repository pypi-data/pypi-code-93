import asyncio
import logging
import time

import dns.asyncresolver
import dns.reversename
from dns.exception import DNSException

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "DNS Reverse"

    @property
    def kind(self) -> str:
        return "mpdnsptr"

    @property
    def definition(self) -> dict:
        dns_re_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="DNS PTR Lookup",
            sensor_help="The DNS sensor monitors a Domain Name Service (DNS) server. "
            "It resolves a domain name and compares it to a given IP address.",
            tag="mpdnssensor",
        )
        dns_re_def_group_dns_spec = SensorDefinitionGroup(name="dns_specific", caption="DNS Specific")
        dns_re_def_group_dns_spec.add_field_timeout(5, 1, 900)
        dns_re_def_group_dns_spec.add_field(
            field_type="integer",
            name="port",
            caption="Port",
            required="1",
            default=53,
            minimum=1,
            maximum=65535,
            help="Enter the port on which the DNS service of the parent device is running.",
        )
        dns_re_def_group_dns_spec.add_field(
            field_type="edit",
            name="ip",
            caption="IP Address",
            required="1",
            help="Enter am IP Address to resolve.",
        )
        dns_re_def.add_group(dns_re_def_group_dns_spec)
        return dns_re_def.data

    async def work(self, task_data: dict, q: asyncio.Queue):
        dns_re_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            start = time.time()
            resolver = dns.asyncresolver.Resolver()
            reverse_addr = dns.reversename.from_address(task_data["ip"])
            resolver.nameservers = [f"{task_data['host']}"]
            resolver.port = int(task_data["port"])
            res = await resolver.resolve(reverse_addr, rdtype="PTR")
            msg = f"Query Type: PTR for {task_data['ip']}. Result: "
            end = (time.time() - start) * 1000
            for rdata in res:
                msg += f"{rdata.target}, "
            dns_re_data.message = msg
            dns_re_data.add_channel(
                name="Repsonse Time",
                mode="float",
                kind="TimeResponse",
                value=float(end),
            )
        except DNSException:
            dns_re_data.error = "Exception"
            dns_re_data.error_code = 1
            dns_re_data.message = "DNS check failed. See log for details"
            logging.exception("Error in dnspython.")
        await q.put(dns_re_data.data)
        q.task_done()
