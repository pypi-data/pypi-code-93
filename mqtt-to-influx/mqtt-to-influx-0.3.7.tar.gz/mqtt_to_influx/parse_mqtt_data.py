#!/usr/bin/env python3
# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# }}}

import os
import sys
import datetime
import json
import logging
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

logger = logging.getLogger(__name__)
        
debug = 1

class ParseMqttData:
    '''Class for influx Data'''
    def __init__(self, msg):
        '''init'''
        self.msg = msg
        self.msg_type = None

        try:
            self.msg_json = json.loads(msg.payload.decode())
            if (msg.payload[0] == ord('{')):
                self.is_json = True
            else:
                self.is_json = False
        except:
            self.is_json = False

        if self.is_json:
            if ((msg.topic.split("/")[1] in ('homegear')) and (msg.topic.split("/")[3] in ('jsonobj'))):
                self.msg_type = "homegear"
            elif (msg.topic.split("/")[-1] in ("STATE", "SENSOR")):
                self.msg_type = "tasmota"
        else:
            if (msg.topic.split("/")[1] in ('sensor', 'luefter', 'door')):
                self.msg_type = "mh_sensor_v1"

        if debug:
            logger.info ("Detected a {} message".format(self.msg_type))
            if (self.msg_type in ( None, 'tasmota', 'homegear', 'mh_sensor_v1')):
                logger.info ("  topic[-1]:      {} ".format(msg.topic.split("/")[-1]))
                if not self.is_json:
                    logger.info ("  topic:message: {: <38}{}".format(msg.topic, msg.payload))

                if self.is_json:
                    logger.info ("  json")
                    logger.info(json.dumps(self.msg_json, sort_keys=True, indent=4, separators=(',', ': ')))
        

