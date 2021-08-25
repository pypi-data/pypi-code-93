import os
from typing import Optional
from applipy.config.protocol import ConfigProtocol


class Environment(ConfigProtocol):

    def provide_for(self, protocol: str, key: str) -> Optional[str]:
        if protocol != 'env':
            return None

        return os.environ.get(key, None)
