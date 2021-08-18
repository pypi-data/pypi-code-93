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
from datetime import timedelta, date
from urllib.parse import urljoin
import logging
import math , json , time
import requests
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
        self.name = name
        self.pw = pw
        self._session = self.loginevn()
  
    def loginevn(self):
        headers = {
          'sec-ch-ua': '"Chromium";v="91", " Not A;Brand";v="99", "Google Chrome";v="91"',
          'Accept': 'application/json, text/javascript, */*; q=0.01',
          'Referer': 'https://cskh.evnhcmc.vn/Taikhoan/lienKetDiemDungDien',
          'X-Requested-With': 'XMLHttpRequest',
          'sec-ch-ua-mobile': '?0',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        sessionlogin = requests.Session()
        data = {
          'u': self.name,
          'p': self.pw,
          'remember': '1',
          'token': ''
        }

        response = sessionlogin.post('https://cskh.evnhcmc.vn/Dangnhap/checkLG', headers=headers, data=data, verify=False)
        print(response.status_code)

        return sessionlogin

    def _request_data(self, makh='PE04000011000'):
        #session = requests.Session()
        date = self.kc_date(1)
        data = {
          'token': '',
          'input_makh': makh,
          'input_tungay': date['kc_date'],
          'input_denngay': date['today']
        }
        response = self._session.post('https://cskh.evnhcmc.vn/Tracuu/ajax_dienNangTieuThuTheoNgay',  data=data, verify=False).text
        #print(response)
        time.sleep(1)
        rsp = json.loads(response)
        state = rsp['state']
        datavn = rsp['data']
        alert = rsp['alert']
        sanluong_tungngay = datavn['sanluong_tungngay']
        datajson = {
          'state':state,
          'alert':alert,
          'soNgay':datavn['soNgay'],
          'tieude':datavn['tieude'],
          'ngay': sanluong_tungngay[0]['ngay'],
          'ngayFull': sanluong_tungngay[0]['ngayFull'],
          'sanluong_tong':sanluong_tungngay[0]['sanluong_tong'],
          'tong_p_giao':sanluong_tungngay[0]['tong_p_giao']
        }
        #print(datajson)

        return datajson

    def _request_data_solar(self, makh='PE04000011000'):
        #session = requests.Session()

        date = self.kc_date(1)

        data = {
          'token': '',
          'input_makh': makh,
          'input_tungay': date['kc_date'],
          'input_denngay': date['today']
        }

        response = self._session.post('https://cskh.evnhcmc.vn/Tracuu/ajax_dienNangPhatLenTheoNgay', data=data, verify=False).text
        #print(response)
        time.sleep(1)
        rsp = json.loads(response)
        #print(rsp)
        state = rsp['state']
        alert = rsp['alert']
        datavn1 = rsp['data']
        sanluong_tungngay = datavn1['sanluong_tungngay']
        datajson = {
          'state':state,
          'alert':alert,
          'soNgay':datavn1['soNgay'],
          'tieude':datavn1['tieude'],
          'ngay': sanluong_tungngay[0]['ngay'],
          'ngayFull': sanluong_tungngay[0]['ngayFull'],
          'sanluong_TD':sanluong_tungngay[0]['sanluong_TD'],
          'sanluong_BT':sanluong_tungngay[0]['sanluong_BT'],
          'sanluong_CD':sanluong_tungngay[0]['sanluong_CD'],
          'sanluong_tong':sanluong_tungngay[0]['sanluong_tong'],
          'tong_p_nhan':sanluong_tungngay[0]['tong_p_nhan']
        }
        #print(datajson)

        return datajson

    def kc_date(self, kc=1):
        import datetime 
        today = datetime.date.today()
        today_date = today - datetime.timedelta(days = kc)

        return {"kc_date":today_date.strftime("%d/%m/%Y"),"today":today.strftime("%d/%m/%Y")}

    def get_evn_hcm(self, makhx):
        return self._request_data(makhx)

    def get_evn_hcm_solar(self, makhx):
        return self._request_data_solar(makhx)
########################################

