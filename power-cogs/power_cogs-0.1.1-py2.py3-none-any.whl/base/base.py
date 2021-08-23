from dataclasses import asdict
from typing import Any, Dict

import hydra

# instantiate
from power_cogs.callbacks.callback import set_method_callback
from power_cogs.config.config import load_config_from_file
from power_cogs.utils import fullname


class BaseConfigMixin:
    @classmethod
    def from_config_file(cls, config_path: str, overrides: Dict[str, Any] = {}):
        _config_class = cls._config_class
        loaded_config = load_config_from_file(
            config_path, _config_class, overrides=overrides
        )
        loaded_config = asdict(loaded_config)
        new_config = {"config": loaded_config}
        new_config["_target_"] = fullname(cls)
        return hydra.utils.instantiate(new_config, _recursive_=False)

    def instantiate(self, config: Dict[str, Any], recursive: bool = False) -> Any:
        return hydra.utils.instantiate(config, _recursive_=recursive)

    def set_callback(self, method, callbacks, rule: str = "wrap"):
        set_method_callback(self, method, callbacks, rule=rule)


class Base(BaseConfigMixin):
    pass
