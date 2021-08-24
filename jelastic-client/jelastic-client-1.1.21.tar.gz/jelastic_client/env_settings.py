from typing import NamedTuple


class EnvSettings(NamedTuple):
    displayName: str = None
    engine: str = None
    ishaenabled: bool = False
    region: str = None
    shortdomain: str = None
    sslstate: bool = False
