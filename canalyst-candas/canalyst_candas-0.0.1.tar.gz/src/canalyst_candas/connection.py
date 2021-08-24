"""
Connection module
"""
from typing import Any
from canalyst_candas.candas import Model, ModelMap, ModelSet
from canalyst_candas.configuration.config import Config, resolve_config


class Connection:
    """
    Connection uses configuration and shares them across the library
    """

    def __init__(self, config: Config = None) -> None:
        self.config = resolve_config(config)

    def get_model(self, *args: Any, **kwargs: Any) -> Model:
        """
        Return a Model with configuration
        """
        return Model(config=self.config, *args, **kwargs)

    def get_model_map(self, *args: Any, **kwargs: Any) -> ModelMap:
        """
        Return a ModelMap with configuration
        """
        return ModelMap(config=self.config, *args, **kwargs)

    def get_model_set(self, *args, **kwargs) -> ModelSet:
        """
        Return a ModelSet with configuration
        """
        return ModelSet(config=self.config, *args, **kwargs)
