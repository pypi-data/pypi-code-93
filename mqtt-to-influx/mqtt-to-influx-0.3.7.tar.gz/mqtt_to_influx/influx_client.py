# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# }}}

from influxdb import InfluxDBClient
from mqtt_to_influx.parse_options import args

# FIXME: This may create one client per import.. let's see
influx_client = InfluxDBClient(args.influx_db_host, 
                               args.influx_db_port,
                               database = args.influx_db_name,
                               username = args.influx_db_user,
                               password = args.influx_db_password)
