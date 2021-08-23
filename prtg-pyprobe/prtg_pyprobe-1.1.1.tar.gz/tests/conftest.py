import pathlib

import pytest
from psutil._common import shwtemp

from prtg_pyprobe.communication.communication_http_api import PRTGHTTPApi
from prtg_pyprobe.sensors import (
    sensor_ping,
    sensor_port,
    sensor_http,
    sensor_http_rest,
    sensor_probe_memory,
    sensor_probe_health,
    sensor_snmp_custom,
    sensor_snmp_cpuload,
    sensor_snmp_traffic,
    sensor_traffic,
    sensor_dns,
    sensor_dns_reverse,
    sensor_probe_temperature,
    sensor_probe_diskspace,
    sensor_external_ip,
    sensor_cpuload,
    sensor_s3_bucket_total,
    sensor_prometheus_exporter,
    sensor_script,
)
from prtg_pyprobe.sensors.helpers import (
    SensorDefinition,
    SensorDefinitionGroup,
    SensorData,
)
from prtg_pyprobe.utils.config import (
    IPDNSValidator,
    PortRangeValidator,
    NotEmptyValidator,
    GUIDValidator,
    BaseIntervalValidator,
    BaseChunkSizeValidator,
    DirectoryWriteableValidator,
    ProbeConfig,
)
from prtg_pyprobe.utils.sensor_loader import load_sensor_modules, create_sensor_objects


@pytest.fixture()
def list_sensor_modules():
    print(pathlib.Path().absolute())
    return load_sensor_modules(sensor_path="../prtg_pyprobe/sensors")


@pytest.fixture()
def list_sensor_objects():
    print(pathlib.Path().absolute())
    return create_sensor_objects(sensor_path="../prtg_pyprobe/sensors")


@pytest.fixture()
def ip_dns_validator():
    return IPDNSValidator()


@pytest.fixture()
def port_range_validator():
    return PortRangeValidator()


@pytest.fixture()
def not_empty_validator():
    return NotEmptyValidator()


@pytest.fixture()
def guid_validator():
    return GUIDValidator()


@pytest.fixture()
def base_interval_validator():
    return BaseIntervalValidator()


@pytest.fixture()
def base_chunk_size_validator():
    return BaseChunkSizeValidator()


@pytest.fixture()
def directory_writeable_validator():
    return DirectoryWriteableValidator()


@pytest.fixture()
def probe_config():
    return ProbeConfig(path="config.yml")


@pytest.fixture()
def probe_config_dict():
    probe_cfg_dict = {
        "disable_ssl_verification": True,
        "log_file_location": "./pyprobe.log",
        "log_level": "INFO",
        "probe_access_key": "miniprobe",
        "probe_access_key_hashed": "cd7b773e2ce4205e9f5907b157f3d26495c5b373",
        "probe_base_interval": "60",
        "probe_task_chunk_size": "20",
        "probe_gid": "1BFB9273-08D7-43AF-B535-18E4A767BA34",
        "probe_name": "Python Mini Probe",
        "probe_protocol_version": "1",
        "prtg_server_ip_dns": "test.prtg.com",
        "prtg_server_port": "443",
    }
    return probe_cfg_dict


@pytest.fixture()
def prtg_api(probe_config_dict):
    return PRTGHTTPApi(probe_config=probe_config_dict, backoff_factor=0.1)


@pytest.fixture()
def sensor_definition():
    definition = SensorDefinition(
        name="Testsensor",
        kind="testkind",
        description="This is a Test",
        sensor_help="Test Help",
        tag="testsensor",
        default="1",
    )
    return definition


@pytest.fixture()
def sensor_definition_group():
    definition_group = SensorDefinitionGroup(name="testgroup", caption="TestCaption")
    return definition_group


@pytest.fixture()
def sensor_data():
    sensor_data = SensorData(sensor_id="1234")
    return sensor_data


@pytest.fixture()
def ping_sensor():
    return sensor_ping.Sensor()


@pytest.fixture()
def port_sensor():
    return sensor_port.Sensor()


@pytest.fixture()
def http_sensor():
    return sensor_http.Sensor()


@pytest.fixture()
def http_rest_sensor():
    return sensor_http_rest.Sensor()


@pytest.fixture()
def prometheus_exporter_sensor():
    return sensor_prometheus_exporter.Sensor()


@pytest.fixture()
def probehealth_sensor():
    return sensor_probe_health.Sensor()


@pytest.fixture()
def probe_memory_sensor():
    return sensor_probe_memory.Sensor()


@pytest.fixture()
def probetemp_sensor():
    return sensor_probe_temperature.Sensor()


@pytest.fixture()
def probe_disk_space_sensor():
    return sensor_probe_diskspace.Sensor()


@pytest.fixture()
def snmp_custom_sensor():
    return sensor_snmp_custom.Sensor()


@pytest.fixture()
def snmp_traffic_sensor():
    return sensor_snmp_traffic.Sensor()


@pytest.fixture()
def snmp_cpu_load_sensor():
    return sensor_snmp_cpuload.Sensor()


@pytest.fixture()
def traffic_sensor():
    return sensor_traffic.Sensor()


@pytest.fixture()
def dns_sensor():
    return sensor_dns.Sensor()


@pytest.fixture()
def dns_reverse_sensor():
    return sensor_dns_reverse.Sensor()


@pytest.fixture()
def external_ip_sensor():
    return sensor_external_ip.Sensor()


@pytest.fixture()
def cpu_load_sensor():
    return sensor_cpuload.Sensor()


@pytest.fixture()
def s3_total_sensor():
    return sensor_s3_bucket_total.Sensor()


@pytest.fixture()
def script_sensor():
    return sensor_script.Sensor()


@pytest.fixture()
def snmp_custom_sensor_taskdata():
    return {
        "sensorid": "1234",
        "community": "public",
        "port": "161",
        "snmp_version": "0",
        "host": "127.0.0.1",
        "custom_oid": "1.3.6.1.1.2.3.4",
        "custom_unit": "test",
        "value_type": "integer",
    }


@pytest.fixture()
def snmp_traffic_sensor_taskdata():
    return {
        "sensorid": "1234",
        "community": "public",
        "port": "161",
        "snmp_version": "0",
        "host": "127.0.0.1",
        "ifindex": "1",
    }


@pytest.fixture()
def snmp_cpuload_sensor_taskdata():
    return {
        "sensorid": "1234",
        "community": "public",
        "port": "161",
        "snmp_version": "0",
        "host": "127.0.0.1",
    }


@pytest.fixture()
def task_data_ping():
    return [
        {
            "sensorid": "1234",
            "host": "paessler.com",
            "timeout": "5",
            "kind": "mpping",
            "target_port": "443",
            "ping_count": "4",
            "ping_type": "tcp",
        }
    ]


@pytest.fixture()
def task_data_snmp():
    return [
        {
            "sensorid": "1234",
            "host": "127.0.0.1",
            "community": "public",
            "port": "161",
            "kind": "mpsnmpcustom",
            "snmp_version": "1",
            "custom_oid": "1.3.6.1",
            "custom_unit": "#",
            "value_type": "integer",
        }
    ]


@pytest.fixture()
def sensor_exception_message():
    return {
        "sensorid": "1234",
        "message": "Overwrite me in test case",
        "error": "Exception",
        "code": 1,
    }


async def asyncio_open_connection(*args, **kwargs):
    reader = ReturnObjectAsyncioOpenConnection()
    writer = ReturnObjectAsyncioOpenConnection()
    return reader, writer


class ReturnObjectAsyncioOpenConnection(object):
    def close(self):
        return

    async def wait_closed(self):
        return


@pytest.fixture()
def psutil_system_temperatures():
    return {
        "acpitz": [shwtemp(label="", current=60.5, high=84.0, critical=84.0)],
        "coretemp": [
            shwtemp(label="Package id 0", current=53.0, high=100.0, critical=100.0),
            shwtemp(label="Core 0", current=53.0, high=100.0, critical=100.0),
            shwtemp(label="Core 1", current=52.0, high=100.0, critical=100.0),
            shwtemp(label="Package id 0", current=53.0, high=100.0, critical=100.0),
            shwtemp(label="Core 0", current=53.0, high=100.0, critical=100.0),
            shwtemp(label="Core 1", current=52.0, high=100.0, critical=100.0),
        ],
        "dell_smm": [
            shwtemp(label="CPU", current=60.0, high=None, critical=None),
            shwtemp(label="Ambient", current=39.0, high=None, critical=None),
            shwtemp(label="Ambient", current=32.0, high=None, critical=None),
            shwtemp(label="GPU", current=16.0, high=None, critical=None),
            shwtemp(label="Other", current=43.0, high=None, critical=None),
        ],
    }


class DnsAnswer(object):
    @property
    def address(self):
        return "1.2.3.4"

    @property
    def target(self):
        return "mytarget"

    @property
    def preference(self):
        return "mypref"

    @property
    def exchange(self):
        return "myex"

    @property
    def mname(self):
        return "mname"

    @property
    def rname(self):
        return "rname"

    @property
    def serial(self):
        return "serial"

    @property
    def refresh(self):
        return 60

    @property
    def expire(self):
        return 60

    @property
    def strings(self):
        return [b"string1", b"string2"]


async def dns_answer(*args, **kwargs):
    return [DnsAnswer()]
