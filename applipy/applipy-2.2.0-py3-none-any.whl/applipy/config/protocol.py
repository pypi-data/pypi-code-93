from typing import Optional, Any


class ConfigProtocol:

    def provide_for(self, protocol: str, key: str) -> Optional[Any]:
        raise NotImplementedError
