import logging
from datetime import datetime

# Logger instance
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(
    handlers=[logging.FileHandler(r'C:/Temp/log', 'w', 'utf-8')],
    format=LOG_FORMAT,
    level=logging.DEBUG)
logger = logging.getLogger()

# Datetime instance of now
now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
