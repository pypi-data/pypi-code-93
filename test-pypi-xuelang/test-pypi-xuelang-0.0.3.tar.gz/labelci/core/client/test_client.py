# encoding: utf-8
# @Time: 2021/8/19 9:26 上午
# @Author: Zuo
# @File: test_client.py
# @Desc:
import pytest
from labelci.core.client.client import DataHubClient


def test_client_requests(url, token):

    hub_client = DataHubClient(url, token)
    hub_client.check_token()


