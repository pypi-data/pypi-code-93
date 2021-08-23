"""Extended DagFactory"""
from typing import Any, Dict

import yaml
from dagfactory import DagFactory


class ExtendedDagFactory(DagFactory):
    """
        extends the dagfactory with a custom yaml loader constructor
        Takes a YAML config and generates DAGs.
        :param config_filepath: the filepath of the DAG factory YAML config file.
            Must be absolute path to file.
    """

    # pylint: disable=super-init-not-called
    def __init__(self, config_filepath: str, loader: yaml.SafeLoader = None) -> None:
        """init"""
        if loader is not None:
            self.loader = loader
        else:
            self.loader = yaml.FullLoader

        self._validate_config_filepath(
            config_filepath=config_filepath
        )
        self.config_filepath: str = config_filepath

        self.config: Dict[str, Any] = self._load_config(
            config_filepath=config_filepath
        )

    def _load_config(self, config_filepath: str) -> Dict[str, Any]:
        """
        Loads YAML config file to dictionary
        :returns: dict from YAML config file
        """
        try:
            with open(config_filepath, "r") as file_:
                config: Dict[str, Any] = yaml.load(
                    file_, Loader=self.loader
                )
        except Exception as err:
            raise Exception("Invalid DAG Factory config file") from err

        return config
