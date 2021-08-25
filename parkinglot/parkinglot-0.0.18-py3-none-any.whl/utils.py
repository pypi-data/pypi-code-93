import logging
import os
from datetime import datetime

# 'AppData' path for saving a log.txt
env = os.getenv('APPDATA') + '\\parkinglot_log.txt'

# Logger instance
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(
    handlers=[logging.FileHandler(env, 'w', 'utf-8')],
    format=LOG_FORMAT,
    level=logging.DEBUG)
logger = logging.getLogger()

# Datetime instance of now
now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
