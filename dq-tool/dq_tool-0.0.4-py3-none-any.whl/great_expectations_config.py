"""A data context config for Great Expectations."""
import copy
from typing import Union

from great_expectations.data_context.types.base import DataContextConfig
from great_expectations.data_context import BaseDataContext


class GreatExpectationsConfig:
    """Default GE configuration and methods around this."""
    _DATA_CONTEXT_CONFIG = {
        'config_version': 2,
        'plugins_directory': None,
        'config_variables_file_path': None,
        'datasources': {
            'spark_datasource': {
                'data_asset_type': {
                    'class_name': 'SparkDFDataset',
                    'module_name': 'great_expectations.dataset',
                },
                'class_name': 'SparkDFDatasource',
                'module_name': 'great_expectations.datasource',
                'batch_kwargs_generators': {},
            }
        },
        'stores': {
            'expectations_in_memory_store': {
                'class_name': 'ExpectationsStore',
                'store_backend': {
                    'class_name': 'InMemoryStoreBackend'
                },
            },
            'validations_in_memory_store': {
                'class_name': 'ValidationsStore',
                'store_backend': {
                    'class_name': 'InMemoryStoreBackend',
                },
            },
            'evaluation_parameter_store': {
                'class_name': 'EvaluationParameterStore'
            },
        },
        'expectations_store_name': 'expectations_in_memory_store',
        'validations_store_name': 'validations_in_memory_store',
        'evaluation_parameter_store_name': 'evaluation_parameter_store',
        'data_docs_sites': {},
        'validation_operators': {
            'validate_and_store_results': {
                'class_name': 'ActionListValidationOperator',
                'action_list': [
                    {
                        'name': 'store_validation_result',
                        'action': {'class_name': 'StoreValidationResultAction'},
                    },
                    {
                        'name': 'store_evaluation_params',
                        'action': {'class_name': 'StoreEvaluationParametersAction'},
                    }
                ],
            }
        },
        'anonymous_usage_statistics': {
            'enabled': False,
            'data_context_id': '16662cac-3a28-438c-b448-3ba301778d71'
        }
    }

    @classmethod
    def _get_db_store(
        cls,
        class_name: str,
        db_connection_dict: dict,
        db_connection_string: str
    ) -> dict:
        """Get database store dict to be used in context"""
        store = {
            'class_name': class_name,
            'store_backend': {
                'class_name': 'DatabaseStoreBackend'
            }
        }
        # connection dict goes to "credentials"
        if db_connection_dict:
            store['store_backend']['credentials'] = db_connection_dict
            return store
        # connection string goes to connection_string
        if not db_connection_string:
            raise ValueError("Both db_connection_string and db_connection_dict are empty, can't create a db store")
        store['store_backend']['connection_string'] = db_connection_string
        return store

    @classmethod
    def _get_config(cls, db_store_connection: Union[dict, str] = None) -> dict:
        """Get a config dict to create a data context from"""
        config = copy.deepcopy(cls._DATA_CONTEXT_CONFIG)
        # no stores, just default config
        if not db_store_connection:
            return config

        if isinstance(db_store_connection, str):
            # if it's a connection string, turn it into a dict - some escaping magic needed for dbx env variables
            db_connection_string = cls._unescape_str(db_store_connection)
            db_connection_dict = None
        else:
            db_connection_string = None
            db_connection_dict = {
                k: cls._unescape_str(v)
                for k, v in db_store_connection.items()
            }
        # add db_connection to the config as ExpectationsStore and ValidationsStore
        config['stores']['expectations_db_store'] = cls._get_db_store(
            class_name='ExpectationsStore',
            db_connection_dict=db_connection_dict,
            db_connection_string=db_connection_string
        )
        config['expectations_store_name'] = 'expectations_db_store'

        config['stores']['validations_db_store'] = cls._get_db_store(
            class_name='ValidationsStore',
            db_connection_dict=db_connection_dict,
            db_connection_string=db_connection_string
        )
        config['validations_store_name'] = 'validations_db_store'
        return config

    @classmethod
    def _unescape_str(cls, s: str):
        """Unescape string from the fun "escaping" that databricks does"""
        return s.strip("'").replace('\\$', '$')

    @classmethod
    def get_context(cls, db_store_connection: Union[dict, str] = None) -> BaseDataContext:
        """Get a Great Expectations context for dq tool"""
        config = cls._get_config(db_store_connection=db_store_connection)
        project_config = DataContextConfig(**config)
        return BaseDataContext(project_config=project_config)
