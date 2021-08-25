"""Device represents basic information about the product."""

from .helpers import generate_attribute_string


class Device:
    """Represent Device config."""

    def __init__(self, request):
        """Initialize new Device object."""
        self._request = request
        self._raw = None

    def __str__(self):
        """Return readable string describint this object."""
        attributes = [
            "product_name",
            "product_type",
            "serial",
            "api_version",
            "firmware_version",
        ]
        return generate_attribute_string(self, attributes)

    def __eq__(self, other: object) -> bool:
        """Return true when other object is equal to this object."""
        if other is None:
            return False
        return self._raw == other._raw

    @property
    def product_name(self):
        """Friendly name of the device."""
        return self._raw["product_name"]

    @property
    def product_type(self):
        """Device Type identifier."""
        return self._raw["product_type"]

    @property
    def serial(self):
        """
        Return readable serial id.

        Formatted as hex string of the 12 characters without delimiters
        eg: "aabbccddeeff"
        """
        return self._raw["serial"]

    @property
    def api_version(self):
        """Return API version of the device."""
        return self._raw["api_version"]

    @property
    def firmware_version(self):
        """
        User readable version of the device firmware.

        Formatted as %d%02d e.g. 2.03
        """
        return self._raw["firmware_version"]

    async def update(self):
        """Fetch new data for device."""
        status, response = await self._request("get", "api")
        if status == 200 and response:
            self._raw = response
            return True
        return False
