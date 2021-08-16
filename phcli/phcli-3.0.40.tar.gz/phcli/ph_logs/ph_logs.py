# -*- coding: utf-8 -*-
"""alfredyang@pharbers.com.

This module document the usage of class pharbers command context,
"""
import io
import sys
import atexit
import logging
from phcli.define_value import *
from phcli.ph_aws.ph_s3 import PhS3

LOG_DEBUG_LEVEL = logging.DEBUG
LOG_INFO_LEVEL = logging.INFO
LOG_WARN_LEVEL = logging.WARNING
LOG_ERROR_LEVEL = logging.ERROR
LOG_DEFAULT_LEVEL = LOG_INFO_LEVEL

LOG_PATH = '{}/logs/python/phcli/{}'

PH_CLI_ACCESS_KEY = 'AKIAWPBDTVEAMVOYSOVE'
PH_CLI_SECRET_KEY = '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'


class PhLogs(object):
    """The Pharbers Logs
    """

    def __init__(self, *args, **kwargs):
        self._log_path = ''
        self.logger = logging.getLogger("ph-log")
        formatter = logging.Formatter("{ 'Time': %(asctime)s, 'Message': %(message)s, 'File': %(filename)s, 'Func': "
                                      "%(funcName)s, 'Line': %(lineno)s, 'Level': %(levelname)s } ")

        sys_handler = logging.StreamHandler(stream=sys.stdout)
        sys_handler.setFormatter(formatter)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.addHandler(sys_handler)

        if 'job_id' in kwargs.keys() and kwargs['job_id']:
            self._log_path = LOG_PATH.format(CLI_VERSION, kwargs['job_id'] + '.log')

        def write_s3_logs(body, bucket, key):
            phs3 = PhS3(access_key=PH_CLI_ACCESS_KEY, secret_key=PH_CLI_SECRET_KEY)
            phs3.s3_client.put_object(Body=body.getvalue(), Bucket=bucket, Key=key)

        if self._log_path and 'storage' in kwargs.keys() and kwargs['storage'] == 's3':
            log_stream = io.StringIO()
            io_handler = logging.StreamHandler(log_stream)
            io_handler.setFormatter(formatter)
            self.logger.addHandler(io_handler)
            atexit.register(write_s3_logs, body=log_stream, bucket=CLI_BUCKET, key=self._log_path)


inst_map = {}


def phs3logger(job_id=None, level=LOG_DEFAULT_LEVEL):
    if job_id and job_id in inst_map.keys():
        return inst_map[job_id]

    logger = PhLogs(job_id=job_id, storage='s3').logger
    logger.setLevel(level)
    inst_map[job_id] = logger

    return logger


phlogger = phs3logger()


if __name__ == '__main__':
    phlogger.debug('debug')
    phlogger.info('info')
    phlogger.warning('warning')
    phlogger.error('error')
    phlogger.critical('critical')

    nulllog = phs3logger('')
    nulllog.debug('debug')
    nulllog.info('info')
    nulllog.warning('warning')
    nulllog.error('error')
    nulllog.critical('critical')

    joblog = phs3logger('job')
    joblog.debug('debug')
    joblog.info('info')
    joblog.warning('warning')
    joblog.error('error')
    joblog.critical('critical')

