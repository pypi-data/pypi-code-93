# @File ：test_log.py
# -*- ecoding: utf-8 -*-
# @Time: 2021/8/12 20:52
# @Author: niu run peng
import pytest

from pytest_log.pytest_log import logger


@pytest.mark.parametrize('log_data', ['日志一', '日志二'])
def test_log(log_data):
    logger.info(log_data)
