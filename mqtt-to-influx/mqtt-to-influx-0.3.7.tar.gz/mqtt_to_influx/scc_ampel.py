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
import paho.mqtt.client as mqtt
from time import sleep

logger = logging.getLogger(__name__)

class Process_mqtt_message:
    def __init__(self, mqtt_client, userdata, msg):
        configname = __name__.split('.')[1]
        logger.debug(configname)
        verbose=int(CONFIG[configname].get('verbose', 0))
        if verbose > 0:
            logger.info("processing: {: <30}: {}".format(msg.topic, msg.payload.decode()))

        device_name        = msg.topic.split("/")[1]\
                        .lstrip("/")
        measurement_sensor = msg.topic.split("/")[2]\
                        .lstrip("/")
        measurement_key= msg.topic.split("/")[3]\
                        .lstrip("/")
        try:
            measurement_value = float(msg.payload.decode())
        except:
            raise

        logger.info(F"device_name:{device_name} - sensor: {measurement_sensor} - key: {measurement_key} - value: {measurement_value}")

        # Convert ESP IDs to Room Names:
        room_name = CONFIG.get(configname, device_name, fallback=device_name)

        try:
            json_body = [
                    { 
                    "measurement": F"{measurement_sensor}",
                    "fields": {
                        F"{measurement_key}": measurement_value,
                        },
                    "tags": {
                        "room": room_name,
                        "device": "co2ampel",
                        "espid": device_name,
                        }
                }
            ]
            logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
            if CONFIG[configname].getboolean('do_write_to_influx'):
                if influx_client.write_points(json_body):
                    if verbose > 0:
                        logger.info("Success writing to influx")
                else:
                    logger.error(F"Error writing points to influxdb")
            if verbose > 0:
                logger.info ("just wrote this output json for storage in influx:")
                logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        except KeyError as e:
            logger.error(F"Key Error; {e}")


        # make sure we have a json object
        #  try:
        #      payload_json = json.loads(msg.payload.decode())
        #  except json.decoder.JSONDecodeError:
        #      return None
        #  if verbose > 1:
        #      logger.info ("payload_json: ")
        #      logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        #
        #  # friendly_name = msg.topic.split("/status/")[1]
        #  # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        #  try:
        #      for (k,v) in payload_json.items():
        #          # logger.info ("key: %s - value: %s" % (k,v))
        #          payload_json[k]=float(v)
        #          # logger.info ("key: %s - value: %s" % (k,payload_json[k]))
        #  except ValueError as e:
        #      # This is pbrobably just a time value
        #      # logger.warning(F"ValueError: '{e}'")
        #      pass
        #      # logger.info (str(e))
        #
        #  try:
        #      abs_hum = rel_hum_to_abs_hum(temperature = float(payload_json["AM2301"]["Temperature"]),
        #                                   humidity    = float(payload_json["AM2301"]["Humidity"]))
        #  except KeyError as e:
        #      logger.info (F"Key error in {__name__}: {e}\n{msg.topic} - {msg.payload}")
        #      return None
        #  except Exception as e:
        #      logger.error(F"uncaught exception: processing {msg.topic} - {msg.payload}\n    {e}")
        #      logger.error("    going to fix this with a power cycle of the sensor")
        #      #FIXME: Power cycle the sensor!
        #      # marcus@nemo:~$ echo "OFF" | mosquitto_pub -q 1 -h q -l -t /sensor/4/cmnd/POWER1
        #      mhiot_mqtt_pub('/sensor/4/cmnd/POWER2', "OFF", clientid='mqtt-to-influx', repeat=2)
        #      time.sleep(3)
        #      # marcus@nemo:~$ echo "ON" | mosquitto_pub -q 1 -h q -l -t /sensor/4/cmnd/POWER2
        #      mhiot_mqtt_pub('/sensor/4/cmnd/POWER2', "ON", clientid='mqtt-to-influx', repeat=3)
        #      time.sleep(3)
        #      return None
        #
        #  # logger.info (F"abs_hum: {abs_hum}")
        #  payload_json["AM2301"]["Absolute_Humidity"] = abs_hum
        #  try:
        #      json_body = [
        #              { # sensor.4
        #              "measurement": str(device_name),
        #              "fields": payload_json["AM2301"]
        #          }
        #      ]
        #      # logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        #      # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        #      if CONFIG[configname].getboolean('do_write_to_influx'):
        #          if influx_client.write_points(json_body):
        #              if verbose > 0:
        #                  logger.info("Success writing to influx")
        #          else:
        #              logger.error(F"Error writing points to influxdb")
        #      if verbose > 0:
        #          logger.info ("just wrote this output json for storage in influx:")
        #          logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        #      if verbose > 0:
        #          logger.info("------\n")
        #  except Exception as e:
        #      logger.error(str(e))

        return None

# logger.info(F"{__name__} imported")
