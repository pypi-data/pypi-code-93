import json
from typing import Dict, Optional


class NamespaceCache:
    def __init__(self):
        self.cache = None

    def __call__(self) -> str:
        if not self.cache:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as f:
                self.cache = f.read().strip()
        return self.cache


get = NamespaceCache()
