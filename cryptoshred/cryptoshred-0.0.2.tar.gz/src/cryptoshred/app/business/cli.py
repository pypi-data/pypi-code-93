from cryptoshred.backends import KeyBackend, DynamoDbSsmBackend
from cryptoshred.config import get_configuration


def get_key_backend(profile: str = "default") -> KeyBackend:
    config = get_configuration(profile=profile)
    return DynamoDbSsmBackend(
        iv_param=config.dynamo_backend_iv_param,
        table_name=config.dynamo_backend_table_name,
    )
