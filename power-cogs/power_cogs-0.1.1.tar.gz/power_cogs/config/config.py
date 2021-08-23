from __future__ import annotations

import os
from typing import Any, Dict, Optional

import hydra
from omegaconf import OmegaConf
from pydantic.dataclasses import dataclass

# internal
from power_cogs.utils.dict_utils import merge


def load_config_from_file(
    config_path: str, config_class: type = None, overrides: Dict[str, Any] = {}
) -> Optional[Dict[str, Any], type]:
    defaults = {}
    if config_class is not None:
        defaults = OmegaConf.to_container(OmegaConf.create(config_class))
    loaded = OmegaConf.load(config_path)
    loaded = merge(defaults, loaded)
    loaded = merge(loaded, overrides)
    loaded = OmegaConf.create(loaded)
    OmegaConf.resolve(loaded)
    if config_class is not None:
        return config_class(**loaded)
    return loaded


def load_config(
    config_class: type = None,
    config: Dict[str, Any] = {},
    overrides: Dict[str, Any] = {},
) -> Optional[Dict[str, Any], type]:
    defaults = {}
    config = {}
    if config_class is not None:
        defaults = OmegaConf.to_container(OmegaConf.create(config_class))
    loaded = merge(defaults, config)
    loaded = merge(loaded, overrides)
    loaded = OmegaConf.create(loaded)
    OmegaConf.resolve(loaded)
    if config_class is not None:
        return config_class(**loaded)


def save_config(config, config_path: str, config_name: str):
    if os.path.isdir(config_path):
        config_path = os.path.join(config_path, "{}.yaml".format(config_name))
    with open(config_path, "w") as f:
        OmegaConf.save(config, f)
    return config_path


@dataclass
class Config:
    @classmethod
    def load_from_file(cls, config_path: str, overrides: Dict[str, Any] = {}) -> Config:
        return load_config_from_file(config_path, cls, overrides)

    def save_to_file(self, config_path: str) -> str:
        return save_config(self, config_path, self.__class__.__name__)

    @classmethod
    def from_dict(cls, d) -> Config:
        return OmegaConf.structured(OmegaConf.merge(OmegaConf.structured(cls), d))

    @classmethod
    def instantiate(cls, config_path: str, overrides: Dict[str, Any] = {}) -> Any:
        loaded = cls.load_from_file(config_path, overrides)
        return hydra.utils.instantiate(loaded)

    def overrides(self):
        pass

    def __post_init_post_parse__(self):
        self.overrides()


def class_config(config: Config):
    def _config(cls):
        cls._config_class = config
        return cls

    return _config
