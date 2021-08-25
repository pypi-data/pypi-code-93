"""Dataclasses for store parsed EVM script parts."""
import json

from dataclasses import dataclass, field, asdict
from typing import (
    List, Dict, Any, Optional
)

# ===========================================================================
# =========================== Data specific constants =======================
# ===========================================================================

# All lengths in numbers of symbols (number of bytes * 2)
SPEC_ID_LENGTH = 8
ADDRESS_LENGTH = 40
METHOD_ID_LENGTH = 8
CALL_DATA_LENGTH = 8

DEFAULT_SPEC_ID = '1'.zfill(SPEC_ID_LENGTH)
HEX_PREFIX = '0x'


# ============================================================================
# =========================== Format checking errors =========================
# ============================================================================

class FormatError(TypeError):
    """
    The base type of exception for format checks.
    """

    pass


class MismatchLength(FormatError):
    """
    Mismatching between expected and received data lengths
    """

    def __init__(self, field_name: str, received: int, expected: int):
        """Get error info and forward formatted message to super"""
        message = f'Length of {field_name} should be: {expected}; ' \
                  f'received: {received}.'
        super().__init__(message)


# ===========================================================================
# ================ Description of EVM scripts as structures =================
# ===========================================================================


def _add_hex_prefix(data: str) -> str:
    """Add HEX_PREFIX to the start of a string data."""
    return f'{HEX_PREFIX}{data}'


@dataclass
class OneCall:
    """
    Contains fields of the single call from script body.
    """

    # 20 bytes
    address: str
    # 4 bytes
    call_data_length: int
    # 4 bytes
    method_id: str
    # call_data_length - 4 bytes
    encoded_call_data: str
    # Contract ABI
    abi: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        """Check length constraints and perform normalized to hex."""
        if len(self.address) != ADDRESS_LENGTH:
            raise MismatchLength(
                'address', len(self.address), ADDRESS_LENGTH
            )

        if len(self.method_id) != METHOD_ID_LENGTH:
            raise MismatchLength(
                'method id', len(self.method_id), METHOD_ID_LENGTH
            )

        call_data_length_without_method_id = (
                self.call_data_length * 2 - len(self.method_id)  # noqa
        )
        if len(self.encoded_call_data) != call_data_length_without_method_id:
            raise MismatchLength(
                'encoded call data',
                len(self.encoded_call_data),
                call_data_length_without_method_id
            )

        self.address = _add_hex_prefix(self.address)
        self.method_id = _add_hex_prefix(self.method_id)
        self.encoded_call_data = _add_hex_prefix(self.encoded_call_data)


@dataclass
class EVMScript:
    """
    Contains data of the whole EVM script.
    """

    # Script executor id
    spec_id: str = field(default=DEFAULT_SPEC_ID)
    # Calls data
    calls: List[OneCall] = field(default_factory=list)

    def __post_init__(self):
        """Check length constraints and perform normalized to hex."""
        if len(self.spec_id) != SPEC_ID_LENGTH:
            raise MismatchLength(
                'spec id', len(self.spec_id), SPEC_ID_LENGTH
            )

        self.spec_id = _add_hex_prefix(self.spec_id)

    def to_json(self) -> str:
        """Encode structure into json format."""
        return json.dumps(asdict(self))
