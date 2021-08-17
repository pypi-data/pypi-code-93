from typing import Any, Dict, List, Union
from cryptoshred.backends import KeyBackend

from cryptoshred.entities import CryptoContainer

import logging

log = logging.getLogger()


def find_and_decrypt_in_dict(
    input: Union[List[Any], Dict[str, Any]], key_backend: KeyBackend
) -> Any:
    # TODO Make this return valid json
    def find_and_decrypt(x: Any) -> Any:
        log.info("Entering find and decrypt")
        log.debug(f"Working on:{x}")

        if type(x) is dict:
            log.debug("Identified Dict")

            if "enc" not in x.keys():
                # Increases performance by about 1/3
                for key, value in x.items():
                    x[key] = find_and_decrypt(value)
                return x

            try:
                log.debug("Looking for crypto container")
                cc: CryptoContainer[str] = CryptoContainer(
                    **x, key_backend=key_backend  # type:ignore
                )
                log.debug("Found")
                x = cc.plain()
                log.debug(f"Plain value: {x}")
                return x
            except Exception as e:  # noqa: E722
                log.debug(f"Not a crypto container. Identification failed with: {e}")
                for key, value in x.items():
                    x[key] = find_and_decrypt(value)
                return x

        elif type(x) is list:
            log.debug("Identified List")
            for idx, a in enumerate(x):
                x[idx] = find_and_decrypt(a)
            return x
        else:
            log.debug("Identified Leaf Node")
            return x

    find_and_decrypt(input)
    return input
