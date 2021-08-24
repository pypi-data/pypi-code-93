from typing import Any

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxData:
    def __init__(self, url: str, org: str, token: str, bucket: str):
        self._client = InfluxDBClient(url=url, token=token)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._org = org
        self._bucket = bucket

    @property
    def bucket(self) -> str:
        return self._bucket

    def write(self, point: Point):
        self._write_api.write(self._bucket, self._org, point)

    def batch(self, sequence: Any):
        self._write_api.write(self._bucket, self._org, sequence)

    def query(self, query: str):
        return self._client.query_api().query(query, org=self._org)

    def is_node_healthy(self):
        status = self._client.health().status
        print(f"HEALTH {self._client.ready()}")
        return True  # TODO
