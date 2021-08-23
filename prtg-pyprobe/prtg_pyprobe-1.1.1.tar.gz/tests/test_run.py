import asyncio
import json
import time

import pytest
from pysnmp.hlapi.asyncio import SnmpEngine
from requests import Response
from testfixtures import LogCapture

import prtg_pyprobe.monitoring
import prtg_pyprobe.run
from prtg_pyprobe.communication.communication_http_api import PRTGHTTPApi
from prtg_pyprobe.monitoring import monitoring
from prtg_pyprobe.run import main, monitoring_loop


def return_response_200(*args, **kwargs):
    resp = Response()
    resp.status_code = 200
    resp._content = (
        b'{"sensorid": "1234", "timeout": 5, "target": "https://example.com","request_type": "GET",'
        b'"acceptable_status_codes": "","headers": "","post_data": "",}'
    )
    return resp


async def return_async_response_200(*args, **kwargs):
    resp = Response()
    resp.status_code = 200
    resp._content = (
        '{"sensorid": "1234", "timeout": 5, "target": "https://example.com", "request_type": "GET", '
        '"acceptable_status_codes": "", "headers": "", "post_data": ""}'.encode("utf-8")
    )
    return resp


def return_dict_json(*args, **kwargs):
    return [
        {
            "sensorid": "1234",
            "timeout": 5,
            "target": "https://example.com",
            "request_type": "GET",
            "acceptable_status_codes": "",
            "headers": "",
            "post_data": "",
        }
    ]


class MockEventLoop(object):
    @staticmethod
    def run_until_complete(self):
        return "work"

    @staticmethod
    def is_running():
        return False


def mock_event_loop():
    return MockEventLoop()


async def return_true_async(*args, **kwargs):
    return True


class TestRun:
    @pytest.mark.asyncio
    async def test_monitoring_loop(self, monkeypatch, prtg_api, probe_config_dict):
        monkeypatch.setattr(PRTGHTTPApi, "get_tasks", return_async_response_200)
        monkeypatch.setattr(PRTGHTTPApi, "send_data", return_async_response_200)
        monkeypatch.setattr(asyncio, "sleep", return_true_async)
        monkeypatch.setattr(monitoring, "monitoring", return_true_async)
        with LogCapture() as log:
            await monitoring_loop(
                prtg_api=prtg_api, sensors=[], run_monitoring=True, snmp_eng=SnmpEngine(), config=probe_config_dict
            )
        log.check_present(
            (
                "root",
                "DEBUG",
                "Tasks received from PRTG {'sensorid': '1234', 'timeout': 5, 'target': 'https://example.com', "
                "'request_type': 'GET', 'acceptable_status_codes': '', 'headers': '', 'post_data': ''}",
            )
        )

    def test_run(self, monkeypatch, mocker):
        monkeypatch.setenv(
            name="PROBE_CONFIG",
            value='{"disable_ssl_verification": false, "log_file_location": "", "log_level": "DEBUG",'
            ' "probe_access_key": '
            '"miniprobe", "probe_access_key_hashed": "cd7b773e2ce4205e9f5907b157f3d26495c5b373", '
            '"probe_base_interval": "60", "probe_task_chunk_size": "20", '
            '"probe_gid": "72C461B5-F768-470B-A1A8-2D5F5DEDDF8F", '
            '"probe_name": "Python Mini Probe UT", "probe_protocol_version": "1", '
            '"prtg_server_ip_dns": "ut.prtg,com", "prtg_server_port": "443"}',
        )
        config = {
            "disable_ssl_verification": False,
            "log_file_location": "",
            "log_level": "DEBUG",
            "probe_access_key": "miniprobe",
            "probe_access_key_hashed": "cd7b773e2ce4205e9f5907b157f3d26495c5b373",
            "probe_base_interval": "60",
            "probe_task_chunk_size": "20",
            "probe_gid": "72C461B5-F768-470B-A1A8-2D5F5DEDDF8F",
            "probe_name": "Python Mini Probe UT",
            "probe_protocol_version": "1",
            "prtg_server_ip_dns": "ut.prtg,com",
            "prtg_server_port": "443",
        }
        monkeypatch.setattr(PRTGHTTPApi, "send_announce", return_response_200)
        monkeypatch.setattr(Response, "json", return_dict_json)
        monkeypatch.setattr(Response, "json", return_dict_json)
        monkeypatch.setattr(asyncio, "get_event_loop", mock_event_loop)
        monkeypatch.setattr(prtg_pyprobe.monitoring, "monitoring", True)
        monkeypatch.setattr(time, "sleep", True)
        with LogCapture() as log:
            main()
        log.check_present(
            ("root", "INFO", "Starting pyprobe!"),
            ("root", "INFO", "Loading configuration"),
            ("root", "INFO", "Config loaded and probe announcing to PRTG"),
            ("root", "DEBUG", f"Your current config: \n {json.dumps(config, indent=2)}"),
            ("root", "INFO", "Initializing SNMP Engine"),
            ("root", "INFO", "Initializing PRTG API"),
            ("root", "INFO", "Initializing Sensors"),
            ("root", "INFO", "Init done!"),
        )
