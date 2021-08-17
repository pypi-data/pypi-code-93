from __future__ import annotations
import asyncio
import logging
import pyaware
import typing
import time
from datetime import datetime
from dataclasses import dataclass
from pyaware.mqtt.models import TopologyV2
from pyaware.mqtt.client import Mqtt
from pyaware import watchdog
from typing import Union

from pyaware import events

import ifaddr

if typing.TYPE_CHECKING:
    from ifaddr import Adapter

log = logging.getLogger(__file__)


@events.enable
@dataclass
class GatewayIPC:
    eth_interface: str
    gateway_id: str = ""
    device_id: str = ""
    serial_number: str = ""
    include_serial: bool = False
    ip_address: Union[str, None] = None
    cloud_broker: Mqtt = None

    def __post_init__(self):
        self.topologies = {}
        self.identify()
        if self.include_serial:
            self.topic_types = {
                "state": "state_serial",
                "topology": "topology_serial",
                "heartbeat": "gateway_heartbeat_serial",
            }
        else:
            self.topic_types = {
                "state": "state",
                "topology": "topology",
                "heartbeat": "gateway_heartbeat",
            }
        events.publish("request_topology")

    def init(self):
        asyncio.create_task(self.send_gateway_heartbeat())
        self.setup_watchdogs()

    def setup_watchdogs(self):
        try:
            self.cloud_broker.client.on_connect = watchdog.watch(
                f"ipc_cloud_comms_status_{id(self)}"
            )(self.cloud_broker.client.on_connect)
        except AttributeError:
            pass
        try:
            self.cloud_broker.client.publish = watchdog.watch(
                f"ipc_cloud_comms_status_{id(self)}"
            )(self.cloud_broker.client.publish)
        except AttributeError:
            pass
        try:
            self.cloud_broker.client.on_disconnect = watchdog.watch_starve(
                f"ipc_cloud_comms_status_{id(self)}"
            )(self.cloud_broker.client.on_disconnect)
        except AttributeError:
            pass
        dog_eth = watchdog.WatchDog(
            heartbeat_time=60,
            success_cbf=lambda: events.publish(
                f"process_data/{id(self)}",
                data={"cloud-comms-status": True},
                timestamp=datetime.utcnow(),
                device_id=self.device_id,
            ),
            failure_cbf=lambda: events.publish(
                f"process_data/{id(self)}",
                data={"cloud-comms-status": False},
                timestamp=datetime.utcnow(),
                device_id=self.device_id,
            ),
        )
        watchdog.manager.add(f"ipc_cloud_comms_status_{id(self)}", dog_eth)
        dog_eth.start(start_fed=False)

    async def update_state(self):
        log.info("Starting gateway update state")
        state = self.identify()
        state.values["version"] = pyaware.__version__
        events.publish(
            f"trigger_send",
            topic_type=self.topic_types["state"],
            data=state.values,
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            gateway=self.gateway_id,
            serial_number=self.serial_number,
        )

    async def send_gateway_heartbeat(self):
        log.info("Starting gateway heartbeat writes")
        while True:
            if pyaware.evt_stop.is_set():
                log.info("Closing gateway heartbeat")
                return
            try:
                await asyncio.sleep(5)
                ip_address = self.get_ip()
                if ip_address:
                    if ip_address != self.ip_address:
                        self.ip_address = ip_address
                        self.update_topology()
                        # We require an IP Address to send the gateway state somewhere so we only send a new state on
                        # IP Address change
                        asyncio.create_task(self.update_state())
                    timestamp = datetime.utcnow()
                    data = {"ipAddress": ip_address, "timestamp": timestamp}
                    events.publish(
                        f"trigger_send",
                        data=data,
                        timestamp=timestamp,
                        topic_type=self.topic_types["heartbeat"],
                        device_id=self.device_id,
                        gateway=self.gateway_id,
                        serial_number=self.serial_number,
                    )
                    events.publish(
                        f"process_data/{id(self)}",
                        data={"heartbeat": time.time()},
                        timestamp=timestamp,
                        device_id=self.device_id,
                        gateway=self.gateway_id,
                    )
                else:
                    log.warning(
                        "No IP Address found for the chosen adapter. Skipping Gateway heartbeat."
                    )
                await asyncio.sleep(25)
            except asyncio.CancelledError:
                if not pyaware.evt_stop.is_set():
                    log.warning("Gateway heartbeat cancelled without stop signal")
                    continue
            except BaseException as e:
                if not pyaware.evt_stop.is_set():
                    log.exception(e)

    def get_network_adapter(self) -> Union[Adapter, None]:
        """
        Gets the network adapter matching the name defined for the IPC controller.
        :return: Adapter object of the name defined for the IPC controller if there is one defined else returns None.
        """
        # Get adapter object from name
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            if adapter.nice_name == self.eth_interface:
                return adapter
        # Returns None if there is no matching adapter
        return None

    def get_ip(self) -> Union[str, None]:
        """
        Gets the IP Address of the adapter defined in config.
        :return: String representation of the IPV4 address tied to the adapter if there is one defined else returns
        None.
        """
        try:
            adapter = self.get_network_adapter()
            if adapter:
                ip_addresses = adapter.ips
                for ip_address in ip_addresses:
                    if ip_address.is_IPv4:
                        return ip_address.ip
            else:
                log.warning(f"No Adapter found with name {self.eth_interface}.")
            # Returns None if there is no IPV4 address or adapter
            return None
        except BaseException as e:
            log.exception(e)

    def identify(self) -> TopologyV2:
        data = {}
        if self.ip_address:
            data["ipAddress"] = self.ip_address
        return TopologyV2(
            values=data,
            timestamp=datetime.utcnow(),
            children=list(self.topologies.values()),
        )

    @events.subscribe(topic="request_topology")
    def update_topology(self):
        """
        Updates the topology for a given device and resends all the currently connected devices
        :param data: Device topology payload derived from identify method
        :param timestamp: Timestamp of the topology
        :param topic: device_topology/{device_id}
        :return:
        """
        payload = self.identify()
        log.info(f"New topology:  {payload}")
        events.publish(
            f"trigger_send",
            data=payload,
            timestamp=datetime.utcnow(),
            topic_type=self.topic_types["topology"],
            device_id=self.device_id,
            gateway=self.gateway_id,
            serial_number=self.serial_number,
        )

    @events.subscribe(topic="device_topology/#", parse_topic=True)
    def build_topology(self, data, timestamp, topic):
        """
        Updates the topology for a given device and resends all the currently connected devices
        :param data: Device topology payload derived from identify method
        :param timestamp: Timestamp of the topology
        :param topic: device_topology/{device_id}
        :return:
        """
        device_id = topic.split("/")[-1]
        self.topologies[device_id] = data
        self.update_topology()
