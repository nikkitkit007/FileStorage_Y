
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '%(levelname)s : [%(asctime)s] %(funcName)s: %(message)s'
        }
    },

    'handlers': {
        'infoFileHandler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': 'logger.log',
            'formatter': 'default_formatter'
        },
        'errorFileHandler': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'filename': 'logger.log',
            'formatter': 'default_formatter'
            # 'moda': 'a'
        },
    },

    'loggers': {
        'info_logger': {
            'handlers': ['infoFileHandler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'error_logger': {
            'handlers': ['errorFileHandler'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
info_logger = logging.getLogger('info_logger')
# logger_info.debug('debug log')
#
error_logger = logging.getLogger('error_logger')
# logger_error.error('here error!')
