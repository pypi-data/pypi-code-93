# https://github.com/sacOO7/socketcluster-client-python
from socketclusterclient import Socketcluster
# https://github.com/titouandk/emitter.py
from emitter import Emitter

from uuid import uuid4
from threading import Thread, Lock
from . import constants
from . import proto
from . import __version__
import os
from google.protobuf import message as _message
import base64
import traceback
import time
import socket as sock
import json
import re
from inspect import signature
from typing import Optional, Type, Union, Callable


# The "official" socketcluster client doesn't respond to ping... let's fix that

class FixedSocketClusterClient(Socketcluster.socket):

    def on_message(self, ws, message):
        if message == "#1":
            ws.send("#2")
        return super().on_message(ws, message)


class RTIClient(Emitter):

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        if self.connected and not self.incognito:
            self._publish_state()

    @property
    def own_channel_prefix(self):
        return f"@{self.client_id}:"

    @property
    def auth_token(self):
        return self.socket.getAuthtoken()

    def __init__(self, application: str = "python", 
            application_version: Optional[str] = None, client_id: Optional[str] = None, 
            federation: Optional[str] = None, host: Optional[str] = None, station: Optional[str] = None, 
            secret: Optional[str] = None, user: Optional[str] = None, participant: Optional[str] = None, 
            role: Optional[str] = None, full_name: Optional[str] = None, password: Optional[str] = None, 
            incognito: bool = False, passive: bool = False, connect: bool = True):
        super().__init__()

        self.measurement_interval_time_scale = 1

        self.subscriptions = {}
        self.known_channels = {}
        self.used_channels = {}
        self.known_clients = {}
        self.used_measures = {}
        self.known_measures = {}

        self._state = proto.UNKNOWN
        self.connected = False
        self.broker_version = None

        url = None
        if not url:
            url = os.environ.get('GEISTT_RTI_URL')
        if not url:
            url = constants.default_url
        self.url = url

        self.application = application
        self.application_version = application_version
        self.client_id = client_id
        if not self.client_id:
            self.client_id = str(uuid4())
        self.federation = federation
        if not self.federation:
            self.federation = os.environ.get('GEISTT_RTI_FEDERATION')
        if self.federation:
            # slashes quietly not allowed in federation id
            self.federation = self.federation.replace("/", "_")

        auth_secret = None
        if not auth_secret:
            auth_secret = os.environ.get('GEISTT_RTI_SECRET')
        if not auth_secret:
            auth_secret = secret
        self.user = user

        self._host = host
        if not self._host:
            self._host = os.environ.get('GEISTT_RTI_HOST')
        if not self._host:
            self._host = sock.gethostname()
        self._station = station
        if not self._station:
            self._station = os.environ.get('GEISTT_RTI_STATION')
        self.participant = participant
        self.role = role
        self.full_name = full_name

        self.incognito = incognito
        self.passive = passive

        auth_token = {
            'application': self.application,
            'clientId': self.client_id,
            'clientLibraryVersion': __version__
        }
        if auth_secret:
            auth_token['secret'] = auth_secret
        if user:
            auth_token['user'] = user
        if password:
            auth_token['password'] = password
        if self.federation:
            auth_token['federation'] = self.federation
        self._auth_token_data = auth_token

        socket = FixedSocketClusterClient(url)
        socket.setdelay(2)
        socket.setreconnection(True)

        def on_connect(socket):
            pass

        def on_disconnect(socket):
            self.connected = False
            self.socket.authToken = None
            self.emit("disconnect")

        def on_fail(socket, error):
            self.emit("error", "fail", error, None)

        def on_connection_error(socket, error):
            self.emit("error", "connection", error, None)

        def on_set_auth(socket, token):
            socket.setAuthtoken(token)
            self.subscribe(constants.clients_channel, proto.Clients, on_clients)
            self.subscribe(constants.channels_channel, proto.Channels, on_channels)
            self.subscribe(constants.measures_channel, proto.Measures, on_measures)
            if self.federation:
                self.publish_text(
                    constants.federations_channel, self.federation)
                self.subscribe_text(
                    constants.federations_channel, on_federations)
            for channel_name in self.subscriptions:
                socket.subscribe(channel_name)
            if not self.connected:
                if not self.incognito:
                    self._publish_client()
                self.connected = True
                self.emit("connect")

        def on_auth(socket, is_authenticated):
            socket.emit("auth", auth_token)

        def on_clients(message: proto.Clients):
            if message.HasField("request_clients") and not self.incognito:
                self._publish_client()
            elif message.HasField("client"):
                self.known_clients[message.client.id] = message.client
            elif message.HasField("register_participant"):
                reg = message.register_participant
                if (reg.client_id == self.client_id or not reg.client_id) and (reg.host == self._host or not reg.host) and (reg.station == self._station or not reg.station) and (reg.participant != self.participant or reg.role != self.role):
                    self.participant = reg.participant
                    self.role = reg.role
                    self.full_name = reg.full_name
                    self._publish_client()

        def on_channels(message: proto.Channels):
            if message.HasField("request_channel_usage"):
                message = proto.Channels()
                message.channel_usage.client_id = self.client_id
                message.channel_usage.usage.extend(self.used_channels.values())
                if not self.incognito:
                    self.publish(constants.channels_channel, message)
            elif message.HasField("channel_usage"):
                for use in message.channel_usage.usage:
                    self.known_channels[use.channel.name] = use.channel
            elif message.HasField("channel"):
                self.known_channels[message.channel.name] = message.channel

        def on_measures(message: proto.Measures):
            if message.HasField("request_measures") and not self.incognito:
                self._publish_measures()
            elif message.HasField("measure"):
                self.known_measures[message.measure.id] = message.measure

        def on_federations(message: str):
            if message == "?":
                self.publish_text(
                    constants.federations_channel, self.federation)

        def on_broker_version(channel: str, content: str):
            self.broker_version = content

        socket.setBasicListener(on_connect, on_disconnect, on_connection_error)
        socket.setAuthenticationListener(on_set_auth, on_auth)
        socket.on("fail", on_fail)
        socket.on("broker-version", on_broker_version)
        self.socket = socket
        self.thread = None
        self.collect_measurements_thread = None
        self.collect_lock = Lock()
        self.collect_queue = {}
        self.last_collect = {}
        if connect:
            self.connect()

        # socketcluster python client provides no event emit for #removeAuthToken when token expires...
        # so let's spawn a thread and check for it
        def check_auth():
            while True:
                time.sleep(1)
                if self.connected and self.socket.authToken is None:
                    self.socket.emit("auth", self._auth_token_data)
        self.check_auth_thread = Thread(target=check_auth)
        self.check_auth_thread.daemon = True
        self.check_auth_thread.start()


    def connect(self):
        self.thread = Thread(target=self.socket.connect)
        self.thread.daemon = True
        self.thread.start()

    def disconnect(self):
        self.socket.disconnect()
        self.connected = False
        self.emit("disconnect")

    def wait_until_connected(self):
        count = 0
        while count < 500 and not self.connected:
            count += 1
            time.sleep(0.01)
        return self.connected

    def verify_token(self, token: str, handler: Callable[[dict], None]):
        def handle_result(socket, content):
            handler(content)
            self.socket.off("verifytoken")
        self.socket.on("verifytoken", handle_result)
        self.socket.emit("verifytoken", token)

    def subscribe(self, channel_name: str, message_class: Type[_message.Message], handler: Callable, register: bool = True):
        def handle_message(content):
            message = self.parse(message_class, content)
            if len(signature(handler).parameters) < 2:
                handler(message)
            else:
                handler(channel_name, message)
        return self.subscribe_text(channel_name, handle_message, register, str(message_class))

    @classmethod
    def parse(cls, message_class, content):
        message = message_class()
        message.ParseFromString(base64.b64decode(content))
        return message

    def subscribe_json(self, channel_name: str, handler: Union[Callable[[str, dict], None], Callable[[dict], None]], register=True):
        def handle_message(content):
            if len(signature(handler).parameters) < 2:
                handler(json.loads(content))
            else:
                handler(channel_name, json.loads(content))
        return self.subscribe_text(channel_name, handle_message, register, "json")

    def subscribe_text(self, channel_name: str, handler: Union[Callable[[str, str], None], Callable[[str], None]], register: bool = True, data_type: str = "text"):
        socket_channel_name = channel_name
        if self.federation and channel_name != constants.federations_channel:
            socket_channel_name = "//" + self.federation + "/" + channel_name
        if (socket_channel_name not in self.subscriptions):
            if self.connected:
                self.socket.subscribe(socket_channel_name)
            self.subscriptions[socket_channel_name] = []
            if register: self._register_channel(channel_name, False, data_type)

            def handle_message(in_channel_name, content):
                for listener in self.subscriptions[socket_channel_name]:
                    try:
                        if len(signature(listener).parameters) < 2:
                            listener(content)
                        else:
                            listener(channel_name, content)
                    except Exception as e:
                        self.emit("error", channel_name, e,
                                  traceback.format_exc())
            self.socket.onchannel(socket_channel_name, handle_message)

        self.subscriptions[socket_channel_name].append(handler)
        return handler

    def unsubscribe(self, channel_name_or_handler: Union[str, Callable[[str], None]]) -> None:
        if channel_name_or_handler is str:
            if self.federation and channel_name_or_handler != constants.federations_channel:
                channel_name_or_handler = "//" + self.federation + "/" + channel_name_or_handler
            self.socket.unsubscribe(channel_name_or_handler)
            if channel_name_or_handler in self.subscriptions:
                del self.subscriptions[channel_name_or_handler]
        else:
            for channel_name in self.subscriptions:
                if channel_name_or_handler in self.subscriptions[channel_name]:
                    self.subscriptions[channel_name].remove(
                        channel_name_or_handler)
                    if len(self.subscriptions[channel_name]) <= 0:
                        self.socket.unsubscribe(channel_name)
                        del self.subscriptions[channel_name]
                        break

    def publish(self, channel_name: str, message: _message.Message) -> None:
        self._register_channel(
            channel_name, True, data_type=str(type(message)))
        content = base64.b64encode(
            message.SerializeToString()).decode("utf8")
        if self.federation and not channel_name.startswith("@"):
            channel_name = "//" + self.federation + "/" + channel_name
        self.socket.publish(channel_name, content)

    def publish_text(self, channel_name: str, content: str) -> None:
        self._register_channel(channel_name, True, data_type="text")
        if self.federation and not channel_name.startswith("@") and channel_name != constants.federations_channel:
            channel_name = "//" + self.federation + "/" + channel_name
        self.socket.publish(channel_name, content)

    def publish_json(self, channel_name: str, message: object) -> None:
        self._register_channel(channel_name, True, data_type="json")
        if self.federation and not channel_name.startswith("@") and channel_name != constants.federations_channel:
            channel_name = "//" + self.federation + "/" + channel_name
        self.socket.publish(channel_name, json.dumps(message))

    def publish_error(self, error_message: str, runtime_state: proto.RuntimeState = None) -> None:
        message = proto.RuntimeControl()
        message.error.client_id = self.client_id
        message.error.message = str(error_message)
        if runtime_state is not None:
            message.error.state = runtime_state
        self.publish(constants.control_channel, message)

    def publish_heartbeat(self) -> None:
        message = proto.Clients()
        message.heartbeat.client_id = self.client_id
        self.publish(constants.clients_channel, message)

    def publish_progress(self, progress: int) -> None:
        message = proto.Clients()
        message.progress.client_id = self.client_id
        message.progress.progress = int(progress)
        self.publish(constants.clients_channel, message)

    def publish_value(self, value: Union[int, float, str], highlight: bool = False, error: bool = False) -> None:
        message = proto.Clients()
        message.value.client_id = self.client_id
        message.value.value = str(value)
        message.value.highlight = highlight
        message.value.error = error
        self.publish(constants.clients_channel, message)

    def _publish_client(self):
        message = proto.Clients()
        message.client.id = self.client_id
        message.client.application = self.application
        message.client.state = self._state
        message.client.passive = self.passive
        message.client.client_library_version = __version__
        if self.application_version:
            message.client.application_version = self.application_version
        if self._host:
            message.client.host = self._host
        if self._station:
            message.client.station = self._station
        if self.user:
            message.client.user = self.user
        if self.participant:
            message.client.participant = self.participant
        if self.role:
            message.client.role = self.role
        if self.full_name:
            message.client.full_name = self.full_name
        self.publish(constants.clients_channel, message)

    def _publish_measures(self):
        for measure in self.used_measures.values():
            message = proto.Measures()
            message.measure.CopyFrom(measure)
            self.publish(constants.measures_channel, message)

    def _publish_state(self):
        message = proto.RuntimeControl()
        message.state.client_id = self.client_id
        message.state.state = self._state
        self.publish(constants.control_channel, message)

    def _register_channel(self, channel_name, publish, data_type=None):
        if channel_name.startswith("@"):
            return
        channel = proto.Channel()
        channel.name = channel_name
        data_type = re.sub("<class.*_pb2\\.", "", data_type)
        data_type = re.sub("'>", "", data_type)
        channel.data_type = data_type
        use = None
        if channel_name not in self.used_channels:
            use = proto.ChannelUse()
            use.channel.CopyFrom(channel)
            self.used_channels[channel_name] = use
        else:
            use = self.used_channels[channel_name]
        if publish:
            use.publish = True
        else:
            use.subscribe = True
        if channel_name not in self.known_channels:
            self.known_channels[channel_name] = channel
            if self.connected and not self.incognito:
                message = proto.Channels()
                message.channel.CopyFrom(channel)
                self.publish(constants.channels_channel, message)

    def register_measure(self, measure: proto.Measure) -> None:
        measure.application = self.application
        self.used_measures[measure.id] = measure
        if measure.id not in self.known_measures:
            self.known_measures[measure.id] = measure
            if self.connected and not self.incognito:
                message = proto.Measures()
                message.measure.CopyFrom(measure)
                self.publish(constants.measures_channel, message)
    
    def measure(self, measure_id: Union[str, proto.Measure], value: float) -> None:
        measure = None
        if type(measure_id) is str:
            measure = self.used_measures.get(measure_id)
            if not measure: measure = self.known_measures.get(measure_id)
            if not measure:
                measure = proto.Measure()
                measure.id = measure_id
                measure.application = self.application
        else:
            measure = measure_id

        if measure.id not in self.used_measures: self.register_measure(measure)
        if measure.interval > 1e-5:
            if not self.collect_measurements_thread: 
                self.collect_measurements_thread = Thread(target=self._collect_measurements_thread_func)
                self.collect_measurements_thread.daemon = True
                self.collect_measurements_thread.start()
            with self.collect_lock:
                if measure.id not in self.collect_queue: self.collect_queue[measure.id] = []
                self.collect_queue[measure.id].append(value)
        else:
            measurement = proto.Measurement()
            measurement.measure_id = measure.id
            measurement.client_id = self.client_id
            measurement.value = value
            channel = measure.channel if measure.channel else constants.measurement_channel
            if self.connected: self.publish(channel, measurement)
    
    def _collect_measurements_thread_func(self):
        while self.connected:
            time.sleep(0.1)
            with self.collect_lock:
                for measure_id, values in self.collect_queue.items():
                    if measure_id not in self.last_collect: 
                        self.last_collect[measure_id] = time.time()
                    else:
                        measure = self.known_measures[measure_id]
                        if (time.time() - self.last_collect[measure_id]) * self.measurement_interval_time_scale > measure.interval:
                            channel = measure.channel if measure.channel else constants.measurement_channel
                            measurement = proto.Measurement()
                            measurement.measure_id = measure.id
                            measurement.client_id = self.client_id
                            if len(values) == 1:
                                measurement.value = values.pop()
                                self.publish(channel, measurement)
                            elif len(values) > 1:
                                window = proto.Measurement.Window()
                                window.max = -float("inf")
                                window.min = float("inf")
                                while len(values) > 0:
                                    value = values.pop()
                                    window.count += 1
                                    window.mean += value
                                    if value > window.max: window.max = value
                                    if value < window.min: window.min = value
                                if window.count > 0: window.mean /= window.count
                                window.duration = (time.time() - self.last_collect[measure_id]) * self.measurement_interval_time_scale
                                measurement.window.CopyFrom(window)
                                self.publish(channel, measurement)
                            self.last_collect[measure_id] = time.time()
