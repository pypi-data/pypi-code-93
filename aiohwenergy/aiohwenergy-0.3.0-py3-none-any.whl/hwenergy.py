"""Representation of a HomeWizard Energy device."""

import logging
import aiohttp

from .device import Device
from .data import Data
from .state import State
from .errors import raise_error

_LOGGER = logging.getLogger(__name__)

SUPPORTED_API_VERSION = "v1"

SUPPORTED_DEVICES = ["HWE-P1", "SDM230-wifi", "SDM630-wifi", "HWE-SKT"]


class HomeWizardEnergy:
    """Communicate with a HomeWizard Energy device."""

    def __init__(self, host):
        """Create a HomeWizard Energy object."""
        _LOGGER.debug("__init__ HomeWizardEnergy")
        self._host = host
        self._clientsession = self._get_clientsession()

        # Endpoints
        self.device = None
        self.data = None
        self.state = None

    async def __aexit__(self, exc_type, exc, tb):
        """Close connection when object got deleted."""
        await self.close()

    def _get_clientsession(self):
        """Get a clientsession that is tuned for communication with the Energy device."""
        connector = aiohttp.TCPConnector(
            enable_cleanup_closed=True,
            limit_per_host=1,
        )

        return aiohttp.ClientSession(connector=connector)

    async def initialize(self):
        """Initialize new Device object and validate connection."""
        self.device = Device(self.request)
        status = await self.device.update()
        if status:

            # Validate 'device'
            if self.device.api_version != SUPPORTED_API_VERSION:
                raise_error(
                    3,
                    f"Unsupported API version, expected version '{SUPPORTED_API_VERSION}'",
                )

            if self.device.product_type not in SUPPORTED_DEVICES:
                raise_error(3, f"Unsupported device '{self.device.product_type}'")

            # Get /data
            self.data = Data(self.request)
            status = await self.data.update()
            if not status:
                _LOGGER.error("Failed to get 'data'")

            # For HWE-SKT: Get /State
            if self.device.product_type == "HWE-SKT":
                self.state = State(self.request)
                status = await self.state.update()
                if not status:
                    _LOGGER.error("Failed to get 'state' data")

    async def update(self) -> bool:
        """Fetch complete state for available endpoints."""
        _LOGGER.debug("hwenergy update")

        if self.device is not None:
            status = await self.device.update()
            if not status:
                return False

        if self.data is not None:
            status = await self.data.update()
            if not status:
                return False

        if self.state is not None:
            status = await self.state.update()
            if not status:
                return False

        return True

    async def close(self):
        """Close client session."""
        await self._clientsession.close()

    async def request(self, method, path, data=None):
        """Make a request to the API."""
        if self._clientsession.closed:
            # Avoid runtime errors when connection is closed.
            # This solves an issue when Updates were scheduled and HA was shutdown
            return -1, None

        url = f"http://{self._host}/{path}"
        _LOGGER.debug("URL: %s", url)

        headers = {"Content-Type": "application/json"}
        _LOGGER.debug("%s, %s, %s", method, url, data)
        async with self._clientsession.request(
            method, url, json=data, headers=headers
        ) as resp:
            _LOGGER.debug("%s, %s", resp.status, await resp.text("utf-8"))

            if resp.status == 401:
                raise_error(
                    101, "API disabled. API must be enabled in HomeWizard Energy app"
                )

            data = None
            if resp.content_type == "application/json":
                data = await resp.json()
            else:
                raise_error(1, "Unexpected content type")

            return resp.status, data
