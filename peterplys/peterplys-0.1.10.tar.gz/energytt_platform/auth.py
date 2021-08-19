from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from energytt_platform.serialize import Serializable


@dataclass
class GarbageToken(Serializable):
    issued: datetime
    expires: datetime
    subject: str
    scope: List[str]
    on_behalf_of: Optional[str]

    @property
    def actual_subject(self) -> str:
        if self.on_behalf_of:
            return self.on_behalf_of
        else:
            return self.subject


@dataclass
class OpaqueToken(Serializable):
    issued: datetime
    expires: datetime
    subject: str
    scope: List[str]
    on_behalf_of: Optional[str]

    @property
    def actual_subject(self) -> str:
        if self.on_behalf_of:
            return self.on_behalf_of
        else:
            return self.subject


def encode_opaque_token(token: OpaqueToken) -> str:
    pass


def decode_opaque_token(encoded_jwt: str) -> OpaqueToken:
    pass
