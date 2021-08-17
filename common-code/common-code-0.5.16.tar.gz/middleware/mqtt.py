import json
import uuid
import paho.mqtt.client as mqtt
from common.logging_config import logger
from common.utility.base import get_uuid


def mqtt_decorator(function):
    def wrapper(obj, *args, **kwargs):
        assert hasattr(obj, "client"), "No connection to mqtt server"
        return function(obj, *args, **kwargs)

    return wrapper


class MQTTClient:
    # _instance_lock = threading.Lock()
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         with MQTTClient._instance_lock:
    #             if not hasattr(cls, '_instance'):
    #                 MQTTClient._instance = super().__new__(cls)
    #
    #         return MQTTClient._instance
    #     else:
    #         raise Exception('不能实例化多个类')

    def __init__(self, on_connect=None, on_message=None, on_subscribe=None, resub=True):
        self._on_connect = on_connect if on_connect else self.on_connect
        self._on_message = on_message if on_message else self.on_message
        self._on_subscribe = on_subscribe if on_subscribe else self.on_subscribe
        self.sub_topics = []
        self.resub = resub
        self._obj_init = True

    @mqtt_decorator
    def mqtt_publish(self, topic, data):
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        self.client.publish(topic, payload=data, qos=0)

    @mqtt_decorator
    def mqtt_subscribe(self, topic):
        self.client.subscribe(topic)
        self.sub_topics.append(topic)
        logger.debug("subscribe topic", topic)

    def on_connect(self, client, userdata, flags, rc):
        if self.resub and self._obj_init is False:
            for topic in self.sub_topics:
                self.client.subscribe(topic)
            logger.debug("resub topic ", self.sub_topics)
        self._obj_init = False
        logger.debug("Connected with result code: " + str(rc))

    def on_message(self, client, userdata, msg):
        logger.debug(msg.topic + " " + str(msg.payload))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logger.debug("On Subscribed: qos = {qos}".format(qos=granted_qos))

    def connect_mtqq(
        self, host=None, port=2883, client_id="", username=None, password=None, keepalive=600, describe=""
    ):
        if not client_id:
            client_id = get_uuid()
        logger.info(host, port, client_id, keepalive, describe)
        client = mqtt.Client(client_id)
        client.username_pw_set(username=username, password=password)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_subscribe = self._on_subscribe
        client.connect(host, port, keepalive)  # 600为keepalive的时间间隔
        self.client = client
        self.loop_forever()
        return client

    def loop_forever(self):
        from threading import Thread

        Thread(target=self.start).start()
        logger.debug("setting mqtt loop_forever")

    def start(self):
        self.client.loop_forever()  # 保持连接

    def get_uuid(self):
        uid = str(uuid.uuid4())
        suid = "".join(uid.split("-"))
        return suid


if __name__ == "__main__":
    mqtt_client = MQTTClient()
    # mqtt_client.connect_mtqq(
    #     host=config.agentmqtt.server,
    #     port=config.agentmqtt.port,
    #     username=config.agentmqtt.username,
    #     password=config.agentmqtt.password,
    #     describe="norm series  start norm series",
    # )
    mqtt_client.mqtt_subscribe("sd")
