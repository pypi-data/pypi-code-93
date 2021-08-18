"""The main interface to the tool: DQTool class"""
from datetime import datetime
from typing import Union, List, Type
import types

from great_expectations.core import (
    expectationSuiteSchema as GEexpectationSuiteSchema,
    ExpectationSuite as GEExpectationSuite
)
from great_expectations.dataset import SparkDFDataset

from .expectation_attributes.expectation_suite import ExpectationSuite
from .validation_result import ValidationResult
from .playground import run_expectation
from .custom_expectations import BaseSparkExpectations
from .great_expectations_config import GreatExpectationsConfig
from .expectation_store import ExpectationStore
from .hive_metastore import HiveMetastore
from .misc.databricks import DatabricksIdentityProvider
from .misc.printing import pretty_print


class DQTool:
    """A class with a simple interface for frequently used features.
    @param expectation_class: A class with custom expectations that will be used
    in playground and validations. A subclass of SparkDFDataset
    @param: A connection to a database where DQTool will store expectations and validation results."""
    def __init__(
        self,
        spark: 'SparkSession',
        expectation_class: Type[SparkDFDataset] = None,
        db_store_connection: dict = None,
        always_create_store: bool = False,  # create an ExpectationStore even for inmemory GE store?
        user_identity_provider: 'UserIdentityProvider' = None
    ):
        """Initialize great_expectations and other moving parts"""
        # "dependency injection"
        self._spark = spark
        self._saved_spark_struct_type = None
        self._saved_user_identity_provider = user_identity_provider
        self._expectation_class = expectation_class or BaseSparkExpectations

        # get the context for GE
        self._context = GreatExpectationsConfig.get_context(db_store_connection=db_store_connection)
        # create a store
        self._has_expectation_store = False
        if db_store_connection or always_create_store:
            self.expectation_store = ExpectationStore(dq_tool=self)
            self._has_expectation_store = True

    _GE_DIR_NAME = 'great_expectations_config'
    _GENERATE_COUNT = 1000
    _GE_DATASOURCE = 'spark_datasource'
    _GE_SUITE_GENERATED_NAME = 'dq_tool_generated_expectations'
    _GE_SUITE_AUTHORED_NAME = 'dq_tool_authored_expectations'
    _GE_VALIDATION_OPERATOR = 'validate_and_store_results'
    _GE_RUN_NAME = 'dq_tool_on_demand_run'

    @property
    def has_expectation_store(self):
        """Is DQTool using an expectation store?"""
        return self._has_expectation_store

    @property
    def _user_identity_provider(self):
        """A user identity provider, initialized as databricks identity provider if we have spark"""
        if self._saved_user_identity_provider:
            return self._saved_user_identity_provider
        if self._spark:
            self._saved_user_identity_provider = DatabricksIdentityProvider(spark=self._spark)
            return self._saved_user_identity_provider
        return None

    def _get_struct_schema(self, schema: dict) -> 'StructType':
        """Get a spark struct schema from a dict schema"""
        dummy_df = self._spark.createDataFrame([], 'int')
        spark_struct_type = dummy_df.schema.__class__
        return spark_struct_type.fromJson(schema)

    def read_csv(self, path: str, schema) -> 'DataFrame':
        """Currently just csv files are supported"""
        # if it's a "jsonValue" convert it to StructType
        if isinstance(schema, dict):
            schema = self._get_struct_schema(schema)
        return self._spark.read.csv(
            path=path,
            header=True,
            schema=schema,
            enforceSchema=False,
            mode='FAILFAST'
        )

    def generate_schema(self, path: str = None, df: 'DataFrame' = None, print_it: bool = True) -> dict:
        """Generate a spark schema from a csv at the given path."""
        if path and df:
            raise ValueError('Both path and df were passed. You need to pass either path or df')
        if not df:
            if not path:
                raise ValueError('Both path and df are empty. You need to pass either path or df')
            df = self._spark.read.csv(
                path=path,
                header=True
            )
        schema = df.schema.jsonValue()
        if print_it:
            pretty_print(schema)
        return schema

    def generate_expectations(
        self,
        df: 'DataFrame',
        expectation_suite_name: str = None
    ) -> ExpectationSuite:
        """Generate an initial set of expectations"""
        df = df.limit(self._GENERATE_COUNT)
        batch_kwargs = {
            "datasource": self._GE_DATASOURCE,
            "dataset": df
        }
        ge_results = self._context.profile_data_asset(
            datasource_name=self._GE_DATASOURCE,
            batch_kwargs=batch_kwargs,
            expectation_suite_name=expectation_suite_name or self._GE_SUITE_GENERATED_NAME
        )
        expectations = ge_results['results'][0][0].to_json_dict()
        return ExpectationSuite(expectation_suite=expectations)

    def validate(
        self,
        df: 'DataFrame',
        expectations: Union[dict, ExpectationSuite],
        save_suite: bool = True
    ) -> ValidationResult:
        """Validate a dataset using given expectations"""
        # create a suite using schema
        if isinstance(expectations, ExpectationSuite):
            expectations = expectations.to_dict()
        if not isinstance(expectations, dict):
            raise ValueError((
                'The expectations needs to be a dict or an ExpectationSuite. The value is {}, type {}. '
                'If you have a list of expectations, create an ExpectationSuite first.'
            ).format(expectations, expectations.__class__))
        # copy suite meta to batch parameters - if any
        dq_tool_meta = expectations.get('meta', {}).get(ExpectationSuite.META_KEY)
        batch_parameters = {ExpectationSuite.META_KEY: dq_tool_meta} if dq_tool_meta else None
        suite = GEexpectationSuiteSchema.load(expectations)

        # batch from the class (might be custom)
        batch = self._expectation_class(
            spark_df=df,
            expectation_suite=suite,
            data_context=self._context,
            batch_parameters=batch_parameters
        )
        run_id = {
            'run_time': datetime.now().astimezone(),
            'run_name': self._GE_RUN_NAME
        }
        # run the validation
        ge_results = self._context.run_validation_operator(
            validation_operator_name=self._GE_VALIDATION_OPERATOR,
            assets_to_validate=[batch],
            run_id=run_id
        )
        # save the expectation suite
        if save_suite:
            self._context.save_expectation_suite(expectation_suite=suite)
        # get the expectation suite results from it
        results = ge_results.list_validation_results()[0].to_json_dict()
        return ValidationResult(self, results)

    def get_expectation_suite(
        self,
        expectations: Union[dict, List[dict], ExpectationSuite] = None,
        name: str = None
    ) -> ExpectationSuite:
        """Get an expectation suite, with the given expectations.
        expectations can be empty (you get an empty suite),
        or it can contain a dict obtained from generate_expectations,
        or a list of expectations created in playground
        """
        expectations = expectations or {}
        # if expectations are already in a suite, just return them
        if isinstance(expectations, ExpectationSuite):
            return expectations
        # expectations ready - create a suite
        if expectations and isinstance(expectations, dict):
            return ExpectationSuite(expectation_suite=expectations)

        # create new expectations and add the expectations there if there are any
        ge_exps = GEExpectationSuite(
            expectation_suite_name=name or self._GE_SUITE_AUTHORED_NAME,
        ).to_json_dict()
        if isinstance(expectations, list):
            # expectations in the list can be a dict or a GE class convertable to dict
            ge_exps['expectations'] = [
                exp.expectation_config.to_json_dict() if hasattr(exp, 'expectation_config') else exp
                for exp in expectations
            ]
        return ExpectationSuite(expectation_suite=ge_exps)

    def get_playground(
        self,
        df: 'DataFrame' = None,
        table_name: str = None,
        database_name: str = None,
        row_count_limit: int = 500
    ) -> SparkDFDataset:
        """Get a playground object that you can use to develop your expectations"""
        if table_name:
            if df:
                raise ValueError(
                    'Both df: {} and table_name: {} given. Choose one or the other.'.format(df, table_name)
                )
            dotted_name = HiveMetastore.get_dot_table_name(
                table_name=table_name,
                database_name=database_name
            )

            df = self._spark.table(dotted_name)
            if row_count_limit:
                df = df.limit(row_count_limit)

        playground = self._expectation_class(spark_df=df)
        method = types.MethodType(run_expectation, playground)
        setattr(playground, 'run_expectation', method)
        return playground
