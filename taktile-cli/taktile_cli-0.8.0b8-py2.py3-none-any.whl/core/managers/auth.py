from typing import Dict

from tktl.core.managers.base import BaseConfigManager
from tktl.core.strings import HeaderStrings


class AuthConfigManager(BaseConfigManager):

    LOGIN_HEADERS = {
        "Accept": HeaderStrings.APPLICATION_JSON,
        "Content-Type": HeaderStrings.APPLICATION_URLENCODED,
    }

    @classmethod
    def get_api_key(cls):
        cfg = cls.get_tktl_config()
        if cfg and "api-key" in cfg:
            return cfg["api-key"]
        else:
            return None

    @classmethod
    def set_api_key(cls, api_key: str) -> Dict:
        cfg = cls.get_tktl_config()
        if cfg:
            if cfg["api-key"] == api_key:
                return {"api-key": api_key}
            cfg["api-key"] = api_key
            return cls.set_tktl_config(cfg)
        else:
            cfg = {"api-key": api_key}
            return cls.set_tktl_config(cfg)
