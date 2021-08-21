import time

# import paho.mqtt.client as mqtt
import json

import paho.mqtt.client as mqttClient
from ndu_gate_camera.utility import constants


class ResultHandlerMqtt:
    '''
        Cihaz verilerinin NDU platformuna MQTT APİ üzerinden gönderilmesi
    '''

    def __init__(self, access_token, mqtt_obj):
        host = mqtt_obj.get("host")

        self.connected_devices = {}

        self.client = mqttClient.Client()
        self.client.username_pw_set(access_token)
        # Connect to ThingsBoard using default MQTT port and 60 seconds keepalive interval
        try:
            self.client.connect(host, mqtt_obj.get("port"), 60)
            self.client.loop_start()
        except:
            print("can not connect mqtt broker!")
            # TODO - bağlanamasa belli aralıklara bağlanmayı tekrar denesin, bağlanamadığ sırada veri gelirse o veriyi hafızada belirli bir süre/miktar tutmalı.
            #  bağlantı oluşur oluşmaz bu biriken veriler de gönderilmelidir.

    def send_connect_request(self, device_name):
        mqtt_data = {"device": device_name}
        self.client.publish('v1/gateway/connect', json.dumps(mqtt_data), 1)
        self.connected_devices[device_name] = True

    def send_disconnect_request(self, device_name):
        mqtt_data = {"device": device_name}
        self.client.publish('v1/gateway/disconnect', json.dumps(mqtt_data), 1)
        self.connected_devices.pop(device_name)

    def save_result(self, results, device=None, runner_name=None, data_type='telemetry'):
        if self.connected_devices.get(device) is None:
            self.send_connect_request(device)

        if data_type == 'telemetry':
            self.send_telemetry(device, results)
        elif data_type == 'attribute':
            self.send_attribute(device, results)

    def send_telemetry(self, device, results):
        try:
            mqtt_data = {
                device: []
            }
            # if mqtt_data.get(device) is None:
            #     mqtt_data['device'] = 'device'

            for result in results:
                if result is None:
                    continue
                data = result.get(constants.RESULT_KEY_DATA, None)

                if data is None:
                    continue

                single_data = {}
                for key in data:
                    if data[key] is not None:
                        single_data[key] = data[key]

                mqtt_data[device].append(single_data)
            if not len(mqtt_data[device]) == 0:
                self.client.publish('v1/gateway/telemetry', json.dumps(mqtt_data), 1)
        except KeyError:
            print('Exception while saving result, key error')

    def send_attribute(self, device, results):
        try:
            mqtt_data = {
                device: {}
            }

            for result in results:
                if result is None:
                    continue
                data = result.get(constants.RESULT_KEY_DATA, None)

                if data is None:
                    continue

                for key in data:
                    if data[key] is not None:
                        mqtt_data[device][key] = data[key]

            if not len(mqtt_data[device]) == 0:
                self.client.publish('v1/gateway/attributes', json.dumps(mqtt_data), 1)
        except KeyError:
            print('Exception while saving result, key error')

    def dispose(self):
        # TODO - disconnect devices
        pass
