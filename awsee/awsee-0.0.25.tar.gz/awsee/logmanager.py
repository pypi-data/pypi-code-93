import os
import logging
import sys
from os.path import expanduser

class LogManager:

    @property
    def LOG(self):
        return self._LOG

    def __init__(self):
        self._LOG = logging.getLogger("app." + __name__)
        self._LOG.setLevel(logging.INFO)
        FILE_LOG = os.path.join(expanduser("~"), ".awsee","log")

        if not os.path.exists(FILE_LOG):
           os.makedirs(FILE_LOG)

        rootLogger = logging.getLogger()
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

        fileHandler = logging.FileHandler("{0}/{1}.log".format(FILE_LOG, "awsee"))
        fileHandler.setFormatter(logFormatter)
        fileHandler.setLevel(logging.INFO)
        rootLogger.addHandler(fileHandler)