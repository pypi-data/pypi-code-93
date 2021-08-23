import asyncio
import logging
import time

import dns.asyncresolver
from dns.exception import DNSException

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class NoMatchException(Exception):
    def __init__(self, string_filter, sensor_last_message):
        self.string_filter = string_filter
        self.last_message = sensor_last_message


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "DNS"

    @property
    def kind(self) -> str:
        return "mpdns"

    @property
    def definition(self) -> dict:
        dns_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors a DNS server (Domain Name Service), resolves a domain name, "
            "and compares it to an IP address",
            sensor_help="The DNS sensor monitors a Domain Name Service (DNS) server. "
            "It resolves a domain name and compares it to a given IP address.",
            tag="mpdnssensor",
        )
        dns_def_group_dns_spec = SensorDefinitionGroup(name="dns_specific", caption="DNS Specific")
        dns_def_group_dns_spec.add_field_timeout(5, 1, 900)
        dns_def_group_dns_spec.add_field(
            field_type="integer",
            name="port",
            caption="Port",
            required="1",
            default=53,
            minimum=1,
            maximum=65535,
            help="Enter the port on which the DNS service of the parent device is running.",
        )
        dns_def_group_dns_spec.add_field(
            field_type="edit",
            name="domain",
            caption="Domain",
            required="1",
            help="Enter a DNS name to resolve.",
        )
        dns_def_group_dns_spec.add_field(
            field_type="edit",
            name="filter",
            caption="Filter",
            help="Enter comma separated strings to look for in the result. i.e. 192.168.1.0,192.168.2.0 or "
            "MX=10 mx.example.com,MX=20 mx2.example.com.  "
            "These values will be compared to the last message shown in the sensor."
            " If it doesn't match the resolved record, the sensor will "
            "go into an error state, if left blank the dns record will not be checked",
        )
        dns_def_group_dns_spec.add_field(
            field_type="radio",
            name="type",
            caption="Query Type",
            required="1",
            help="Specify the type of query that the sensor will send to the DNS server.",
            options={
                "A": "Host address IPv4 (A)",
                "AAAA": "Host address IPv6 (AAAA)",
                "CNAME": "Canonical name for an alias (CNAME)",
                "MX": "Mail exchange (MX)",
                "NS": "Authoritative name server (NS)",
                "SOA": "Start of a zone of authority marker (SOA)",
                "SRV": "Service Record",
                "TXT": "Text Record",
            },
            default="A",
        )
        dns_def.add_group(dns_def_group_dns_spec)
        return dns_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        dns_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            start = time.time()
            resolver = dns.asyncresolver.Resolver()
            resolver.nameservers = [f"{task_data['host']}"]
            resolver.port = int(task_data["port"])
            res = await resolver.resolve(task_data["domain"], rdtype=task_data["type"])

            end = (time.time() - start) * 1000
            msg = f"Query Type: {task_data['type']} for {task_data['domain']}. Result: "
            if task_data["type"] == "A" or task_data["type"] == "AAAA":
                for rdata in res:
                    msg += f"{str(rdata.address)}, "
            elif task_data["type"] == "MX":
                for rdata in res:
                    msg += f"{rdata.preference}: {rdata.exchange}"
            elif task_data["type"] == "SOA":
                for rdata in res:
                    msg += (
                        f"NS: {rdata.mname}, TECH: {rdata.rname}, S/N: {rdata.serial}, "
                        f"Refresh: {rdata.refresh / 60} min, Expire: {rdata.expire / 60} min"
                    )
            elif task_data["type"] == "TXT":
                for rdata in res:
                    for string in rdata.strings:
                        msg += f"{string.decode('utf-8') }"
            else:
                for rdata in res:
                    msg += f"{rdata.target}, "
            dns_data.message = msg
            split_strings = task_data["filter"].split(",")
            if task_data["filter"]:
                for string in split_strings:
                    if string not in msg:
                        logging.debug(f'{msg} did not contain filtered string "{string}"')
                        raise NoMatchException(string_filter=string, sensor_last_message=msg)
            dns_data.add_channel(
                name="Repsonse Time",
                mode="float",
                kind="TimeResponse",
                value=float(end),
            )
        except DNSException:
            dns_data.error = "Exception"
            dns_data.error_code = 1
            dns_data.message = "DNS check failed. See log for details"
            logging.exception("Error in dnspython.")
        except NoMatchException as e:
            dns_data.error = "Exception"
            dns_data.error_code = 1
            dns_data.message = (
                f"Filtered value '{e.string_filter}' not found in last message '{e.last_message}'. See log for details"
            )
            logging.exception("Filter did not match!")
        await q.put(dns_data.data)
        q.task_done()
