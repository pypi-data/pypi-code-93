from typing import Dict, Union

from datalogue.errors import DtlError
from datalogue.version import __version__ as dtl_version


class Version:
    """
    Version object containing version number of SDK, platform, and the platform's services'
    """

    def __init__(self, sdk: str, platform: str, services: Dict[str, str]):
        """
            :param sdk: sdk version
            :param platform: Datalogue's platform version
            :param services: Datalogue's list of services
        """
        self.sdk = sdk
        self.platform = platform
        self.services = services

    def __eq__(self, other):
        return (self.sdk == other.sdk) and (self.platform == other.platform) and (self.services == other.services)

    def __repr__(self):
        service_string = ""
        for service, version in self.services.items():
            service_string += "    " + service + ": " + version + "\n"
        return (
            "DTLVersion("
            f"\n  sdk: {self.sdk}, "
            f"\n  platform: {self.platform}, "
            f"\n  services:\n{service_string})"
        )

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, "Version"]:
        """
        Convert to Datalogue's version object from JSON payload received from Datalogue's backend
        :param payload: The JSON payload
        :return: Datalogue's version object
        """
        platform_ver = payload.get("platform")
        if platform_ver is None or not isinstance(platform_ver, str):
            return DtlError("'platform_ver' is missing or not a string")
        services_ver = payload.get("services")
        if services_ver is None or not isinstance(services_ver, dict):
            return DtlError("'services_ver' is missing or not a dictionary")
        return Version(dtl_version, platform_ver, services_ver)
