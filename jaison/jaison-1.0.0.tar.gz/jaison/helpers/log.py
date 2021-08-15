import logging
import os


def initialize_log():
    pid = os.getpid()
    logging.basicConfig()
    log = logging.getLogger(f'jaison-{pid}')
    log.setLevel(logging.DEBUG)
    return log


log = initialize_log()
