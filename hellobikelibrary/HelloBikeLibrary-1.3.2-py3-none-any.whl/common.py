# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-03-10 14:52:05
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-07-01 16:30:36

from robot.api import logger
from HelloBikeLibrary.request import Request
from HelloBikeLibrary.get_thirdInfo import ThirdInfo
import json
import time

__version__ = "1.0"

class Common(object):

	def __sendCodeV3(self,mobilePhone,env="uat"):
		if env == "uat":
			url = "https://uat-api.hellobike.com/api"
		elif env == "pre":
			url = "https://pre-api.hellobike.com/api"
		else:
			url = "https://fat-api.hellobike.com/api"
		data = {
			"mobile" : mobilePhone,
			"source" : 0,
			"riskControlData" : {
			"userAgent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
			"deviceLon" : "121.363833",
			"roam" : "460",
			"systemCode" : "61",
			"deviceLat" : "31.122775"
			},
			"action" : "user.account.sendCodeV3"
		}
		rep = Request().request_client(url=url,data=data)
		print(rep)

	def login_auth_app(self,mobilePhone,env="uat"):
		"""
			app登陆认证
			mobilePhone 登陆手机号
			env 不传默认为uat
			支持pre,uat,fat登录```
			返回token,guid,ticket
		"""
		
		
		if env != "pre":
			self.__sendCodeV3(mobilePhone,env)


		if env == "pre":
			td = ThirdInfo()
			content = td.exe_redis("usercore-cluster",
				"hmset sms:{phone} code 1234".format(phone=mobilePhone),
				env="pre")
			print(content)
			print('gees')

		if env == "uat":
			app_url = "https://uat-api.hellobike.com/auth"
		elif env == "pre":
			app_url = "https://pre-api.hellobike.com/auth"

		else:
			app_url = "https://fat-api.hellobike.com/auth"

		# if env == "pre":
		data = {
			"action" : "user.account.login",
			"mobile" : mobilePhone,
			"adCode" : "310112",
			"city" : "上海市",
			"code" : "1234",
			"longitude" : "121.364887",
			"clientId" : "01J01610284512025880",
			"latitude" : "31.123065",
			"version" : "5.58.0",
			"cityCode" : "021",
			"systemCode" : "61"				
		}

		rep = Request().request_client(url=app_url,data=data)
		print(rep)
		if rep[0] == 200:
			content = rep[1]
			if content.get("code") == 0:
				if content.get('data').get('token'):
					logger.info(content.get('data'))
					return content.get('data').get('token'),content.get('data').get('guid'),content.get('data').get('ticket','')
			else:
				return "网络异常" + str(content)
		else:
			raise Exception("App登陆失败")

		# else:
		# data = {
		# "clientId" : "01L01610000038690879",
		# "version" : "5.34.0",
		# "riskControlData" : {
		# 	"userAgent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
		# 	"deviceLon" : "121.363761",
		# 	"roam" : "460",
		# 	"systemCode" : "61",
		# 	"deviceLat" : "31.122788"
		# },
		# "mobile" : mobilePhone,
		# "longitude" : "121.363800",
		# "latitude" : "31.122782",
		# "cityCode" : "021",
		# "code" : "3050",
		# "action" : "user.account.login",
		# "city" : "上海市",
		# "systemCode" : "61",
		# "adCode" : "310112"
		# }

if __name__ == '__main__':
	com = Common()
	# print(com.login_auth_app("12010002002",env="uat"))
	print(com.login_auth_app("17521766998",env="pre"))
	# print(com.login_auth_app("12010060001",env="uat"))

