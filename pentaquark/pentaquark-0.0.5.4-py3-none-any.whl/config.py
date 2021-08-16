import json
import os
import warnings

from dotenv import load_dotenv


class Config:
    DEFAULTS = dict(
        DEBUG=True,
        NEO4J_URI="bolt://localhost:7687",
        NEO4J_USER="neo4j",
        NEO4J_PASSWORD="neo4j",
        NEO4J_DEFAULT_DATABASE="neo4j",
        NEO4J_ENCRYPTED_CONNECTION=False,
    )

    def __init__(self, **kwargs):
        for k, v in self.DEFAULTS.items():
            if k in kwargs:
                v = kwargs[k]
            setattr(self, k, v)

    def feed_from_json_file(self, json_file_path):
        with open(json_file_path, "r") as f:
            data = json.load(f)
        for k, v in data.items():
            if k in self.DEFAULTS:
                setattr(self, k, v)
            else:
                warnings.warn(f"Key '{k}' is not a valid configuration key, will be ignored", UserWarning)

    def feed_from_env_file(self, env_file=".env", override=True):
        load_dotenv(dotenv_path=env_file, override=override)
        self.feed_from_env()

    def feed_from_env(self, set_null=False):
        for k in self.DEFAULTS:
            v = os.getenv(k, None)
            if v or set_null:
                setattr(self, k, v)

    def __str__(self):
        return "\n".join(f"{k}={getattr(self, k, None)}" for k in self.DEFAULTS)


gconf = Config()
