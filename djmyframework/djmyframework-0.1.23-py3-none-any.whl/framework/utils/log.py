# coding:utf-8
# 日志类
#


import logging
import logging.config
import time

#from settings import LOGGING
from .multiprocesslogging import MultiProcessTimedRotatingFileHandler

#logging.config.dictConfig(LOGGING)


# 使用django 的logging


class Logger(object):
    '''#使用django 的logging
    @name 记录的名字 需在setting里设置
    '''

    def __new__(cls, name='root'):
        logger = logging.getLogger(name)
        return logger


logger = Logger()
log = logger

def TimedRotatingLogger(name):
    log_format = '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_ha = MultiProcessTimedRotatingFileHandler('%s.log' % name, when='h', interval=24, encoding='utf-8')
    file_ha.setLevel(logging.DEBUG)
    file_ha.setFormatter(formatter)
    logger.addHandler(file_ha)
    return logger


if __name__ == '__main__':
    import multiprocessing


    def test(num):
        time.sleep(1)
        log = Logger('cache', 'D', 1, 3)
        # log.info('info')
        # log.critical('critissscal')
        log.warn('wassrn')
        # log.error('errssor')


    pool = multiprocessing.Pool(processes=5)
    for i in range(20):
        pool.apply_async(func=test, args=(i,))
    pool.close()
    pool.join()
    print('完毕')
