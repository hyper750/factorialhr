import logging.config
import os

BASE_PROJECT = os.path.abspath(os.path.dirname(__file__))

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(name)s - %(asctime)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_PROJECT, 'logs', 'factorialclient.log'),
            'interval': 1,
            'when': 'W0',
            'backupCount': 6
        }
    },
    'loggers': {
        'factorial.client': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
