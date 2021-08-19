import re
import jwt
from abc import abstractmethod
from typing import Dict, Optional
from functools import cached_property

from energytt_platform.serialize import json_serializer
from energytt_platform.auth import (
    OpaqueToken,
    encode_opaque_token,
    decode_opaque_token,
)


class Context(object):
    """
    Context for a single incoming HTTP request.
    """

    TOKEN_HEADER = 'Authorization'
    TOKEN_PATTERN = re.compile(r'^Bearer:\s*(.+)$')

    @property
    @abstractmethod
    def headers(self) -> Dict[str, str]:
        """
        Returns request headers.
        """
        raise NotImplementedError

    @cached_property
    def raw_token(self) -> Optional[str]:
        """
        Returns request Bearer token.
        """
        if self.TOKEN_HEADER in self.headers:
            matches = self.TOKEN_PATTERN.findall(self.headers[self.TOKEN_HEADER])
            if matches:
                return matches[0]

    @cached_property
    def token(self) -> Optional[OpaqueToken]:
        """
        Parses token into an OpaqueToken.
        """
        if self.raw_token is not None:
            return decode_opaque_token(self.raw_token)
