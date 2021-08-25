"""State represents state of device, eg. as 'power_on'."""

import logging
from .helpers import generate_attribute_string

_LOGGER = logging.getLogger(__name__)


class State:
    """Represent current state."""

    def __init__(self, request):
        """Initialize new State object."""
        self._raw = None
        self._request = request

    def __str__(self):
        """Return readable string describint this object."""
        attributes = ["power_on", "switch_lock", "brightness"]
        return generate_attribute_string(self, attributes)

    def __eq__(self, other: object) -> bool:
        """Return true when other object is equal to this object."""
        if other is None:
            return False
        return self._raw == other._raw

    async def set(self, power_on=None, switch_lock=None, brightness=None):
        """Set state of device."""
        state = {}
        if isinstance(power_on, bool):
            state["power_on"] = power_on
        if isinstance(switch_lock, bool):
            state["switch_lock"] = switch_lock
        if isinstance(brightness, int):
            state["brightness"] = brightness

        if state == {}:
            _LOGGER.error("At least one state update is required")
            return False, ""

        status, response = await self._request("put", "api/v1/state", state)
        if status == 200 and response:
            # Zip result and original
            self._raw = {**self._raw, **response}
            return True, response

        error_message = ""
        try:
            error_message = response["error"]["description"]
        except (NameError, AttributeError, ValueError):
            error_message = response

        _LOGGER.error("Failed to set state: %s", error_message)
        return False, response

    @property
    def power_on(self) -> bool:
        """Return true when device is switched on."""
        return self._raw["power_on"]

    @property
    def switch_lock(self) -> bool:
        """
        Return True when switch_lock feature is on.

        Switch lock forces the relay to be turned on. While switch lock is enabled,
        you can't turn off the relay (not with the button, app or API)
        """
        return self._raw["switch_lock"]

    @property
    def brightness(self) -> int:
        """
        Return brightness of status-LED.

        Value between 0 and 255, where 255 is max
        """
        return self._raw["brightness"]

    async def update(self) -> bool:
        """Fetch new data for object."""
        status, response = await self._request("get", "api/v1/state")
        if status == 200 and response:
            self._raw = response
            return True

        return False
