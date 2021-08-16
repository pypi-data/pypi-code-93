#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/15

import requests
import os

from .setting import setting
from .exception import CommandError
from .custom_logging import Logs
from .common import find_project_root_dir

log = Logs(__name__)


def update_testcases():
    try:
        WEB_PLATFORM_SERVER_HOST = setting.WEB_PLATFORM_SERVER_HOST
        WEB_PLATFORM_TESTCASES_UPLOAD_URL = setting.WEB_PLATFORM_TESTCASES_UPLOAD_URL
    except AttributeError:
        msg = 'WEB_SERVER_HOST or TESTCASES_UPLOAD_URL not set in settings'
        raise CommandError(msg)

    upload_server = WEB_PLATFORM_SERVER_HOST + WEB_PLATFORM_TESTCASES_UPLOAD_URL
    testcases = []
    testcase_record_file = os.path.join(find_project_root_dir(), 'testcases_nodeid_record.txt')
    with open(testcase_record_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            testcase = {}
            testcase['node_id'] = line
            testcases.append(testcase)

    resp = requests.post(url=upload_server, json=testcases)
    log.info(resp.json())
