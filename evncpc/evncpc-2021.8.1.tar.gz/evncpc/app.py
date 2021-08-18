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

MIN_PYTHON_VERSION = (3, 5, 3)

_ = version_info >= MIN_PYTHON_VERSION or exit(
    "Python %d.%d.%d required" % MIN_PYTHON_VERSION
)

__version__ = "1.0.1"

_LOGGER = logging.getLogger(__name__)

# Date format for url
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

TIMEOUT = timedelta(seconds=30)


'''
#nguyen ban
bac1 = 1678 # 0 - 50
bac2 = 1734 # 51 - 100
bac3 = 2014 # 101 - 200
bac4 = 2536 # 201 - 300
bac5 = 2834 # 301 - 400
bac6 = 2927 # 401 tro len
'''
#giam gia covid19
bac1 = 1510 # 0 - 50
bac2 = 1561 # 51 - 100
bac3 = 1813 # 101 - 200
bac4 = 2282 # 201 - 300
bac5 = 2834 # 301 - 400
bac6 = 2927 # 401 tro len


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
            jsondata = self._home()
            #log out
            submit('ctl00$ctrlHeader1$btnDangxuat')
            return jsondata

        if xxx.find('Mật khẩu truy cập không chính xác') >0:
            print("001 : Mật khẩu truy cập không chính xác")
            return {"message": "Login Error ! Sử dụng tài khoản có thể login tại https://cskh.cpc.vn/ "}


        if xxx.find('Tên truy cập không chính xác') >0:
            print("002 : Tên truy cập không chính xác")
            return {"message": "Login Error ! Sử dụng tài khoản có thể login tại https://cskh.cpc.vn/ "}

    def _home(self):

        go("https://cskh.cpc.vn/Default.aspx")
        code(200)
        xxx = show()

        data = self._get_home_detail(xxx)
        #save login
        if data['sanluong']=='Công tơ không hỗ trợ':
            del data['chiso']
            del data['socongto']
            del data['thoidiem']

            return data
        else:

            jsondata = self.hass_chisohientai(data)
            return jsondata

    def _get_home_detail(self, string):

        #Mã khách hàng: 
        ten = string.split('<span id="ContentPlace_lblMaKH">')
        makh = ten[1][:ten[1].find('</span>')]

        #ten khách hàng: 
        ten = string.split('<span id="ContentPlace_lbTenKHang"><b>')
        ten_kh = ten[1][:ten[1].find('</b></span>')]

        #tinhtrang
        if string.find('Chưa thanh toán')>1:
            ten = string.split('Chưa thanh toán')
            tienthangtruoc = ten[1][:ten[1].find('</span>')].replace('</font>','')
            tienthangtruoc = 'Chưa thanh toán' + tienthangtruoc
            
        else:
            tienthangtruoc = "Đã thanh toán"

        #check khong ho tro cong to dien tu

        if string.find('<p>- Sản lượng : <span style="color: #3498db">') > -1:

            #sanluong
            ten = string.split('<p>- Sản lượng : <span style="color: #3498db">')
            sanluong = ten[1][:ten[1].find('</span>')]

            #chiso
            ten = string.split('Chỉ số (kWh) : <span style="color: #3498db">')
            chiso = ten[1][:ten[1].find('</span>')].strip()
            #socongto
            ten = string.split('Số công tơ : <span style="color: #3498db">')
            sosongto = ten[1][:ten[1].find('</span>')]
            #thoidiem
            ten = string.split('<p>- Ngày giờ : <span style="color: #3498db">')
            thoidiem = ten[1][:ten[1].find('</span>')]

        else:
            sanluong = 'Công tơ không hỗ trợ'
            chiso = 'Công tơ không hỗ trợ'
            sosongto ='Công tơ không hỗ trợ'
            thoidiem ='Công tơ không hỗ trợ'

        json_data = {
                "ten_kh":ten_kh,
                "makh":makh,
                "tienthangtruoc":tienthangtruoc,
                "sanluong":sanluong,
                "chiso":chiso,
                "socongto":sosongto,
                "thoidiem":thoidiem,
                "copyright": 'trumxuquang@gmail.com'
        }

        return json_data

    def hass_chisohientai(self, jsondata):

        sanluong = jsondata['sanluong']
        makh = jsondata['makh']
        tienthangtruoc = jsondata['tienthangtruoc']
        chiso = jsondata['chiso']
        socongto = jsondata['socongto']
        thoidiem = jsondata['thoidiem']

        intx = sanluong.find(".")
        sanLuong1 = 0
        if intx == -1:
            sanLuong1 = sanluong
        else:
            sanLuong1 = sanluong[: intx]
        
        sanLuong1 = sanLuong1.strip()

        tienhientai = self.tinhtien(float(sanLuong1))

        json_data = {
            "ten_kh":jsondata['ten_kh'],
            "ma_khachhang":makh,
            "sanLuong_thangnay":sanLuong1,
            "tien_thangnay":tienhientai,
            "chiso_congto":chiso.replace(" ",""),
            "thoidiemdo":thoidiem,
            "tienthangtruoc":tienthangtruoc,
            "socongto":socongto,
            "chiso_date":thoidiem[:10],
            "chiso_time":thoidiem[-8:],
            "copyright":'trumxuquang@gmail.com'
        }

        return json_data


    def _50k(self, xyz):
        result = xyz*bac1
        return result

    def _100k(self, xyz):
        result = self._50k(50) + (xyz -50) * bac2
        return result

    def _200k(self, xyz):
        result = self._100k(100) + (xyz -100) * bac3
        return result

    def _300k(self, xyz):
        result = self._200k(200) + (xyz -200) * bac4
        return result

    def _400k(self, xyz):
        result = self._300k(300) + (xyz -300) * bac5
        return result

    def _500k(self, xyz):
        result = self._400k(400) + (xyz -400) * bac6
        return result

    def _thue10(self, x):
        return x * 10 /100

    def tinhtien(self, x):
        b1 = 0 < x < 51
        b2 = 50 < x < 101
        b3 = 100 < x < 201
        b4 = 200 < x < 301
        b5 = 300 < x < 401
        b6 = 400 < x < 3009

        if b1:
            tiengoc = self._50k(x)
            tienthue = self._thue10(tiengoc)
            sumd = tiengoc + tienthue
            return round(sumd)
        if b2:
            tiengoc = self._100k(x)
            tienthue = self._thue10(tiengoc)
            sumd = tiengoc + tienthue
            return round(sumd)
        if b3:
            tiengoc = self._200k(x)
            tienthue = self._thue10(tiengoc)
            sumd = tiengoc + tienthue
            return round(sumd)
        if b4:
            tiengoc = self._300k(x)
            tienthue = self._thue10(tiengoc)
            sumd = tiengoc + tienthue
            return round(sumd)
        if b5:
            tiengoc = self._400k(x)
            tienthue = self._thue10(tiengoc)
            sumd = tiengoc + tienthue
            return round(sumd)
        if b6:
            tiengoc = self._500k(x)
            tienthue = self._thue10(tiengoc)
            sumd = tiengoc + tienthue
            return round(sumd)


    def get_evn_cpc(self):
        return self._login()
########################################

