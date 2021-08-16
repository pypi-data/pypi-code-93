import os
import logging.config

from pentaquark.config import gconf as config

if os.getenv("ENV", "").lower() == "test":
    ENV_FILE = ".env.test"
elif os.getenv("PENTAQUARK_ENV_FILE_PATH"):
    ENV_FILE = os.getenv("PENTAQUARK_ENV_FILE_PATH")
else:
    ENV_FILE = ".env"

config.feed_from_env_file(env_file=ENV_FILE)

APPS = []


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s L%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG' if config.DEBUG else 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'DEBUG' if config.DEBUG else "INFO",
            'propagate': True
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
