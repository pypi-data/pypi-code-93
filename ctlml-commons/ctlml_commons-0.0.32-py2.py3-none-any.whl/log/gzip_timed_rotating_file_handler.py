import gzip
import os
from logging.handlers import TimedRotatingFileHandler


class GzipTimedRotatingFileHandler(TimedRotatingFileHandler):
    """ rotating file handler that compresses """

    def __init__(self, **kwargs):
        TimedRotatingFileHandler.__init__(self, **kwargs)

    def rotate(self, source, dest):
        """ Compress rotated log file """

        os.rename(source, dest)

        with open(dest, "rb") as file_in:
            with gzip.open("%s.gz" % dest, "wb") as file_out:
                file_out.writelines(file_in)

        os.remove(dest)
