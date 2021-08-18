import pandas as pd
from pathlib import Path
from types import FunctionType
from typing import List, Optional
import webbrowser
import yaml

from .error import APIError, ParameterValueError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, FeatureSet, DataSource
from pyrasgo.schemas.enums import Granularity, ModelType
from pyrasgo.storage.dataframe import utils as dfutils
from pyrasgo.utils import ingestion, naming, track_usage


class Publish():

    def __init__(self):
        from . import Create, Get, Match, Save, Update
        from .connection import Connection
        from pyrasgo.config import get_session_api_key
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()
        self.match = Match()
        self.create = Create()
        self.update = Update()
        self.save = Save()


    @track_usage
    def experiment(self, df: pd.DataFrame,
                         dimensions: List[str],
                         granularity: List[str],
                         features: List[str] = [],
                         return_cli_only: bool = True,
                         verbose: bool = True) -> Collection:
        """
        Accepts a dataframe and publishes:
        - DataFrame as Rasgo DataSource
        - Dataframe columns as Rasgo Features
        - Rasgo Collection comprised of all Features

        params
        ------
        df: DataFrame: Pandas DataFrame to use as source data
        features: List[str]: List of columns to add as features.
                  If none is passed, all columns not in `dimensions` list will be registered as features
        dimensions: List[str]: List of columns to add as dimensions
        granularity: List[str]: List of granularities to apply to dimensions
        verbose: boolean: Print status statements to stdout while function executes

        Returns Rasgo Collection
        """
        if verbose:
            print('Publishing DataFrame as a Rasgo DataSource')
        try:
            source = self.source_data(source_type='dataframe', df=df, verbose=verbose)
            if verbose:
                print('Successfully created:', source)
        except Exception as e:
            print(f'Failed to create DataSource: {e}')
            return
        if verbose:
            print('Creating Features from DataSource')
        try:
            dimensions, features = dfutils.confirm_df_columns(df, dimensions, features)
            feature_set = self.features_from_source(source.id,
                                            features=features,
                                            dimensions=dimensions,
                                            granularity=granularity)
            features = self.get.features_by_featureset(feature_set.id)
            if verbose:
                print('Successfully created:', features)
        except Exception as e:
            print(f'Failed to create Features: {e}')
            return
        if verbose:
            print('Creating a Collection of your Features')
        try:
            collection = self.create.collection('name', 'Timeseries', granularity[0])
            collection.add_features(features)
            collection.generate_training_data()
            if verbose:
                print('Successfully created:', collection)
        except Exception as e:
            print(f'Failed to create Collection: {e}')
            return
        if not return_cli_only:
            webbrowser.open(f"app.rasgoml.com/collections/{collection.id}")
        return collection

    @track_usage
    def features(self, features_dict: dict,
                 trigger_stats: bool = True) -> FeatureSet:
        f"""
        Creates or updates Features based on metadata provided in the dict

        params:
            features_dict: Valid Rasgo dict (see below)

        return:
            Rasgo FeatureSet

        Valid Rasgo dict format:
        -----------------------
        {ingestion.RASGO_DICT}
        """
        # TODO need to publish docs on granularity and data types
        return self.save.feature_set_dict(features_dict, trigger_stats)

    @track_usage
    def features_from_df(self,
                         df: pd.DataFrame,
                         dimensions: List[str],
                         features: List[str],
                         granularity: List[str] = [],
                         tags: List[str] = [],
                         sandbox: bool = True):
        raise NotImplementedError("`publish.features_from_df()` is a deprecated method. "
                                  "Please use `publish.features()` or `publish.features_from_source()` instead")

    @track_usage
    def features_from_source(self,
                             data_source_id: int,
                             dimensions: List[str],
                             features: List[str] = [],
                             granularity: List[str] = [],
                             tags: List[str] = [],
                             feature_set_name: str = None,
                             sandbox: bool = True,
                             trigger_stats: bool = True,
                             if_exists: str = 'fail',
                             verbose: bool = False) -> FeatureSet:
        """
        Publishes a FeatureSet from an existing DataSource table

        params:
            data_source_id: ID to a Rasgo DataSource
            features: List of column names that will be features
                      If none is passed, all columns not in `dimensions` list will be registered as features
            dimensions: List of column names that will be dimensions
            granularity: List of grains that describe the form of the data. Common values are: 'day', 'week', 'month', 'second'
            tags: List of tags to be added to all features
            feature_set_name: Optional name for the FeatureSet (if not passed a random string will be assigned)
            sandbox: boolean: False = Production, True = Sandbox
            if_exists:  fail - returns an error message if a featureset already exists against this table
                        return - returns the featureset without operating on it
                        edit - edits the existing featureset
                        new - creates a new featureset
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo FeatureSet
        """
        # V1 Trade-offs / Possible Future Enhancements
        # --------------
        # Constucting a featureset using v0 method - cut over to v1
        # We aren't adding display names, descriptions to features

        # Check for valid DataSource
        data_source = self.get.data_source(data_source_id)
        if not data_source.table:
            raise ValueError(f"DataSource {data_source_id} is not usable. Please make sure it exists and has a valid table registered.")
        if not isinstance(dimensions, list) and all([isinstance(dimension, str) for dimension in dimensions]):
            raise TypeError('Dimensions must be provided as a list of strings.')
        if not isinstance(features, list) and all([isinstance(feature, str) for feature in features]):
            raise TypeError('Features must be provided as a list of strings.')
        if not isinstance(granularity, list):
            if isinstance(granularity, str):
                granularity = [granularity]
            else:
                raise TypeError("granularity must be provided as a list of strings")
        if not isinstance(tags, list):
            if isinstance(tags, str):
                tags = [tags]
            else:
                raise TypeError("tags must be provided as a list of strings")
        if len(granularity) > len(dimensions):
            raise APIError("Number of granularities cannot exceed number of dimensions."
                           "Dimensions are the index fields your data should join on and group by."
                           "Granularity is an attribute that describes precision of your dimensions."
                           "Consider passing more dimensions or fewer granularities.")

        db = data_source.tableDatabase.upper() if data_source.tableDatabase else None
        schema = data_source.tableSchema.upper() if data_source.tableSchema else None
        table = data_source.table.split(".")[-1] if data_source.table.count(".") > 0 else data_source.table
        if verbose:
            print(f"Publishing features from source table {db}.{schema}.{table}")

        # Handle if FeatureSet already exists
        feature_set = self.match.feature_set(table_name=table)
        if feature_set and if_exists == 'fail':
            raise APIError(f"A featureset ({feature_set.id} - {feature_set.name}) is already built against this table. "
                            "Pass parameter if_exists = 'edit', 'new', or 'return' to continue.")

        columns = self.data_warehouse.get_source_columns(table=table, database=db, schema=schema)
        if columns.empty:
            raise APIError("The table associated with this DataSource is not accessible.")
        dimensions, features = dfutils.confirm_list_columns(columns["COLUMN_NAME"].values.tolist(), dimensions, features)

        # Publish Featureset V0
        timestamp = naming.make_timestamp()
        feature_set = self.save.feature_set(name=feature_set_name or data_source.name+"_"+timestamp,
                                            data_source_id=data_source.id,
                                            table_name=data_source.table,
                                            source_code=data_source.sourceCode,
                                            if_exists=if_exists)

        for _i, row in columns.iterrows():
            if row["COLUMN_NAME"] in dimensions:
                # Dimension / Granularity order matching:
                try:
                    # Try to match the position of the dim with the position of the granularity
                    dim_pos = dimensions.index(row['COLUMN_NAME'])
                    dim_granularity = granularity[dim_pos] if len(granularity) > 1 else granularity[0]
                except:
                    # Otherwise default to the next granularity in the list
                    dim_granularity = granularity.pop(0) if len(granularity) > 1 else granularity[0]
                self.save.dimension(feature_set_id=feature_set.id,
                                    column_name=row["COLUMN_NAME"],
                                    data_type=naming._cleanse_sql_data_type(row["DATA_TYPE"]),
                                    granularity=dim_granularity,
                                    if_exists=if_exists)

            if row["COLUMN_NAME"] in features:
                if verbose:
                    print(f'Publishing feature {row["COLUMN_NAME"]}')
                self.save.feature(feature_set_id=feature_set.id,
                                  display_name=row["COLUMN_NAME"],
                                  data_type=naming._cleanse_sql_data_type(row["DATA_TYPE"]),
                                  description=f"Feature {row['COLUMN_NAME']} created from DataSource {data_source.table}",
                                  column_name=row["COLUMN_NAME"],
                                  granularity=granularity[0],
                                  tags=tags,
                                  status="Sandboxed" if sandbox else "Productionized",
                                  if_exists=if_exists)

        if trigger_stats:
            if verbose:
                print("Triggering stats for all features. These may take a few minutes to run.")
            self.create.feature_set_stats(feature_set.id)
        return self.get.feature_set(feature_set.id)

    @track_usage
    def features_from_source_code(self,
                                  data_source_id: int,
                                  source_code_type: str,
                                  dimensions: List[str],
                                  features: List[str] = [],
                                  granularity: List[str] = [],
                                  tags: List[str] = [],
                                  sql_definition: str = None,
                                  python_function: FunctionType = None,
                                  feature_set_name: str = None,
                                  feature_set_table_name: str = None,
                                  sandbox: bool = True,
                                  sql_risk_override: bool = False,
                                  trigger_stats: bool = True,
                                  if_exists: str = 'fail',
                                  verbose: bool = False) -> FeatureSet:
        """
        Publishes a FeatureSet from an existing DataSource table

        params:
            data_source_id: ID to a Rasgo DataSource
            source_code_type: Valid string values are ['sql', 'python']
            sql_definition: Valid sql select statement that can create a view
            python_function: Valid python function that accepts a dataframe as input and returns a dataframe of features
            features: List of column names that will be features
                      If none is passed, all columns not in `dimensions` list will be registered as features
            dimensions: List of column names that will be dimensions
            granularity: List of grains that describe the form of the data. Common values are: 'day', 'week', 'month', 'second'
            tags: List of tags to be added to all features
            feature_set_name: Optional name for the FeatureSet (if not passed a random string will be assigned)
            sandbox: boolean: False = Production, True = Sandbox
            sql_risk_override: boolean: pass True if you receive a warning message about a dangerous sql keyword
            if_exists:  fail - returns an error message if a featureset already exists against this table
                        return - returns the featureset without operating on it
                        edit - edits the existing featureset
                        new - creates a new featureset
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo FeatureSet
        """
        source_code_type = source_code_type.lower()
        if source_code_type not in ["sql", "python"]:
            raise ParameterValueError("source_code_type", ["sql", "python"])
        if source_code_type == "sql":
            if not sql_definition:
                raise ParameterValueError("sql_definition", ["Valid sql select statement that can create a veiw"])
        elif source_code_type == "python":
            raise APIError("Not supporting python functions quite yet...")
            if not python_function:
                raise ParameterValueError("python_function", ["Valid python function that accepts a dataframe as input and returns a dataframe of features"])

        # Publish the new data as a source
        # First make sure this is a valid source
        parent_source = self.get.data_source(data_source_id)
        if verbose:
            print(f"Publishing derivative source from parent source {parent_source.table}")
        child_source = self.source_data(source_type=source_code_type,
                                        sql_definition=sql_definition if source_code_type == "sql" else None,
                                        python_function=python_function if source_code_type == "python" else None,
                                        data_source_name=feature_set_name,
                                        data_source_table_name=feature_set_table_name,
                                        parent_data_source_id=data_source_id,
                                        sql_risk_override=sql_risk_override,
                                        trigger_stats=trigger_stats,
                                        if_exists=if_exists)

        # Then publish features
        if verbose:
            print(f"Publishing features from derivative source {child_source.id}")
        return self.features_from_source(data_source_id=child_source.id,
                                         features=features,
                                         dimensions=dimensions,
                                         granularity=granularity,
                                         tags=tags,
                                         feature_set_name=feature_set_name,
                                         sandbox=sandbox,
                                         trigger_stats=trigger_stats,
                                         if_exists=if_exists)

    @track_usage
    def features_from_yml(self,
                          yml_file: str,
                          sandbox: Optional[bool] = True,
                          git_repo: Optional[str] = None,
                          trigger_stats: bool = True,
                          verbose: bool = False) -> FeatureSet:
        """
        Publishes metadata about a FeatureSet to Pyrasgo

        params:
            yml_file: Rasgo compliant yml file that describes the featureset(s) being created
            sandbox: Status of the features (True = 'Sandboxed' | False = 'Productionized')
            git_repo: Filepath string to these feature recipes in git
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo FeatureSet
        """
        with open(yml_file) as fobj:
            if verbose:
                print("Unpacking yml")
            contents = yaml.load(fobj, Loader=yaml.SafeLoader)
        if isinstance(contents, list):
            raise APIError("More than one feature set found, please pass in only one feature set per yml")
        else:
            if verbose:
                print("Publishing features")
            feature_set = self.save.feature_set_dict(contents, trigger_stats)
        return feature_set

    @track_usage
    def source_data(self,
                    source_type: str,
                    file_path: Path = None,
                    df: pd.DataFrame = None,
                    table: str = None,
                    table_database: Optional[str] = None,
                    table_schema: Optional[str] = None,
                    sql_definition: str = None,
                    python_function: FunctionType = None,
                    data_source_name: str = None,
                    data_source_domain: str = None,
                    data_source_table_name: str = None,
                    parent_data_source_id: Optional[int] = None,
                    sql_risk_override: bool = False,
                    trigger_stats: bool = True,
                    if_exists: str = 'fail',
                    verbose: bool = True
                    ) -> DataSource:
        """
        Push a csv, Dataframe, or table to a Snowflake table and register it as a Rasgo DataSource (TM)

        NOTES: csv files will import all columns as strings

        params:
            source_type: Values: ['csv', 'dataframe', 'table', 'sql', 'python']
            df: pandas DataFrame (only use when passing source_type = 'dataframe')
            file_path: full path to a file on your local machine (only use when passing source_type = 'csv')
            table: name of a valid Snowflake table in your Rasgo account (only use when passing source_type = 'table')
            table_database: Optional: name of the database of the table passed in 'table' param (only use when passing source_type = 'table')
            table_schema: Optional: name of the schema of the table passed in 'table' param (only use when passing source_type = 'table')
            sql_definition: Optional: valid SQL string that will create a new view in your DataWarehous
            python_function: Optional: valid python function that accepts a dataframe as input and returns a dataframe of features
            data_source_name: Optional name for the DataSource (if not provided a random string will be used)
            data_source_table_name: Optional name for the DataSource table in Snowflake (if not provided a random string will be used)
            data_source_domain: Optional domain for the DataSource (default is NULL)
            parent_data_source_id: Optional ID of a valid Rasgo DataSource that is a parent to this DataSource (default is NULL)
            sql_risk_override: boolean: pass True if you receive a warning message about a dangerous sql keyword
            if_exists: Values: ['fail', 'append', 'replace'] directs the function what to do if a DataSource already exists with this table name  (defaults to fail)
            verbose: boolean: Print status statements to stdout while function executes

        return:
            Rasgo DataSource
        """
        # V1 Trade-offs / Possible Future Enhancements
        # --------------
        # csv's upload with all columns as string data type
        # uploading csv locally vs. calling the post/data-source/csv endpoint

        # Validate inputs
        vals = ["csv", "dataframe", "table", "sql"]
        source_type = source_type.lower()
        _org_defaults = self.api._get_default_namespace()

        if source_type not in vals:
            raise ParameterValueError("sourceType", vals)
        if source_type == "csv" and not Path(file_path).exists():
                raise FileNotFoundError("Please pass in a valid file path using the `file_path` parameter")
        if source_type == "dataframe":
            if not isinstance(df, pd.DataFrame) or df.empty:
                raise ValueError("Please pass in a valid DataFrame using the `df` parameter")
        if source_type == 'sql':
            if not sql_definition:
                raise ValueError('Please pass in a valid SQL string using the `sql_definition` parameter')
            #check for dangerous sql
            if naming._is_scary_sql(sql_definition) and not sql_risk_override:
                # NOTE: In the future we will want to send an email to the account owner
                #       or require special permissions to run with a sql_risk_override param
                raise ValueError("It looks like the sql string you passed may have some potentially dangerous keywords in it like DELETE or DROP or TRUNCATE. "
                                 "This SQL will be used to create a view in your DataWarehouse. Please ensure this is the code you want to run. "
                                 "If you're confident in your code, please pass in the parameter `sql_risk_override=True` to run this code.")
            if not naming._is_valid_view_sql(sql_definition) and not sql_risk_override:
                raise ValueError("It looks like the sql string you passed is missing basic elements like a SELECT or FROM clause. "
                                 "This SQL will be used to create a view in your DataWarehouse. Please ensure this is the code you want to run. "
                                 "If you're confident in your code, please pass in the parameter `sql_risk_override=True` to run this code.")
        if source_type == "table":
            if not table:
                raise ValueError("Please pass in a valid table using the `table` parameter")
            if if_exists in ["append", "replace"]:
                # Raise this as an error after we've confirmed there will be no backwards compat issues
                print("Data Sources built from SQL tables do not physically append or replace data, proceeding with a no-op registration.")
            parsed_database, parsed_schema, parsed_table = naming.parse_fqtn(table, _org_defaults)
            table = parsed_table
            table_database = table_database or parsed_database
            table_schema = table_schema or parsed_schema
            try:
                src_table = self.data_warehouse.get_source_table(table_name=table, database=table_database, schema=table_schema, record_limit=10)
                if src_table.empty:
                    raise APIError(f"Source table {table} is empty or this role does not have access to it.")
            except:
                raise APIError(f"Source table {table} does not exist or this role does not have access to it.")
        if data_source_table_name == "":
            raise ValueError("The `data_source_table_name` parameter was passed as a blank string, please pass in a valid SQL table name")

        # Determine the ouput table based on user inputs
        if source_type in ["csv", "dataframe", "sql"]:
            table_name = data_source_table_name or naming.random_table_name()
        else: #source_type == "table":
            table_name = table
        table_name = table_name.upper()
        table_database = table_database if source_type == "table" else _org_defaults.get('database')
        table_schema = table_schema if source_type == "table" else _org_defaults.get('schema')
        table_fqtn = naming.make_fqtn(table=table_name, database=table_database, schema=table_schema)

        # Check if a DataSource already exists
        data_source = self.match.data_source(fqtn=table_fqtn)
        if data_source:
            # If it does, override to the existing table
            table_name = data_source.table
            table_database = data_source.tableDatabase
            table_schema = data_source.tableSchema
            table_fqtn = naming.make_fqtn(table=table_name, database=table_database, schema=table_schema)

            # Then handle input directives
            vals = ["append", "fail", "replace"]
            msg = f"DataSource {data_source.id} already exists. "
            if data_source.organizationId != self.api._profile.get('organizationId'):
                raise APIError(msg+"This API key does not have permission to replace it.")
            if data_source.sourceType != source_type:
                raise APIError(msg+"Your input parameters would edit the source_type. To change DataSource attributes, use the update_data_source method. To update this source table, ensure your input parameters match the DataSource definition.")
            if if_exists not in vals:
                raise ParameterValueError("if_exists", vals)
            if if_exists == 'fail':
                raise APIError(msg+"Pass if_exists='replace' or 'append' to proceed.")

        # Determine operation to perform: [create, append, replace, register, no op]
        _operation = self._source_table_operation(source_type, if_exists, table_fqtn, org_defaults=_org_defaults)
        if verbose:
            print(f"Proceeding with operation {_operation}")

        # Upload to Snowflake
        # Path: csv & dataframe
        if source_type in ["csv", "dataframe"]:
            if source_type == "csv":
                df = pd.read_csv(file_path)
            if verbose:
                print("Uploading to table:", table_name)
            dfutils._cleanse_sql_dataframe(df)
            self.data_warehouse.write_dataframe_to_table(df, table_name=table_name, append=True if if_exists=="append" else False)
            self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

        # Path: python
        if source_type == "python":
            raise NotImplementedError("Not supporting python source code just yet...")

        # Path: sql
        if source_type == "sql":
            view_query = f"CREATE OR REPLACE VIEW {table_name} AS {sql_definition};"
            if verbose:
                print("Creating sql view as:", view_query)
            self.data_warehouse.execute_query(view_query)
            self.data_warehouse.grant_table_ownership(table=table_name, role=self.data_warehouse.publisher_role)
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role)

        # Path: table
        if source_type == "table":
            if verbose:
                print(f"Granting read access on table {table_name} to {self.data_warehouse.reader_role.upper()}")
            # NOTE: grant_table_acess is intentional here
            # In other methods, we create a table with the rasgo user role and want to hand if off to the reader role
            # In this case, the table is likely part of a pre-existing rbac model and we just want to grant rasgo access
            self.data_warehouse.grant_table_access(table=table_name, role=self.data_warehouse.reader_role, database=table_database, schema=table_schema)

        # Publish DataSource
        data_source = self.save.data_source(name=data_source_name or table_name,
                                            table=table_name,
                                            database=table_database if source_type == 'table' else _org_defaults.get('database'),
                                            schema=table_schema if source_type == 'table' else _org_defaults.get('schema'),
                                            source_code=sql_definition if source_type == 'sql' else None,
                                            domain=data_source_domain,
                                            source_type=source_type,
                                            parent_source_id=parent_data_source_id,
                                            if_exists='edit')
        if data_source:
            if trigger_stats:
                self.create.data_source_stats(data_source.id)
            return data_source
        else:
            raise APIError("DataSource failed to upload")

    def _source_table_operation(self,
                                source_type: str,
                                if_exists: str,
                                to_fqtn: str,
                                from_fqtn: Optional[str] = None,
                                org_defaults: Optional[dict] = None):
        """
        Called by publish_source_data:
            Given a source_type and tables, return the operation that should be performed to publish this table
        """
        to_database, to_schema, to_table = naming.parse_fqtn(to_fqtn, org_defaults)
        data_source_exists = True if self.match.data_source(fqtn=to_fqtn) is not None else False

        try:
            dest_table = self.data_warehouse.get_source_table(table_name=to_table, database=to_database, schema=to_schema, record_limit=10)
            is_dest_table_empty = dest_table.empty
        except:
            is_dest_table_empty = True

        if source_type in ["csv", "dataframe", "sql"]:
            if not data_source_exists:
                if is_dest_table_empty:
                    return "create"
                else: #not is_dest_table_empty
                    raise APIError(f"A table named {to_fqtn} already exists, but is not registered as a Rasgo DataSource. "
                                   f"Try running this function with params: source_type='table', table='{to_table}'. "
                                    "If this wasn't an intentional match, run this function again to generate a new table name.")
            elif data_source_exists:
                if is_dest_table_empty:
                    return "create"
                else: #not is_dest_table_empty
                    return if_exists
            else:
                raise APIError("Could not determine what operation to perform.")
        elif source_type == "table":
            if not data_source_exists:
                return "register"
            elif not is_dest_table_empty and if_exists in ["append", "replace"]:
                print(f"pyRasgo does not support {if_exists} operations on tables yet.")
            return "no op"
        else:
            raise APIError("Could not determine what operation to perform.")