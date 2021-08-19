import os


class ServiceConfig:
    SERVICE_NAME = os.getenv('SERVICE_NAME', 'microservice_template_core')
    SERVICE_PORT = os.getenv('SERVICE_PORT', 8081)
    SERVER_NAME = os.getenv('SERVER_NAME', "0.0.0.0")
    URL_PREFIX = os.getenv('URL_PREFIX', '/api/v1')
    SERVICE_NAMESPACE = os.getenv('SERVICE_NAMESPACE', 'dev')
    POD_NAME = os.getenv('POD_NAME', '')
    configuration = {}


class LoggerConfig:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOGGING_VERBOSE = os.getenv('LOGGING_VERBOSE', False)
    LOKI_SERVER = os.getenv('LOKI_SERVER', '127.0.0.1')
    LOKI_PORT = os.getenv('LOKI_PORT', 3100)


class TracerConfig:
    JAEGER_SERVER = os.getenv('JAEGER_SERVER', '127.0.0.1')
    JAEGER_PORT = int(os.getenv('JAEGER_PORT', 6831))


class FlaskConfig:
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
    FLASK_THREADED = os.getenv('FLASK_THREADED', False)

    FLASK_JWT = os.getenv('FLASK_JWT', True)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'khFw8H5hP3gQ9kKS')
    JWT_DECODE_ALGORITHMS = os.getenv('JWT_DECODE_ALGORITHMS', ['RS256'])
    JWT_IDENTITY_CLAIM = os.getenv('JWT_IDENTITY_CLAIM', 'sub')
    JWT_USER_CLAIMS = os.getenv('JWT_USER_CLAIMS', 'authorities')
    PROPAGATE_EXCEPTIONS = os.getenv('PROPAGATE_EXCEPTIONS', True)


class DbConfig:
    USE_DB = os.getenv('USE_DB', False)
    DATABASE_SERVER = os.getenv('DATABASE_SERVER', '127.0.0.1')
    DATABASE_PORT = os.getenv('DATABASE_PORT', 3306)
    DATABASE_USER = os.getenv('DATABASE_USER', 'microservice_template_core')
    DATABASE_PSWD = os.getenv('DATABASE_PSWD', 'microservice_template_core')
    DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA', 'harp')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DATABASE_USER}:{DATABASE_PSWD}@' \
                              f'{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_SCHEMA}'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    SQLALCHEMY_POOL_RECYCLE = os.getenv('', 300)


class AerospikeConfig:
    AEROSPIKE_USER = os.getenv('AEROSPIKE_USER', 'admin')
    AEROSPIKE_PASS = os.getenv('AEROSPIKE_PASS', 'admin')
    AEROSPIKE_HOST = os.getenv('AEROSPIKE_HOST', '127.0.0.1')
    AEROSPIKE_PORT = int(os.getenv('AEROSPIKE_PORT', 3000))
    AEROSPIKE_NAMESPACE = os.getenv('AEROSPIKE_NAMESPACE', 'harpia')


class KafkaConfig:
    KAFKA_USER = os.getenv('KAFKA_USER', 'admin')
    KAFKA_PASS = os.getenv('KAFKA_PASS', 'admin')
    KAFKA_SERVERS = os.getenv('KAFKA_SERVERS', '127.0.0.1:9092')
