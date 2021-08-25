import logging
import os
try:
    import psutil
except ImportError:
    psutil = None
import tempfile


def logger(package, userspace=False):
    logger = logging.getLogger(package)
    logger.setLevel(logging.DEBUG)

    if userspace:
        if psutil:
            current_user = psutil.Process().username().lower()
        else:
            current_user = os.getlogin()
        # Remove Windows domain if needed
        if '\\' in current_user:
            current_user = current_user.split('\\')[1]
        logfile = os.path.join(tempfile.gettempdir(), 'WAPT', current_user, package + '.log')
    else:
        logfile = os.path.join(os.environ['SYSTEMROOT'], 'WAPT', 'logs', package + '.log')

    if not os.path.isdir(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))

    handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
