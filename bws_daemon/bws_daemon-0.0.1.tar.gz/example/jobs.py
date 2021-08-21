from app import dm
import logging
import time
import datetime
import os


logger = logging.getLogger(__name__)

@dm.daemon(logfile=f"{os.getcwd()}/example/sleepy.log")
def sleepy(prefix="A", sleep_time=1):
    count = 0

    while True:
        logger.info(f"{prefix} count: {count}")
        time.sleep(sleep_time)
        count += 1


@dm.daemon(logfile=f"{os.getcwd()}/example/whatis.log")
def whatis():
    logger.info(f"is {datetime.datetime.now()} clock")
