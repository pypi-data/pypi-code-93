"""
This module is intended to parse configuration files and instantiate the necessary systems within pyaware.
"""
import asyncio
import logging
import platform
import typing
import uuid
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import ruamel.yaml

import pyaware
import pyaware.mqtt.config
import pyaware.mqtt.client

aware_path = Path("")
config_main_path = Path("")

log = logging.getLogger(__file__)


@lru_cache()
def load_file_raw(file_path: typing.Union[Path, str]) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


@lru_cache()
def _yaml_load(data: str) -> dict:
    return ruamel.yaml.safe_load(data)


def yaml_load(data: bytes) -> dict:
    return deepcopy(_yaml_load(data.decode()))


def load_yaml_config(file_path: typing.Union[str, Path]) -> dict:
    """
    Load yaml config from a path
    :param file_path:
    :return: Loaded config
    """
    return yaml_load(load_file_raw(file_path))


def save_yaml_config(file_path: typing.Union[str, Path], config: dict):
    """
    Load config in its raw form and produce a dictionary, raw
    :param file_path:
    :return: Loaded config, raw data
    """
    with open(file_path, "w") as f:
        ruamel.yaml.dump(config, f, default_flow_style=False)
    load_file_raw.cache_clear()


def save_config_raw(file_path, config):
    """
    Load config in its raw form and produce a dictionary, raw
    :param file_path:
    :return: Loaded config, raw data
    """
    with open(file_path, "wb") as f:
        f.write(config)
    load_file_raw.cache_clear()


async def parse_modbus_rtu(port, **kwargs):
    """
    :param kwargs: All parameters required for instantiating the modbus client
    :return: Asyncronous modbus client
    """
    from aiomodbus.serial import ModbusSerialClient

    client = ModbusSerialClient(port, **kwargs)
    asyncio.get_event_loop().create_task(client.connect())
    return client


async def parse_modbus_tcp(host, **kwargs):
    """
    :param kwargs: All parameters required for instantiating the modbus client
    :return: Partial function that can be called to initiate the object and connection.
    """
    from aiomodbus.tcp import ModbusTCPClient

    client = ModbusTCPClient(host, **kwargs)
    asyncio.get_event_loop().create_task(client.connect())
    return client


async def parse_modbus_tcp_server(host, **kwargs):
    from pyaware.protocol.modbus import ModbusAsyncTcpServer

    server = ModbusAsyncTcpServer(host, **kwargs)
    asyncio.get_event_loop().create_task(server.start())
    return server


async def parse_translator(**kwargs):
    from pyaware.controllers.translator import Translator

    Translator(**kwargs)


async def parse_sp_pro(port: str, baudrate: int, parity: str, stopbits: int, **kwargs):
    try:
        from aiosppro.serial import SPPROSerialClient
    except ImportError:
        log.error(
            "Proprietary driver SPPro is specified in the config but is not correctly installed. "
            "Please acquire and install an appropriate version of aiosppro"
        )
        pyaware.stop()
        return

    client = SPPROSerialClient(
        port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, **kwargs
    )
    asyncio.get_event_loop().create_task(client.connect())
    return client


async def parse_imac2_master_auto_detect(**kwargs):
    from pyaware.protocol.imac2.protocol import Imac2Protocol
    from pyaware.controllers.imac2.master import auto_detect

    proto = Imac2Protocol(
        client_ser=kwargs.get("client_ser"),
        client_eth=kwargs.get("client_eth"),
        unit=kwargs.get("unit", 1),
    )
    return await auto_detect(proto)


async def parse_modbus_device(**kwargs):
    from pyaware.controllers.modbus import ModbusDevice

    return ModbusDevice(**kwargs)


async def parse_comap_device(**kwargs):
    from pyaware.controllers.comap import ComApInteliliteMRS16

    return ComApInteliliteMRS16(**kwargs)


async def parse_sp_pro_device(**kwargs):
    from pyaware.controllers.sp_pro import SPPRODevice

    return SPPRODevice(**kwargs)


async def parse_snmp_device(**kwargs):
    from pyaware.controllers.snmp import SNMPDevice

    return SNMPDevice(**kwargs)


async def parse_hbmqtt_gcp(**kwargs):
    raise DeprecationWarning(
        "Mqtt information should not be included in gateway configuration. Please remove"
    )


async def parse_hbmqtt_raw(device_id, **kwargs):
    raise DeprecationWarning(
        "Mqtt information should not be included in gateway configuration. Please remove"
    )


def build_connection_yaml():
    """
    Attempts to build a valid connection.yaml from legacy configuration files
    :return:
    """
    try:
        # Legacy cloud.yaml
        with open(aware_path / "config" / "cloud.yaml") as r:
            with open(aware_path / "config" / "connection.yaml", "w") as w:
                w.write("defaults: gcp\n" + r.read())
    except FileNotFoundError:
        # Legacy Local gateway.yaml
        legacy_config = pyaware.config.load_yaml_config(
            aware_path / "config" / "gateway.yaml"
        )
        mqtt_info = [
            v["params"]
            for v in legacy_config.get("communication", [])
            if v.get("type") in ["hbmqtt_raw", "mqtt_raw"]
        ]
        if len(mqtt_info) != 1:
            raise ValueError(
                "No valid mqtt communication information in legacy gateway.yaml. Aborting"
            )
        mqtt_info = mqtt_info[0]
        mqtt_info["defaults"] = "local"
        pyaware.config.save_yaml_config(
            aware_path / "config" / "connection.yaml", mqtt_info
        )


def load_connection_config():
    try:
        return pyaware.config.load_yaml_config(
            pyaware.config.aware_path / "config" / "connection.yaml"
        )
    except FileNotFoundError:
        pyaware.config.build_connection_yaml()
        return pyaware.config.load_yaml_config(
            pyaware.config.aware_path / "config" / "connection.yaml"
        )


async def parse_mqtt(
    params: typing.Dict[
        str, typing.Dict[str, typing.Union[str, dict, int, float, bool]]
    ]
) -> pyaware.mqtt.client.Mqtt:
    import pyaware.mqtt.client

    # Checks if the unit can parse the mqtt comms without information from gateway.yaml
    defaults = params.pop("defaults", "gcp")
    if defaults == "local":
        config = pyaware.mqtt.config.LocalConfig(**params)
    elif defaults == "gcp":
        config = pyaware.mqtt.config.GCPCloudConfig(**params)
    else:
        config = pyaware.mqtt.config.GCPCloudConfig(**params)
    client = pyaware.mqtt.client.Mqtt(config)
    # If mqtt parsing completed with all parameters set then set the event
    asyncio.create_task(client.connect())
    asyncio.create_task(client.loop())
    try:
        log.info(
            f"Waiting {config.remote_configuration_timeout} seconds for configuration over mqtt"
        )
        await asyncio.wait_for(
            client.gateway_config_received.wait(),
            timeout=config.remote_configuration_timeout,
        )
    except asyncio.TimeoutError:
        log.info(
            "Failed to receive remote configuration, proceeding to load local configuration"
        )
        client.load_config_from_disk()
    return client


async def parse_gateway_ipc(**kwargs):
    from pyaware.controllers.ipc import GatewayIPC

    return GatewayIPC(**kwargs)


async def get_mac_address(eth_interface="eth0", **kwargs):
    if platform.system() == "Linux":
        import fcntl
        import socket
        import struct

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(
            s.fileno(), 0x8927, struct.pack("256s", bytes(eth_interface, "utf-8")[:15])
        )
        return ":".join([f"{b:02x}" for b in info[18:24]])
    else:
        import uuid

        # Note: This ignores the interface selection and if no interfaces are present will return a random mac address
        # each power up with the least significant bit of the first octet set to 1
        return ":".join(
            [f"{(uuid.getnode() >> ele) & 0xff:02x}" for ele in range(0, 8 * 6, 8)][
                ::-1
            ]
        )


async def parse_comm_params(comms, instances) -> typing.Tuple[dict, dict]:
    comms_params = {}
    comms_params_unable_to_parse = {}

    for (
        k,
        v,
    ) in comms["params"].items():
        try:
            if not isinstance(v, dict):
                comms_params[k] = v
            elif v["type"] == "value":
                comms_params[k] = v["value"]
            elif v["type"] == "ref_comms":
                comms_params[k] = instances[v["value"]]
            elif v["type"] == "ref_path":
                comms_params[k] = aware_path / Path(v["value"])
            elif v["type"] == "ref_device":
                comms_params[k] = (
                    Path(pyaware.__file__).parent / "devices" / Path(v["value"])
                )
            elif v["type"] == "ref_comms_param":
                comms_params[k] = getattr(instances[v["value"]], v["key"])
            elif v["type"] == "ref_translation_config":
                comms_params[k] = aware_path / "config" / Path(v["value"])
            elif v["type"] == "ref_translation":
                comms_params[k] = {d: instances[d] for d in v["value"]}
            elif v["type"] == "ref_mac_address":
                comms_params[k] = await get_mac_address(v.get("value", "eth0"))
            elif v["type"] == "uuid":
                comms_params[k] = uuid.uuid4()
            else:
                raise ValueError("No valid type detected in config file")
        except KeyError:
            comms_params_unable_to_parse[k] = v
    return comms_params, comms_params_unable_to_parse


async def parse_communication(communication: list):
    """
    :param communication:
    :return: dictionary of form
    {
      <id>:
        {
          "protocol": <string>, # eg. modbus_rtu, modbus_tcp
          "handler": handler to call to return the communication type in a connected state
        },
        {...},
      ...,
    }
    """
    protocol_handlers = {
        "modbus_rtu": parse_modbus_rtu,
        "modbus_rtu2": parse_modbus_rtu,
        "modbus_tcp": parse_modbus_tcp,
        "modbus_tcp2": parse_modbus_tcp,
        "sp_pro": parse_sp_pro,
        "modbus_tcp_server": parse_modbus_tcp_server,
        "imac2_auto_detect": parse_imac2_master_auto_detect,
        "translator": parse_translator,
        "modbus_device": parse_modbus_device,
        "comap_device": parse_comap_device,
        "sp_pro_device": parse_sp_pro_device,
        "mqtt_raw": parse_hbmqtt_raw,
        "mqtt_gcp": parse_hbmqtt_gcp,
        "hbmqtt_raw": parse_hbmqtt_raw,
        "hbmqtt_gcp": parse_hbmqtt_gcp,
        "gateway_ipc": parse_gateway_ipc,
        "snmp_device": parse_snmp_device,
    }
    instances = {}
    for comms in communication:
        log.info(f"Initialising {comms['name']}")
        comms_params, _ = await parse_comm_params(comms, instances)
        try:
            instances[comms["name"]] = await protocol_handlers[comms["type"]](
                **comms_params
            )
        except DeprecationWarning as e:
            log.warning(repr(e))
        log.info(f"Initialised {comms['name']}")
    return instances
