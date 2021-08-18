# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-12-10 21:54:18
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-01-26 19:07:44
import os
import json
import base64
import threading
try:
	import pymysql
except:
	os.popen("pip install pymysql -i https://mirrors.ustc.edu.cn/pypi/web/simple/").read()


class UseMysql(object):
	_instance_lock = threading.Lock()

	def __init__(self):
		self.db = pymysql.connect("10.69.12.184","maoyongfan",base64.b64decode('bTEyMzQ1Ng==').decode(),"helloBikeDB")
		self.cursor = self.db.cursor()

	def __new__(cls, *args, **kwargs):
		# print(dir(cls))
		if not hasattr(cls, '_instance'):
			# print(dir(UseMysql))
			with UseMysql._instance_lock:
				if not hasattr(cls, '_instance'):
					UseMysql._instance = super().__new__(cls)

		return UseMysql._instance

	def getTokenInfos(self):
		sql = "select helloBikeToken,user_agent from helloBikeDB.helloBikeUserInfo where id=1" 
		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall()[0]
			# print(results)
			return results[0],results[1]
		except Exception as e:
			raise Exception("Failed to obtain token information")

	def getFixturePort(self,num):
		sql = "select port FROM helloBikeDB.firture_config where num={}".format(num)

		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall()[0]
			# print(results)
			return results[0]
		except Exception as e:
			raise Exception("Get jig port abnormal")

	def getToEmail(self):
		sql = "select email from helloBikeDB.firture_toEmail"

		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall() #(('maoyongfan10020@hellobike.com',), ('maoyongfan@163.com',))
			return results
		except Exception as e:
			raise Exception("Failed get to email")

	def getCcEmail(self):
		sql = "select email from helloBikeDB.firture_ccEmail"

		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall() #(('maoyongfan10020@hellobike.com',), ('maoyongfan@163.com',))
			return results
		except Exception as e:
			raise Exception("Failed get cc email")

	def __del__(self):
		self.cursor.close()  # 5. 关闭链接
		self.db.close()

if __name__ == '__main__':
	us = UseMysql()
	print(us.getToEmail())