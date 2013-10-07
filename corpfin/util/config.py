# -*- coding: utf-8 -*-

import os
import logging
import logging.config


DIRS = dict()
DIRS['base'] = os.getcwd()
DIRS['log'] = os.path.join(DIRS['base'], 'log')
DIRS['out'] = os.path.join(DIRS['base'], 'out')
DIRS['data'] = os.path.join(DIRS['base'], 'data')
DIRS['temp'] = os.path.join(DIRS['base'], 'temp')

ENGINE = 'postgresql://test:test@localhost/testdb'

for key in DIRS.keys():
    if not os.access(DIRS[key], os.F_OK):
        os.makedirs(DIRS[key])

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        },
        'simple':{
            'class': 'logging.Formatter',
            'format': '%(levelname)s %(message)s'
        }
    },
    'filters': {
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/log.txt',
            'mode': 'w+',
            'formatter': 'detailed',
        },
        'errorfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/errors.txt',
            'mode': 'w+',
            'formatter': 'detailed',
        },
    },
    'loggers': {
    },
    'root':{
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'errorfile'],
            'propagate': False,
        }
}

logging.config.dictConfig(LOGGING)
