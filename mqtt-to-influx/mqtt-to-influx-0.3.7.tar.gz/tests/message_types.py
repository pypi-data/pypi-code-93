# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace, invalid-name, missing-docstring
import unittest
import json
import sys
from copy import deepcopy
import paho.mqtt.client as mqtt
# import paho.mqtt.client.MQTTMessage as MQTTMessage
from mqtt_to_influx.parse_mqtt_data import ParseMqttData

is_py2 = sys.version[0] == '2'


class check_type_detction(unittest.TestCase):
    def test_mh_sensors_v1_1(self):
        msg = mqtt.MQTTMessage
        msg.topic   = "/luefter/2/status/dht_temp/"
        msg.payload = "21.10"
        parsed_mqtt_data= ParseMqttData(msg)
        self.assertEqual("mh_sensor_v1", parsed_mqtt_data.msg_type)
    def test_mh_sensors_v1_2(self):
        # pylint: disable=too-many-statements
        msg = mqtt.MQTTMessage
        msg.topic   = "/luefter/2/status/dht_temp/"
        msg.payload = "21.10"
        parsed_mqtt_data= ParseMqttData(msg)



if __name__ == '__main__':
    unittest.main()

