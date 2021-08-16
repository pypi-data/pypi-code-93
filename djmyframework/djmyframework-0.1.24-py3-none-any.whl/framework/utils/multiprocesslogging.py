# -*- coding: utf-8 -*-
# 多进程日志按时间分割
# 加入文件锁,解决分割文件,日志丢失问题


import fcntl
from logging.handlers import TimedRotatingFileHandler
import multiprocessing
import os
import struct
import time
import logging


class MultiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kw):
        super(MultiProcessTimedRotatingFileHandler, self).__init__(*args, **kw)

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.

        Override,   1. if dfn not exist then do rename
                    2. _open with "a" model
        """

        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)

        try:
            fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
                logging.info('%s rename %s to %s' %
                             (os.getpid(), self.baseFilename, dfn))
                os.rename(self.baseFilename, dfn)
        except (IOError, OSError):
            logging.warn('%s rename %s to %s IOError,OSError' %
                         (os.getpid(), self.baseFilename, dfn))
        except Exception:
            logging.error('%s rename %s to %s error' %
                         (os.getpid(), self.baseFilename, dfn))
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                if os.path.isfile(s):
                    logging.info('%s remove %s ' % (os.getpid(), s))
                    try:
                        os.remove(s)
                    except:
                        logging.warn('%s remove %s error' % (os.getpid(), s))
        if self.stream:
            self.stream.close()
            self.stream = None
        if not hasattr(self, 'delay') or not self.delay:
            self.mode = "a"
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


if __name__ == '__main__':
    import multiprocessing
    import os

    logger = logging.getLogger('test')
    fileTimeHandler = MultiProcessTimedRotatingFileHandler('test.log', 'S', 1, 300)
    formatter = logging.Formatter(
            '%(asctime)spid:%(process)d %(name)s:%(lineno)d %(levelname)s %(message)s', datefmt='[%Y-%m-%d %H:%M:%S]')
    fileTimeHandler.setFormatter(formatter)
    logger.addHandler(fileTimeHandler)


    def test(num):
        time.sleep(1)
        logger.warn('warn')


    pool = multiprocessing.Pool(processes=5)
    for i in range(20):
        pool.apply_async(func=test, args=(i,))
    pool.close()
    pool.join()
    os.system('wc -l test.log*')
    print('第一次运行,日志数量大于等于20')
