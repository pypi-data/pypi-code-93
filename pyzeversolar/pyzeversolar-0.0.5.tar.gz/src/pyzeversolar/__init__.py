"""PyZeverSolar interacts as a library to communicate with Zever Solar inverters"""
from re import split
import aiohttp
import asyncio
import concurrent
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)

MAPPER_STATES = {  # These states are copied directly from ZeverSolar maintaining the broken english.
    "0": "OK",
    "1": "Ready to connect ZeverCloud",
    "2": "Not connected to the router",
    "3": "Not inserted ethernet cable",
    "4": "Zevercloud no response",
    "5": "Failed with Zevercloud authentication",
    "6": "Can't connect to Internet",
    "7": "DNS server exception:DNS error or no internet access",
    "8": "device information error",
    "9": "Not bind a plant",
}

URL_PATH_WIFI_INFO = "home.cgi"

class Sensor(object):
    """Sensor definition"""

    def __init__(self, key, dataIndex, name, unit="", per_day_basis=False):
        self.key = key
        self.dataIndex = dataIndex
        self.name = name
        self.unit = unit
        self.value = None
        self.per_day_basis = per_day_basis
        self.date = datetime.now()
        self.enabled = False


class Sensors(object):
    """ZeverSolar sensors"""

    def __init__(self):
        self.__s = []
        self.add(
            (
                Sensor("pac", 10, "Current Power", "W"),
                Sensor("e-today", 11, "Today Yeild", "kWh", True),
                Sensor("Status", 7, "Status"),
            )
        )

    def __len__(self):
        """Length."""
        return len(self.__s)

    def __contains__(self, key):
        """Get a sensor using either the name or key."""
        try:
            if self[key]:
                return True
        except KeyError:
            return False

    def __getitem__(self, key):
        """Get a sensor using either the name or key."""
        for sen in self.__s:
            if sen.name == key or sen.key == key:
                return sen
        raise KeyError(key)

    def __iter__(self):
        """Iterator."""
        return self.__s.__iter__()

    def add(self, sensor):
        """Add a sensor, warning if it exists."""
        if isinstance(sensor, (list, tuple)):
            for sss in sensor:
                self.add(sss)
            return

        if not isinstance(sensor, Sensor):
            raise TypeError("PyZeverSolar.Sensor expected")

        if sensor.name in self:
            old = self[sensor.name]
            self.__s.remove(old)
            _LOGGER.warning("Replacing sensor %s with %s", old, sensor)

        if sensor.key in self:
            _LOGGER.warning("Duplicate ZeverSolar sensor key %s", sensor.key)

        self.__s.append(sensor)


class ZSI:
    """Provides access to ZeverSolar inverter data"""

    def __init__(self, host):
        self.host = host
        self.serialNumber = "XXXXXXXXXXXXXXXXX"
        self.registeryId = "XXXXXXXXXXXXX"
        self.registeryKey = "XXXXXXXXXXXXX"
        self.hardwareVersion = "MXX"
        self.url = "http://{0}/".format(self.host)
        self.url_info = self.url + URL_PATH_WIFI_INFO

    async def read(self, sensors):
        """Returns necessary sensors from ZeverSolar inverter"""

        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(
                timeout=timeout, raise_for_status=True
            ) as session:
                current_url = self.url_info
                async with session.get(current_url) as response:
                    data = await response.text()
                    reader = split("\n", data)
                    try:
                        self.serialNumber = reader[9]
                    except:
                        self.serialNumber = self.serialNumber
                    try:
                        self.registeryId = reader[2]
                    except:
                        self.registeryId = self.registeryId
                    try:
                        self.registeryKey = reader[3]
                    except:
                        self.registeryKey = self.registeryKey
                    try:
                        self.hardwareVersion = reader[4]
                    except:
                        self.hardwareVersion = self.hardwareVersion
                    _LOGGER.debug("Inverter SN: %s", self.serialNumber)
                    at_least_one_enabled = False

                    for sen in sensors:
                        try:
                            v = reader[sen.dataIndex]
                        except IndexError:
                            v = None

                        if v is not None:
                            if sen.name == "Status":
                                sen.value = MAPPER_STATES.get(v, "Unknown")
                            else:
                                sen.value = v
                            sen.date = datetime.now()
                            sen.enabled = True
                            at_least_one_enabled = True

                    if not at_least_one_enabled:
                        raise UnexpectedResponseException("not at_least_one_enabled")

                    if sen.enabled:
                        _LOGGER.debug(
                            "Got new value for sensor %s: %s", sen.name, sen.value
                        )

                    return True
        except (
            aiohttp.client_exceptions.ClientConnectorError,
            concurrent.futures._base.TimeoutError,
        ):
            _LOGGER.warning(
                "Connection to ZeverSolar inverter is not possible. "
                + "The inverter may be offline due to insufficient sunlight. "
                + "Otherwise check host/ip address."
            )
            return False
        except aiohttp.client_exceptions.ClientResponseError as err:
            raise UnexpectedResponseException(err)


class UnexpectedResponseException(Exception):
    """Exception for unexpected status code"""

    def __init__(self, message):
        Exception.__init__(self, message)