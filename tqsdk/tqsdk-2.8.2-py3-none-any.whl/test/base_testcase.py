#!/usr/bin/env python
#  -*- coding: utf-8 -*-


import logging
import os
import unittest

import lz4.frame
from shinny_structlog import JSONFormatter

from tqsdk.channel import TqChan
from tqsdk.connect import TqConnect
from tqsdk.test.helper import MockInsServer, MockWebsocketsServer


def connect__init__(self, logger) -> None:
    self._logger = logger
    self._first_connect = True
    self._keywords = {"max_size": None, "ping_timeout": None}
TqConnect.__init__ = connect__init__


TqChan._level = 10


class TQBaseTestcase(unittest.TestCase):

    def setUp(self, md_url="wss://api.shinnytech.com/t/nfmd/front/mobile"):
        self.ins = MockInsServer()
        os.environ["TQ_INS_URL"] = f"http://127.0.0.1:{self.ins.port}/t/md/symbols/2020-09-15.json"
        os.environ["TQ_AUTH_URL"] = f"http://127.0.0.1:{self.ins.port}"
        os.environ["TQ_CONT_TABLE_URL"] = f"http://127.0.0.1:{self.ins.port}/t/md/symbols/continuous_table.json"
        self.md_mock = MockWebsocketsServer(url=md_url)

        # 清空 logger handler
        logger = logging.getLogger("TqApi")
        while logger.handlers:
            logger.removeHandler(logger.handlers[0])
        log_file_name = f"./log_archive/{self._testMethodName}.log.lz4"
        fp = lz4.frame.open(log_file_name, mode='wt')
        sh = logging.StreamHandler(fp)
        sh.setFormatter(JSONFormatter())
        sh.setLevel(logging.DEBUG)
        logger.addHandler(sh)

    def tearDown(self) -> None:
        self.ins.close()
        self.md_mock.close()
