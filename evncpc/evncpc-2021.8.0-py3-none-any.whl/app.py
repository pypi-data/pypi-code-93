#!/usr/bin/env python
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

from sys import version_info
from datetime import timedelta
import logging
import requests
from twill.commands import *
import urllib3
urllib3.disable_warnings()

MIN_PYTHON_VERSION = (3, 5, 3)

_ = version_info >= MIN_PYTHON_VERSION or exit(
    "Python %d.%d.%d required" % MIN_PYTHON_VERSION
)

__version__ = "1.0.1"

_LOGGER = logging.getLogger(__name__)

# Date format for url
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

TIMEOUT = timedelta(seconds=30)


class API:
    """ API class for EVN Online API  """

    INTERVAL_6MIN = "6min"
    INTERVAL_DAY = "day"

    def __init__(self, name=None, pw=None):
        self._session = requests.Session()
        self._name = name
        self._pw = pw


    def _login(self):
        go("https://cskh.cpc.vn/Default.aspx")
        code(200)
        formvalue(1,'ctl00$ctrlHeader1$ctrlSignin1$txtMA_KHANG',self._name)
        formvalue(1,'ctl00$ctrlHeader1$ctrlSignin1$txtPassword',self._pw)
        submit('ctl00$ctrlHeader1$ctrlSignin1$btnSignIn')
        xxx = show()
        if xxx.find('Chào mừng khách hàng') >0:
            print("000 : Chào mừng khách hàng")
            jsondata = {'stat7s' :'ok'}
            #log out
            submit('ctl00$ctrlHeader1$btnDangxuat')
            return jsondata

        if xxx.find('Mật khẩu truy cập không chính xác') >0:
            print("001 : Mật khẩu truy cập không chính xác")
            return {"message": "Login Error ! Sử dụng tài khoản có thể login tại https://cskh.cpc.vn/ "}


        if xxx.find('Tên truy cập không chính xác') >0:
            print("002 : Tên truy cập không chính xác")
            return {"message": "Login Error ! Sử dụng tài khoản có thể login tại https://cskh.cpc.vn/ "}

    def get_evn_cpc(self):
        return self._login()
########################################

