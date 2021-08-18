import os
import logging
from logging import handlers
import coloredlogs


from os import path

TMP_PATH = os.environ.get('TMP', '/tmp')
LOG_PATH = os.environ.get('LOG_PATH', path.join(TMP_PATH, 'log'))
LOG_FORMAT = '%(name)s %(asctime)s %(message)s'


def create_logger(name, log_path=LOG_PATH, log_to_file=False):

    if log_to_file:
        log_path = log_path or LOG_PATH
        path_exists = os.path.isdir(log_path)

        if not path_exists:
            try:
                os.mkdir(log_path)
            except Exception as ex:
                print(ex)
        else:
            pass

        hostname = os.environ.get('HOSTNAME', 'localhost')
        log_id = 'instance-%s' % hostname

        instance_log_path = path.join(log_path, log_id)

        # label = '%s:instance-%s' % (name, log_id)

        filename = '%s.log' % name.replace(':', '.')
        filepath = path.join(instance_log_path, filename)

        try:
            os.mkdir(instance_log_path)
            print("Initializing logs at %s" % filepath)

        except Exception as ex:
            pass

    logging.basicConfig(format=LOG_FORMAT)

    # logging.basicConfig(format = LOG_FORMAT, level = logging.DEBUG)

    log = logging.getLogger(name)

    if log_to_file:
        log.addHandler(handlers.RotatingFileHandler(filepath,
                       maxBytes=10000000,
                       backupCount=2))

    # else:
        # log.addHandler(logging.StreamHandler())

    coloredlogs.install(logger=log)


    return log
