from dataclasses import dataclass


@dataclass
class Credentials:
    URL: str
    TOKEN: str
    BUCKET: str
    ORG: str
