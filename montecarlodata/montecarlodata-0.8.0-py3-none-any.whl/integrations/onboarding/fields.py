# Query responses
EXPECTED_GENERIC_DB_GQL_RESPONSE_FIELD = 'testDatabaseCredentials'
EXPECTED_HIVE_S3_GQL_RESPONSE_FIELD = 'testS3Credentials'
EXPECTED_HIVE_SQL_GQL_RESPONSE_FIELD = 'testHiveCredentials'
EXPECTED_PRESTO_SQL_GQL_RESPONSE_FIELD = 'testPrestoCredentials'
EXPECTED_PRESTO_S3_GQL_RESPONSE_FIELD = 'testS3Credentials'
EXPECTED_GLUE_GQL_RESPONSE_FIELD = 'testGlueCredentials'
EXPECTED_ATHENA_GQL_RESPONSE_FIELD = 'testAthenaCredentials'
EXPECTED_SPARK_GQL_RESPONSE_FIELD = 'testSparkCredentials'
EXPECTED_SNOWFLAKE_GQL_RESPONSE_FIELD = 'testSnowflakeCredentials'
EXPECTED_BQ_GQL_RESPONSE_FIELD = 'testBqCredentials'
EXPECTED_TOGGLE_EVENTS_GQL_RESPONSE_FIELD = 'toggleEventConfig'
EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD = 'updateCredentials'
EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD = 'removeConnection'

# Available connections types
HIVE_MYSQL_CONNECTION_TYPE = 'hive-mysql'
HIVE_S3_CONNECTION_TYPE = 'hive-s3'
HIVE_SQL_CONNECTION_TYPE = 'hive'
PRESTO_SQL_CONNECTION_TYPE = 'presto'
PRESTO_S3_CONNECTION_TYPE = 'presto-s3'
GLUE_CONNECTION_TYPE = 'glue'
ATHENA_CONNECTION_TYPE = 'athena'
SPARK_CONNECTION_TYPE = 'spark'
REDSHIFT_CONNECTION_TYPE = 'redshift'
SNOWFLAKE_CONNECTION_TYPE = 'snowflake'
BQ_CONNECTION_TYPE = 'bigquery'

# Available warehouse types
DATA_LAKE_WAREHOUSE_TYPE = 'data-lake'
REDSHIFT_WAREHOUSE_TYPE = REDSHIFT_CONNECTION_TYPE
SNOWFLAKE_WAREHOUSE_TYPE = SNOWFLAKE_CONNECTION_TYPE
BQ_WAREHOUSE_TYPE = BQ_CONNECTION_TYPE

# S3 event types
S3_METADATA_EVENT_TYPE = 's3_metadata_events'
S3_QL_EVENT_TYPE = 's3_ql_events'

# Job types
QL_JOB_TYPE = ['query_logs']

# Job limits
PRESTO_CATALOG_KEY = 'catalog_name'
HIVE_GET_PARTS_KEY = 'get_partition_locations'
HIVE_MAX_PARTS_KEY = 'max_partition_locations'
HIVE_MAX_PARTS_DEFAULT_VALUE = 50

# Certificate details
S3_CERT_MECHANISM = 'dc-s3'
PRESTO_CERT_PREFIX = 'certificates/presto/'
AWS_RDS_CA_CERT = 'https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem'

# Connections to friendly name (i.e. human presentable) map
GQL_TO_FRIENDLY_CONNECTION_MAP = {
    HIVE_MYSQL_CONNECTION_TYPE: 'Hive (metastore)',
    HIVE_S3_CONNECTION_TYPE: 'Hive (EMR logs)',
    HIVE_SQL_CONNECTION_TYPE: 'Hive (SQL)',
    PRESTO_SQL_CONNECTION_TYPE: PRESTO_SQL_CONNECTION_TYPE.capitalize(),
    PRESTO_S3_CONNECTION_TYPE: 'Presto (logs)',
    GLUE_CONNECTION_TYPE: GLUE_CONNECTION_TYPE.capitalize(),
    ATHENA_CONNECTION_TYPE: 'Athena',
    SPARK_CONNECTION_TYPE: 'Spark (SQL)',
    REDSHIFT_CONNECTION_TYPE: REDSHIFT_CONNECTION_TYPE.capitalize(),
    SNOWFLAKE_CONNECTION_TYPE: SNOWFLAKE_CONNECTION_TYPE.capitalize(),
    BQ_CONNECTION_TYPE: 'BigQuery'
}

# Failure Verbiage
OPERATION_ERROR_VERBIAGE = 'Operation failed - This might not be a valid connection for your account. ' \
                           'Please contact Monte Carlo.'
