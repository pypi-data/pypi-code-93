from logging import config, getLogger, DEBUG, INFO

level = INFO

config.dictConfig({
    'version': 1,
    'formatters': {
        'defaltFormatter': {
            'format': '[%(asctime)s] [%(levelname)s] [%(funcName)s] : %(message)s'
        }
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'formatter': 'defaltFormatter',
            'level': level
        }
    },
    'root': {
        'handlers': ['consoleHandler'],
        'level': level
    },
    'loggers': {
        'defalt': {
            'handlers': ['consoleHandler'],
            'level': level,
            'propagate': 0
        }
    }
})

logger = getLogger('defalt')

