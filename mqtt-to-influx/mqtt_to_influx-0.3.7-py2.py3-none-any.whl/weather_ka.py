# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# pylint: disable=unused-argument
# }}}
import json
import logging
from mqtt_to_influx.config import CONFIG
from mqtt_to_influx.rel_h_t_abs import rel_hum_to_abs_hum
from mqtt_to_influx.influx_client import influx_client

logger = logging.getLogger(__name__)

class Process_mqtt_message:
    def __init__(self, mqtt_client, userdata, msg):
        configname = __name__.split('.')[1]
        logger.debug(configname)
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info("processing: {: <30}{}".format(msg.topic, msg.payload.decode()))
        message_type = msg.topic.split("/")[3]

        # Ignore STATE messages for now
        if message_type == "STATE":
            return None
    
        device_name = msg.topic.split("/status")[0].lstrip("/").replace("/",".")

        # make sure we have a json object
        try:
            payload_json = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            return None
        if int(CONFIG[configname].get('verbose', 0)) > 1:
            logger.info ("payload_json: ")
            logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))

        # friendly_name = msg.topic.split("/status/")[1]
        # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        try:
            for (k,v) in payload_json.items():
                # logger.info ("key: %s - value: %s" % (k,v))
                payload_json[k]=float(v)
                # logger.info ("key: %s - value: %s" % (k,payload_json[k]))
        except ValueError as e:
            # logger.exception("Exception")
            pass
            # print (str(e))
        # Derive the absolute humidity
        try:
            abs_hum = rel_hum_to_abs_hum(temperature = float(payload_json["data"]["Lufttemperatur"]),
                                         humidity    = float(payload_json["data"]["Luftfeuchtigkeit"]))
            payload_json["data"]["Absolute_Humidity"] = abs_hum

        except KeyError as e:
            logger.info (F"Key error in {__name__}: {e}\n{msg.topic} - {msg.payload}")
            logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
            return None
        except Exception as e:
            logger.info (F"uncaught exception: processing {msg.topic} - {msg.payload}\n    {e}")

# /sensor/arno/SENSOR {"Time":"2019-10-27T21:21:51","DS18B20":{"Temperature":21.2},"TempUnit":"C"}
        try:
            json_body = [
                    { # sensor.4
                    "measurement": str(device_name),
                    "fields": payload_json["data"] 
                }
            ]
            if CONFIG[configname].getboolean('do_write_to_influx'):
                influx_client.write_points(json_body)
            if int(CONFIG[configname].get('verbose', 0)) > 0:
                logger.info ("output json for storage in influx:")
                logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            if int(CONFIG[configname].get('verbose', 0)) > 0:
                logger.info("------\n")
        except Exception as e:
            logger.exception("")

        return None

# print(F"{__name__} imported")
