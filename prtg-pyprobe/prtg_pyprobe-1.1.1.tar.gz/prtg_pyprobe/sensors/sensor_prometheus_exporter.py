import asyncio
import logging
from typing import Any

import httpx
from prometheus_client import parser

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "Prometheus Exporter (experimental)"

    @property
    def kind(self) -> str:
        return "mpprometheusexporter"

    @property
    def definition(self) -> dict:
        prometheus_exporter_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors a Prometheus exporter",
            sensor_help="Monitors a Prometheus exporter and pulls select metrics.",
            tag="mpprometheusexporter",
        )
        prometheus_exporter_def_group_target = SensorDefinitionGroup(name="target_info", caption="Target Information")
        prometheus_exporter_def_group_metric = SensorDefinitionGroup(name="metric_info", caption="Metric Information")
        prometheus_exporter_def_group_target.add_field_timeout(10, 10, 900)
        prometheus_exporter_def_group_target.add_field(
            field_type="edit",
            name="port",
            caption="Exporter Port",
            required="1",
            help="Enter the port the Prometheus Exporter is listening on.",
        )
        prometheus_exporter_def_group_metric.add_field(
            field_type="edit",
            name="metrics",
            caption="Metrics",
            default="",
            required="1",
            help="Enter a list of comma separated metrics to capture.",
        )
        prometheus_exporter_def_group_metric.add_field(
            field_type="edit",
            name="metric_path",
            caption="Metric Path",
            default="/metrics",
            required="1",
            help="Enter the path to the metrics, e.g. /metrics",
        )
        prometheus_exporter_def.add_group(group=prometheus_exporter_def_group_target)
        prometheus_exporter_def.add_group(group=prometheus_exporter_def_group_metric)
        return prometheus_exporter_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        prometheus_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            uri = f"http://{task_data['host']}:{task_data['port']}{task_data['metric_path']}"

            async with httpx.AsyncClient() as client:
                request = client.build_request(
                    method="GET",
                    url=uri,
                )
                response = await client.send(request=request, timeout=int(task_data["timeout"]))

            res_txt = response.text
            metrics = parser.text_string_to_metric_families(res_txt)
            for family in metrics:
                for sample in family.samples:
                    if sample.name in task_data["metrics"]:
                        prometheus_data.add_channel(
                            name=f"{sample.name} - {sample.labels}",
                            mode="float",
                            kind="Custom",
                            customunit="",
                            value=self.cast_to_float(value=sample.value, sample_name=sample.name),
                        )
            prometheus_data.message = "OK"
        except CastException:
            prometheus_data.error = "Exception"
            prometheus_data.error_code = 1
            prometheus_data.message = "Could not cast the value returned to the correct format."
            logging.exception("Casting error.")
        except httpx.HTTPError:
            prometheus_data.error = "Exception"
            prometheus_data.error_code = 1
            prometheus_data.message = "HTTP request failed. See log for details."
            logging.exception("There was an error in httpx.")
        except KeyError:
            prometheus_data.error = "Exception"
            prometheus_data.error_code = 1
            prometheus_data.message = "Something went wrong. See logs for details."
            logging.exception("Something went wrong.")
        except ValueError:
            prometheus_data.error = "Exception"
            prometheus_data.error_code = 1
            prometheus_data.message = "Something went wrong. See logs for details."
            logging.exception("Something went wrong.")

        await q.put(prometheus_data.data)
        q.task_done()

    @staticmethod
    def cast_to_float(value: Any, sample_name: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise CastException(value=value, sample_name=sample_name)


class CastException(Exception):
    def __init__(self, value: Any, sample_name: str):
        self._message = f"Could not convert {value} for sample {sample_name}"
        super().__init__(self._message)
