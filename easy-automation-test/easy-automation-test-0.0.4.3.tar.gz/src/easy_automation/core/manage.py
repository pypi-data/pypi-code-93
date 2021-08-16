#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21
import argparse

from easy_automation.utils.upload_testcases import update_testcases
from easy_automation.utils.upload_test_result import update_result


def manage():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        type=str,
                        choices=('uploadTestCases', 'uploadTestReport'))
    parser.add_argument('-u', '--build_url',
                        type=str,
                        help="Jenkins build url")
    args = parser.parse_args()
    if args.operation == 'uploadTestCases':
        return update_testcases()
    else:
        build_url = args.build_url
        return update_result(build_url)


if __name__ == '__main__':
    manage()
