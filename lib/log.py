#!/usr/bin/env python3

import os, sys
import logging


APP_NAME = os.environ.get('APP_NAME', 'default')
LOGGER_LEVEL = os.environ.get('LOGGER_LEVEL', logging.INFO) ## default: info
LOGGER_FILE = os.environ.get('LOGGER_FILE', '/app/log/app.log')


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(LOGGER_FILE)
fh.setLevel(int(LOGGER_LEVEL))

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(name)s] [%(asctime)s] [%(levelname)s] - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)
