import os
import logging


BASE_PROJECT = os.path.abspath(os.path.dirname(__file__))

# Formaters
DEFAULT_FORMATER = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')

# Handlers
# File handler
FILE_HANDLER = logging.FileHandler(os.path.join(BASE_PROJECT, 'factorialclient.log'), 'a', 'utf-8')
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(DEFAULT_FORMATER)
# Console handler
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.DEBUG)
CONSOLE_HANDLER.setFormatter(DEFAULT_FORMATER)

# Loggers
LOGGER = logging.getLogger('factorial.client')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(CONSOLE_HANDLER)
