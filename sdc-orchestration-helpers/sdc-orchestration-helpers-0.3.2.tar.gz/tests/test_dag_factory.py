"""TestExtendedDagFactory"""
from pathlib import Path

import pytest
import yaml

from sdc_orchestration_helpers.airflow.dag_factory import ExtendedDagFactory
from sdc_orchestration_helpers.yaml_helpers.loaders import get_yaml_config


class TestExtendedDagFactory:
    """Test Extended DagFactory class"""

    @staticmethod
    def test_simple_config_load():
        """Test the extended dagfactory loads config as expected"""
        # pylint: disable=protected-access

        simple_config = Path('tests/fixtures/simple_dummy_dag.yml').absolute()

        try:
            dag_factory = ExtendedDagFactory(config_filepath=simple_config, loader=yaml.SafeLoader)
            _ = dag_factory._load_config(config_filepath=simple_config)
        except Exception as exception:
            raise pytest.fail("DID RAISE {0}".format(exception))

    @staticmethod
    def test_simple_config_correct_output():
        """Test the extended dagfactory loads config with expected output"""
        # pylint: disable=protected-access
        simple_config = Path('tests/fixtures/simple_dummy_dag.yml').absolute()
        validation_yaml = get_yaml_config(filepath=simple_config)
        dag_factory = ExtendedDagFactory(config_filepath=simple_config, loader=yaml.SafeLoader)
        actual = dag_factory._load_config(config_filepath=simple_config)

        return actual == validation_yaml, (
            "failed. Loaded config did not match the validation config."
        )
