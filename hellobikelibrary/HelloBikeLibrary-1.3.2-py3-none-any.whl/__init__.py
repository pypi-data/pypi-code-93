# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-03-08 13:24:25
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2020-12-02 21:48:06

from HelloBikeLibrary.request import Request
from HelloBikeLibrary.version import VERSION
from HelloBikeLibrary.common import Common
from HelloBikeLibrary.con_mysql import UseMysql
from HelloBikeLibrary.get_thirdInfo import ThirdInfo
from HelloBikeLibrary.basic_fun import BasicFun

__version__ = VERSION

class HelloBikeLibrary(Request,Common,UseMysql,ThirdInfo,BasicFun):
	"""
		HelloBikeLibrary 1.0
	"""
	ROBOT_LIBRARY_SCOPE = "GLOBAL"

if __name__ == '__main__':
	pass