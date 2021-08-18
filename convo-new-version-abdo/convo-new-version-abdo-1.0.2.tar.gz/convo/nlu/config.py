import copy
import logging
import os
import ruamel.yaml as yaml
from typing import Any, Dict, List, Optional, Text, Union

from convo.shared.exceptions import ConvoExceptions 
import convo.shared.utils.io
import convo.utils.io
from convo.shared.constants import (
    PIPELINE_DOCUMENTS_URL ,
    MIGRATION_GUIDE_DOCUMENTS_URL,
    DEFAULT_CONFIGURATION_PATH,
)
from convo.shared.utils.io import json_to_str

log = logging.getLogger(__name__)


class InvalidConfigurationError(ValueError, ConvoExceptions ):
    """Raised if an invalid configuration is encountered."""


def load(
    configuration: Optional[Union[Text, Dict]] = None, **kwargs: Any
) -> "ConvoNLUModelConfiguration":
    if isinstance(configuration, Dict):
        return load_from_dictionary(configuration, **kwargs)

    file_configuration = {}
    if configuration is None and os.path.isfile(DEFAULT_CONFIGURATION_PATH):
        configuration = DEFAULT_CONFIGURATION_PATH

    if configuration is not None:
        file_configuration = convo.shared.utils.io.read_configuration_file(configuration)

    return load_from_dictionary(file_configuration, **kwargs)


def load_from_dictionary(config: Dict, **kwargs: Any) -> "ConvoNLUModelConfiguration":
    if kwargs:
        config.update(kwargs)
    return ConvoNLUModelConfiguration(config)


def overriding_dfault_values(
    defaults: Optional[Dict[Text, Any]], custom: Optional[Dict[Text, Any]]
) -> Dict[Text, Any]:
    if defaults:
        config = copy.deepcopy(defaults)
    else:
        config  = {}

    if custom:
        for key in custom.keys():
            if isinstance(config .get(key), dict):
                config [key].update(custom[key])
            else:
                config [key] = custom[key]

    return config


def comp_configuration_from_pipeline(
    index: int,
    pipeline: List[Dict[Text, Any]],
    defaults: Optional[Dict[Text, Any]] = None,
) -> Dict[Text, Any]:
    try:
        d = pipeline[index]
        return overriding_dfault_values(defaults, d)
    except IndexError:
        convo.shared.utils.io.raising_warning(
            f"Tried to get configuration value for component "
            f"number {index} which is not part of your pipeline. "
            f"Returning `defaults`.",
            docs=PIPELINE_DOCUMENTS_URL ,
        )
        return overriding_dfault_values(defaults, {})


class ConvoNLUModelConfiguration:
    def __init__(self, config_vals: Optional[Dict[Text, Any]] = None) -> None:
        """Create a model configuration, optionally overriding
        defaults with a dictionary ``configuration_values``.
        """
        if not config_vals:
            config_vals = {}

        self.language = "en"
        self.pipeline = []
        self.data = None

        self.overriding(config_vals)

        if self.__dict__["pipeline"] is None:
            # replaces None with empty list
            self.__dict__["pipeline"] = []
        elif isinstance(self.__dict__["pipeline"], str):
            # DEPRECATION EXCEPTION - remove in 2.1
            raise ConvoExceptions (
                f"You are using a pipeline template. All pipelines templates "
                f"have been removed in 2.0. Please add "
                f"the components you want to use directly to your configuration "
                f"file. {MIGRATION_GUIDE_DOCUMENTS_URL}"
            )

        for key, value in self.items():
            setattr(self, key, value)

    def __getitem__(self, key: Text) -> Any:
        return self.__dict__[key]

    def get(self, key: Text, default: Any = None) -> Any:
        return self.__dict__.get(key, default)

    def __setitem__(self, key: Text, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: Text) -> None:
        del self.__dict__[key]

    def __contains__(self, key: Text) -> bool:
        return key in self.__dict__

    def __len__(self) -> int:
        return len(self.__dict__)

    def __getstate__(self) -> Dict[Text, Any]:
        return self.as_dictionary()

    def __setstate__(self, state: Dict[Text, Any]) -> None:
        self.overriding(state)

    def items(self) -> List[Any]:
        return list(self.__dict__.items())

    def as_dictionary(self) -> Dict[Text, Any]:
        return dict(list(self.items()))

    def view_representation(self) -> Text:
        return json_to_str(self.__dict__, indent=4)

    def for_comp(self, index, defaults=None) -> Dict[Text, Any]:
        return comp_configuration_from_pipeline(index, self.pipeline, defaults)

    @property
    def comp_names(self) -> List[Text]:
        if self.pipeline:
            return [c.get("name") for c in self.pipeline]
        else:
            return []

    def set_comp_attribute(self, index, **kwargs) -> None:
        try:
            self.pipeline[index].update(kwargs)
        except IndexError:
            convo.shared.utils.io.raising_warning(
                f"Tried to set configuration value for component "
                f"number {index} which is not part of the pipeline.",
                docs=PIPELINE_DOCUMENTS_URL ,
            )

    def overriding(self, config) -> None:
        if config:
            self.__dict__.update(config)
