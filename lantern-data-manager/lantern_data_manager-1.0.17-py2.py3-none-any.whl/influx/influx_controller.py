import os

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import \
    SYNCHRONOUS  # To handle InfluxDB synchonous writing
from lantern_data_manager.utils.query import make_query
from lantern_data_manager.utils.time import to_nanoseconds

IS_LOCAL = os.environ.get("IS_LOCAL", False)


class InfluxController:
    def __init__(self, url=None, org=None, token=None):
        """Constructor of class

        Args:
            ulr (string): url to influx api, exampl: http://localhost:9999
            token (string, optional): token to influx, if absent, read from environ, otherwise fail.
            org (string, optional): organization to influx, if absent, read from environ, otherwise fail.
            user_name (string, optional): user_name to influx, if absent, read from environ, otherwise fail.
            password (string, optional): password to influx, if absent, read from environ, otherwise fail.
        """
        if not url:
            if IS_LOCAL:
                url = os.getenv("INFLUXDB_BASE_URL_PUBLIC", False)
            else:
                url = os.getenv("INFLUXDB_BASE_URL", False)
            if not url:
                raise Exception("url not defined")
        if not org:
            org = os.getenv("INFLUXDB_ORG", False)
            if not org:
                raise Exception("org not defined")

        if not token:
            token = os.getenv("INFLUXDB_TOKEN", False)
            if not token:
                raise Exception("token not defined")

        self.org = org
        self.client = self.__get_influx_connection(url, token, self.org)

    def __get_influx_connection(self, URL, TOKEN, ORG):
        return InfluxDBClient(url=URL, token=TOKEN, org=ORG)

    def add_telemetries(self, bucket, telemetries, org=None):
        """
        Adds telemetries into influx

        Args:
            bucket (string): bucket to put telemetries
            telemetries (list<dict>): points to write into influx, example:
            [{
                "measurement" : mesurement value,
                "tags" : {}, custom values
                "fields" : {}, custom values
                "time" : int
            }]
            org (string, optional): organization, if absent, read from environ . Defaults to None.
        """
        for data in telemetries:
            if not data["measurement"]:
                raise Exception("no 'measurement' column found")
            if not data["tags"]:
                raise Exception("no 'tags' column found")
            if not data["fields"]:
                raise Exception("no 'fields' column found")
            if not data["time"]:
                raise Exception("no 'time' column found")

        write_client = self.client.write_api(write_options=SYNCHRONOUS)
        if not org:
            org = self.org
        points = [p.to_line_protocol() for p in self._get_points(telemetries)]
        return write_client.write(bucket, org, points)

    def _get_points(self, telemetries):
        _points = self._format_telemetries(telemetries)
        points = []
        for _point in _points:
            _point["timestamp"] = to_nanoseconds(round(_point["timestamp"]))
            point = Point(_point["measurement"])
            # adding tags
            try:
                _point["field"]["value"] = float(_point["field"]["value"])
            except Exception:
                pass
            for tag in _point["tags"]:
                point.tag(tag["key"], tag["value"])
            point.field(_point["field"]["key"], _point["field"]["value"])
            point.time(_point["timestamp"])
            points.append(point)
        return points

    def _format_telemetries(self, telemetries):
        points = []
        for telemetry in telemetries:
            for field in telemetry["fields"]:
                point = {}
                point["measurement"] = telemetry["measurement"]
                point["tags"] = [
                    {"key": key, "value": value}
                    for key, value in telemetry["tags"].items()
                ]
                point["field"] = {"key": field, "value": telemetry["fields"][field]}
                point["timestamp"] = telemetry["time"]
                points.append(point)
        return points

    def call_query_builder(
        self,
        bucket,
        start_range,
        device_ids,
        measurement=None,
        type=None,
        stop_range=None,
        field=None,
        fields=[],
        filters=None,
        groupers=None,
        first=None,
        last=None
    ):
        """Creates a query list based on the params

        Args:
            bucket (string): bucket
            start_range (string): a start point to query data: -1m,-1h,-1d, etc
            device_ids (list): list of devices to query
            measurement (string, optional): '_measurement' value in influxdb (metric type) ex: watermeter. Defaults to None.
            stop_range (string, optional): an stop point to query data, similar to start_range. Defaults to None.
            field (string, optional): '_field' value in influxdb (metric name), ex: counter, temperature, humidity, etc. Defaults to None.
            fields ([string], optional): '_field' value in influxdb (metric name), ex: counter, temperature, humidity, etc. Defaults to None. with an or
            filters (list<dict>, optional): List of {name: 'str', value: 'str'}, which is a list of filters to be added to query. Defaults to None.
            groupers (list<dict>, optional): Which is the grouper to be used, with the form: {every: 'str', fn: 'str', type: 'str'(None)}, ex: {every: '10s', fn: 'sum', type: 'float'}, where type is optional and will cast data to that type.

        Returns:
            list<string>: list with queries, it's a query per grouper
        """
        return make_query(
            bucket=bucket,
            start_range=start_range,
            device_ids=device_ids,
            measurement=measurement,
            type=type,
            stop_range=stop_range,
            field=field,
            fields=fields,
            filters=filters,
            groupers=groupers,
            first=first,
            last=last
        )

    def query(self, query_string):
        """Performs a query into influx

        Args:
            query_string (string): query to perform in influx, for an easier use,
                                  call call_query_builder to generate a query

        Returns:
            list<dict>: response from influx
        """
        query_api = self.client.query_api()
        tables = query_api.query(query_string)
        return self.parse_data(tables)

    def parse_data(self, data):
        items = []
        for table in data:
            for record in table.records:
                items.append(record.values)
        return items


""" Usage example
        gateway_trace = {
            "mapping" : (self.timestamp)*1000,
            "virtual_node" : "virtual" + self.virtual_node,
            "time_interval": self.time_interval,
            "gateway_mac": self.gateway_mac,
            "seen_beacons": len(self.data),
            "gateways": len(self.data)
        }
        logger.info("Saving gateways telemetries into InfluxDB for: {}".format(gateway_trace))
        influx_manager = InfluxController('http://telemetry.lantern.rocks:9999','my-token','lantern',"{}_ble_buffer".format(self.team))
        influx_manager.write_data("Trilateration","gateways",[gateway_trace],"mapping")
        logger.info("TRACE GATEWAY {}".format(self.gateway_mac))
"""
