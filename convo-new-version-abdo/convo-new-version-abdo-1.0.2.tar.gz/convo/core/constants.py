BY_DEFAULT_SERVER_PORT = 5005

BY_DEFAULT_SERVER_FORMAT = "{}://localhost:{}"

BY_DEFAULT_SERVER_URL = BY_DEFAULT_SERVER_FORMAT.format("http", BY_DEFAULT_SERVER_PORT)

BY_DEFAULT_NLU_FALL_BACK_THRESHOLD = 0.3

BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD = 0.1

BY_DEFAULT_CORE_FALL_BACK_THRESHOLD = 0.3

BY_DEFAULT_REQUEST_TIMEOUT = 60 * 5  # 5 minutes

BY_DEFAULT_RESPONSE_RESULT_TIMEOUT = 60 * 60  # 1 hour

BY_DEFAULT_LOCK_LIFETIME = 60  # in seconds

BEARER_TOKEN_AFFIXES = "Bearer "

# the lowest priority intended to be used by machine learning policies
BY_DEFAULT_POLICY_PREFERENCE = 1
# the priority intended to be used by mapping policies
MAPPING_POLICY_PREFERENCE = 2
# the priority intended to be used by memoization policies
# it is higher than default and mapping to prioritize training stories
MEMOIZATION_POLICY_PREFERENCE = 3
# the priority intended to be used by fallback policies
# it is higher than memoization to prioritize fallback
FALLBACK_POLICY_PREFERENCE = 4
# the priority intended to be used by form policies
# it is the highest to prioritize form to the rest of the policies
FORM_POLICY_PRIORITY = 5
# The priority of the `RulePolicy` is higher than the priorities for `PolicyFallback`,
# `TwoStageFallbackPolicy` and `FormPolicy` to make it possible to use the
# `RulePolicy` in conjunction with these deprecated policies.
RULE_POLICY_PREFERENCE = 6

COMMUNICATION = "dialogue"

# RabbitMQ message property header added to events published using `convo export`
EXPORT_PROCESS_ID_HEADER_NAME = "convo-export-process-id"

# Name of the environment variable defining the PostgreSQL schema to access. See
# https://www.postgresql.org/docs/9.1/ddl-schemas.html for more details.
POSTGRESQL_SCHEMA_NAME = "POSTGRESQL_SCHEMA_NAME"

# Names of the environment variables defining PostgreSQL pool size and max overflow
POSTGRESQL_POOL_SIZE = "SQL_POOL_SIZE"
POSTGRESQL_MAXIMUM_OVERFLOW = "SQL_MAX_OVERFLOW"
