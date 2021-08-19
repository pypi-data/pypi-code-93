from dataclasses import dataclass


@dataclass(frozen=True)
class Market:
    url: str
    todays_hours: str
    mic: str
    operating_mic: str
    acronym: str
    name: str
    city: str
    country: str
    timezone: str
    website: str
