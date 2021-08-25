"""
Base class for ABI hierarchy.
"""
from typing import (
    List, Dict, Any, Optional
)
from abc import ABC, abstractmethod

from sha3 import keccak_256

# ============================================================================
# ======================== Types aliases =====================================
# ============================================================================

ABI_T = List[Dict[str, Any]]
METHOD_ABI_MAPPING_T = Dict[str, Dict[str, Any]]


# ============================================================================
# ========================= Utilities ========================================
# ============================================================================

def _get_encoded_signature(func_name: str, input_types: List[str]) -> str:
    """
    Encode signature of function according to the ABI specification.

    :param func_name: str, function name
    :param input_types: List[str], list with inputs types for function.
    :return: str, first fours bytes of encoded function.

    The result of encoding is:

    keccak256('func_name(input_type1,input_type2,...)')
    """
    input_types = ','.join(input_types)
    signature = f'{func_name}({input_types})'
    keccak = keccak_256()
    keccak.update(signature.encode('ascii'))
    return f'0x{keccak.hexdigest()[:8]}'


def _gather_types(inputs: List[Dict[str, Any]]) -> List[str]:
    """
    Parse input json ABI description for function input types.

    :param inputs: List[Dict[str, Any]], 'inputs' entry of a json description.
    :return: List[str], gathered types.
    """

    def __extract_type(entity: Dict[str, Any]) -> str:
        if 'components' in entity:
            t = ','.join(_gather_types(
                entity['components']
            ))
            return f'({t})'

        return entity['type']

    return [
        __extract_type(inp)
        for inp in inputs
    ]


def with_decoded_signatures(
        contract_abi: ABI_T
) -> METHOD_ABI_MAPPING_T:
    """Create mapping from function signatures to function descriptions."""

    def __is_function(entity: Dict[str, Any]) -> bool:
        t = entity['type']
        if t == 'function' or t == 'receive':
            return True

        return False

    return {
        _get_encoded_signature(
            entry['name'],
            _gather_types(entry['inputs'])
        ): entry
        for entry
        in filter(
            __is_function, contract_abi
        )
    }


# ============================================================================
# ============================== ABI =========================================
# ============================================================================


class ABI(ABC):
    """
    Instance for getting methods descriptions from ABI.
    """

    @abstractmethod
    def _load_abi(self) -> ABI_T:
        """Describe a way of getting ABI."""
        pass

    @staticmethod
    def _extract_mapping(abi: ABI_T, *args, **kwargs) -> METHOD_ABI_MAPPING_T:
        """Convert ABI description to mapping { function -> function desc. }"""
        return with_decoded_signatures(abi)

    def __init__(self):
        """Create instance of ABI."""
        self._abi = self._load_abi()
        self._method_abi_mapping = self._extract_mapping(
            self._abi
        )

    def get_func_abi(
            self, function_sign: str, default: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Return function description for function signature."""
        return self._method_abi_mapping.get(function_sign, default)
