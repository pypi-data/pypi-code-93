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
from mqtt_to_influx.influx_client import influx_client

logger = logging.getLogger(__name__)

class Process_mqtt_message:
    def __init__(self, mqtt_client, userdata, msg):
        configname = __name__.split('.')[1]
        logger.debug(configname)
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info("processing: {: <30}{}".format(msg.topic, msg.payload.decode()))

          # 1 "Entkleide"
          # 2 "Wohnzimmer"
          # 3 "Kueche vorn"
          # 4 "Kueche hinten"
          # 5 "Gaestezimmer"
          # 6 "Bad"
        ## FIXME: We can get the device names from homegear...
        devices=[" ", "Entkleide" , "Wohnzimmer" , "Kueche vorn" , "Kueche hinten" , "Gaestezimmer" , "Bad", "Kueche vorn neu"]
        device_num     = msg.topic.split("/")[4]
        device_channel = int(msg.topic.split("/")[5])
        if device_channel < 0:
            return None

        try:
            device_name  = devices[int(device_num)]
        except IndexError as e:
            device_name = "unknown"
            logger.info("Error with device number {}".format(device_num))
            logger.exception(e)

        # make sure we have a json object
        try:
            payload_json = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            return None
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            logger.info ("payload_json: ")
            logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))

        # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        try:
            for (k,v) in payload_json.items():
                payload_json[k]=float(v)
        except ValueError as e:
            pass
        except TypeError as e:
            pass
            # logger.exception(e)

        try:
            json_body = [
                {
                    "measurement": str(device_name),
                    "fields": payload_json 
                }
            ]
            # logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            # logger.info(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
            if CONFIG[configname].getboolean('do_write_to_influx'):
                influx_client.write_points(json_body)
            else: 
                if int(CONFIG[configname].get('verbose', 0)) > 1:
                    logger.info(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception as e:
            logger.error("tried to write: {}".format(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': '))))
            logger.exception (str(e))

        return None
