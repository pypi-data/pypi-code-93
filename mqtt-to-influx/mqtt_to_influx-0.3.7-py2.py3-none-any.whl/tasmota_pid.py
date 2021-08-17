# pylint
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# pylint: disable=logging-fstring-interpolation

import json
import logging
from mqtt_to_influx.config import CONFIG
from mqtt_to_influx.rel_h_t_abs import rel_hum_to_abs_hum
from mqtt_to_influx.influx_client import influx_client

logger = logging.getLogger(__name__)

class Process_mqtt_message:
    def __init__(self, mqtt_client, userdata, msg):
        configname = __name__.split('.')[1]
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info(configname)
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info("processing: {: <30}{}".format(msg.topic, msg.payload.decode()))
        message_type = msg.topic.split("/")[3]
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logging.info(F"message type: '{message_type}'")

    
        device_name = msg.topic.split("/"+message_type)[0].lstrip("/").replace("/",".")
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info (F"DEVICE_NAME {device_name}")

        # make sure we have a json object
        json_body=None
        try:
            payload_json = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            logger.error(F"Cannot JSON decode message >>{msg.payload.decode()}<<")
            return None
        if int(CONFIG[configname].get('verbose', 0)) > 1:
            logger.info ("payload_json: ")
            logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))


        # convert values to float
        try:
            for (k,v) in payload_json.items():
                # logger.info ("key: %s - value: %s" % (k,v))
                payload_json[k]=float(v)
                # logger.info ("key: %s - value: %s" % (k,payload_json[k]))
        except ValueError as e:
            pass
            # logger.info (str(e))

        if message_type == "SENSOR":
            logger.debug ("SENSOR message obtained")
            try:
                json_body = [
                        {
                        "measurement": str(device_name),
                        "fields": {
                            "Temperature": payload_json["DS18B20"]["Temperature"],
                            "PID_Power": payload_json["PID"]["PidPower"],
                            "Setpoint": payload_json["PID"]["PidSp"]
                        }
                    }
                ]
            except KeyError as e:
                logger.info ("KeyError: " + str(e))
            except Exception as e:
                logger.info (str(e))

        elif message_type == "RESULT":
            try:
                json_body = [
                    {
                        "measurement": str(device_name),
                        "fields": {
                            "Setpoint": payload_json["PidSp"]
                        }
                    }
                ]
            except KeyError as e:
                logger.info ("KeyError: " + str(e))


        elif message_type == "STATE":
            try:
                power_value = 0
                if payload_json["POWER"] == "ON":
                    power_value = 1
                json_body = [
                        {
                        "measurement": str(device_name),
                        "fields": {
                            "Power": power_value
                        }
                    }
                ]
            except KeyError as e:
                logger.info ("KeyError: " + str(e))
            except Exception as e:
                logger.info (str(e))

        elif message_type == "PID":  # deprecated
            try:
                json_body = [
                        {
                        "measurement": str(device_name),
                        "fields": {
                            "PID_Power": payload_json["power"]
                        }
                    }
                ]
            except KeyError as e:
                logger.info ("KeyError: " + str(e))
            except Exception as e:
                logger.info (str(e))

        elif message_type == "RESULT":
        # /sensor/5/LOGGING 21:03:12 MQT: /sensor/5/RESULT = {"PID_SP":"30.00"}
            try:
                if payload_json["PID_SP"] is not None:
                    logger.info(payload_json)
                    json_body = [
                            { 
                            "measurement": str(device_name),
                            "fields": {
                                "Setpoint": payload_json["PID_SP"]
                            }
                        }
                    ]
            except KeyError as e:
                logger.info ("KeyError: " + str(e))
            except Exception as e:
                logger.error (str(e))

        # logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        if CONFIG[configname].getboolean('do_write_to_influx') and json_body:
            influx_client.write_points(json_body)
            if int(CONFIG[configname].get('verbose', 0)) > 0:
                logger.info("wrote to influx")
        if int(CONFIG[configname].get('verbose', 0)) > 0 and json_body:
            logger.info ("output json for storage in influx:")
            logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info("------------------------")

        return None

# logger.info(F"{__name__} imported")
