#!/usr/bin/env python3
# pylint
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods

import os
import sys
import datetime
import json
import logging
import paho.mqtt.client as mqtt
from time import sleep
from influxdb.exceptions import InfluxDBServerError
from mqtt_to_influx.parse_mqtt_data import ParseMqttData
from mqtt_to_influx.config import CONFIG
from mqtt_to_influx.parse_options import args


# logformat='[%(levelname)s] %(message)s'
logformat='[%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
if args.verbose:
    logformat='[%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
if args.debug:
    logging.basicConfig(level=os.environ.get("LOG", "DEBUG"), format = logformat)
else:
    logging.basicConfig(level=os.environ.get("LOG", "INFO"), format = logformat)

logger = logging.getLogger(__name__)


# The callback for when the mqtt_client receives a CONNACK response from the server.
def on_connect(mqtt_client, userdata, flags, rc):
    logger.info("Connected to server")

    logger.info("Connecting configured mqtt topics with interpreters")
    for path in CONFIG['mqtt_topics']:
        try:
            mqtt_client.subscribe(path, qos = 0)
            __import__ ("mqtt_to_influx." + CONFIG['mqtt_topics'][path])
            callback_func = getattr(sys.modules["mqtt_to_influx." + CONFIG['mqtt_topics'][path]], "Process_mqtt_message")
            mqtt_client.message_callback_add(path, callback_func)
            is_verbose = "silent"
            config_verbose = int(CONFIG[CONFIG['mqtt_topics'][path]]['verbose'])
            # logger.info("verbose: {}".format(config_verbose))
            if  config_verbose == 1:
                is_verbose = "verbose"

            is_active = "not active"
            config_influx_active = CONFIG[CONFIG['mqtt_topics'][path]].getboolean( 'do_write_to_influx')
            # logger.info("active: {}".format(config_influx_active))
            if config_influx_active is True:
                is_active = "activated"
            logger.info("Connected {:.<31} {:.<30} {:.<10} {}".format(path+' ', CONFIG['mqtt_topics'][path]+' ',\
                    is_verbose+' ', is_active))
        except Exception as e:
            logger.exception("  Error connecting to mqtt")
            exit (2)
    # Subscribe all
    # mqtt_client.subscribe("/#")

def on_message(mqtt_client, userdata, msg):
    '''Default Handler for Processing message that aren't caught otherwhere'''
    logger.debug("Unregistered topic: {}".format(msg.topic))

if 'mqtt_topics' not in CONFIG:
    logger.error("Error no secion for 'mqtt_topics' found in pathconfig")
    exit (1)


def main():
    # for some reason logging is configured in config.py
    logger.info("starting daemon")
    # sys.stderr.write("here is stderr\n")

    mqtt_client = mqtt.Client()
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    #
    mqtt_client.connect(args.mqtt_host, args.mqtt_port, keepalive=60)
    #
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    while True:
        try:
            mqtt_client.loop_forever()
        except KeyboardInterrupt:
            print ("\b\b\nExit: user pressed control-c\n")
            logger.info("\b\b\nExit: user pressed control-c\n")
            exit (0)
        except InfluxDBServerError:
            logger.error("Connection Error when contacting influx daemon")
            sleep (5)
            logger.error("Continuing after 5 s")

if __name__ == '__main__':
    main()
