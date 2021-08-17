import platform
import subprocess
from os import path, environ
from typing import Optional

from .connection import start_connection, CustomConnection
from .objects import *


def get_proxy_name():
    machine = platform.machine().lower()
    if "armv7" in machine:
        return "proxy-armv7"
    if "arm64" in machine or "aarch64" in machine or "armv8" in machine:
        return "proxy-arm64"
    if "arm" in machine:
        return "proxy-arm"

    if "x86_64" in machine or "amd64" in machine or "i686" in machine:
        return "proxy-x64"
    if "x86" in machine or "i386" in machine:
        return "proxy-x86"


PROXY_FOLDER = path.join(path.dirname(path.realpath(__file__)), "bin")
PROXY_NAME = get_proxy_name()
PROXY_BIN = path.join(PROXY_FOLDER, PROXY_NAME)


class IngeniumAPI:
    # Onload is a class static
    _onload = None

    @property
    def onload(self) -> Optional[Callable[["IngeniumAPI"], None]]:
        return IngeniumAPI._onload

    @onload.setter
    def onload(self, val: Callable[["IngeniumAPI"], None]):
        IngeniumAPI._onload = val

    _user: Optional[str]
    _pass: Optional[str]
    _host: Optional[str]

    _is_knx: bool = False
    _objects: List[IngObject] = []
    _connection: CustomConnection
    _proxy: subprocess.Popen

    _state = None

    def __init__(self, state=None):
        self._state = state
        pass

    @property
    def state(self):
        return self._state

    def remote(self, username: str, password: str):
        self._user = username
        self._pass = password
        self._host = None
        return self

    def local(self, host: str):
        self._host = host
        self._user = None
        self._pass = None
        return self

    async def load(self, just_login=False, hass_integration=False, debug=False):
        my_env = environ.copy()
        my_env["ENABLE_TRAFFICSERVER"] = str(self._user == "CalidadAire").lower()
        if debug:
            my_env["LOG_LEVEL"] = "debug"
        self._proxy = subprocess.Popen([PROXY_BIN], env=my_env, universal_newlines=True)
        await asyncio.sleep(1)

        try:
            login_result = await start_connection(self, self._host, self._user, self._pass, just_login, hass_integration)
        except BaseException as e:
            print("Exception during login: " + repr(e) + " " + str(e))
            return False

        if login_result is None:
            return False

        # Add all the objects
        self._objects = []
        for o in login_result.get("devices"):
            # Filter out any external devices
            if o.get("externalId") is not None:
                continue

            ctype = get_device_type(o.get("ctype"))
            address = safecast(o.get("address"), int)

            # Skip over invalid types
            if ctype == IngComponentType.NOT_IMPLEMENTED or address is None:
                continue

            components = [IngComponent(c) for c in o.get("components")]

            if ctype.is_actuator():
                self._objects.append(IngActuator(self, self._is_knx, address, ctype, components))
            elif ctype.is_meterbus():
                self._objects.append(IngMeterBus(self, self._is_knx, address, ctype, components))
            elif ctype.is_tsif():
                self._objects.append(IngSif(self, self._is_knx, address, ctype, components))
            elif ctype.is_air_sensor():
                self._objects.append(IngAirSensor(self, self._is_knx, address, ctype, components))
            elif ctype.is_busing_regulator():
                self._objects.append(IngBusingRegulator(self, self._is_knx, address, ctype, components))
            elif ctype.is_thermostat():
                self._objects.append(IngThermostat(self, self._is_knx, address, ctype, components))

        if self.onload is not None:
            self.onload()
        return True

    @property
    def is_remote(self) -> bool:
        return self._host is None

    @property
    def is_knx(self) -> bool:
        return self._is_knx

    @property
    def objects(self) -> List[IngObject]:
        return self._objects

    @property
    def connection(self) -> CustomConnection:
        return self._connection

    async def send(self, p: Package):
        return await self.connection.send(p)

    async def close(self):
        await self.connection.close()
        if self._proxy is not None:
            self._proxy.terminate()

    def get_switches(self):
        entities = []
        for obj in self.objects:
            if not isinstance(obj, IngActuator):
                continue

            if obj.mode == ACTUATOR_NORMAL:
                for comp in obj.components:
                    entities.append((obj, comp))

        return entities

    def get_covers(self):
        entities = []
        for obj in self.objects:
            if not isinstance(obj, IngActuator):
                continue

            if obj.mode == ACTUATOR_BLIND:
                for comp in obj.components:
                    entities.append((obj, comp))

        return entities

    def get_meterbuses(self):
        entities = []
        for obj in self.objects:
            if isinstance(obj, IngMeterBus):
                for comp in obj.components:
                    for i in range(1, 5):
                        entities.append((obj, comp, i))
        return entities

    def get_sifs(self):
        entities = []
        for obj in self.objects:
            if isinstance(obj, IngSif):
                for comp in obj.components:
                    for i in [0, 2, 3, 4]:
                        entities.append((obj, comp, i))
        return entities

    def get_air_sensors(self):
        entities = []
        for obj in self.objects:
            if isinstance(obj, IngAirSensor):
                for comp in obj.components:
                    entities.append((obj, comp, 0))
                    entities.append((obj, comp, 1))
        return entities

    def get_lights(self):
        entities = []
        for obj in self.objects:
            if isinstance(obj, IngBusingRegulator):
                for comp in obj.components:
                    entities.append((obj, comp))
        return entities

    def get_climates(self):
        entities = []
        for obj in self.objects:
            if isinstance(obj, IngThermostat):
                for comp in obj.components:
                    entities.append((obj, comp))
        return entities
