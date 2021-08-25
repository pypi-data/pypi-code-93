from typing import Optional
from applipy.config.protocol import ConfigProtocol


class DockerSecrets(ConfigProtocol):

    def provide_for(self, protocol: str, key: str) -> Optional[str]:
        if protocol != 'secret':
            return None

        with open('/run/secrets/' + key, 'r') as f:
            return f.read()
