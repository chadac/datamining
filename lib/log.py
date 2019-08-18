#!/usr/bin/env python3

import os, sys
import logging


APP_NAME = os.environ.get('APP_NAME', 'default')
LOGGER_LEVEL = os.environ.get('LOGGER_LEVEL', logging.INFO) ## default: info
LOGGER_FILE = os.environ.get('LOGGER_FILE', None)


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(name)s] [%(asctime)s] [%(levelname)s] - %(message)s')

if LOGGER_FILE:
    fh = logging.FileHandler(LOGGER_FILE)
    fh.setLevel(int(LOGGER_LEVEL))
    fh.setFormatter(formatter)
    logger.addHandler(fh)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
logger.addHandler(sh)
