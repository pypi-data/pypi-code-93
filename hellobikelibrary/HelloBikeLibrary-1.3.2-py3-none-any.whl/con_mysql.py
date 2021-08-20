# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-08-19 15:31:50
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-08-20 18:10:06

from robot.api import logger
import os
import json
import base64
try:
	import pymysql
except:
	os.popen("pip install pymysql -i https://mirrors.ustc.edu.cn/pypi/web/simple/").read()


class UseMysql(object):
	def __init__(self):
		db = pymysql.connect(host="10.69.12.184",user="maoyongfan",passwd=base64.b64decode('bTEyMzQ1Ng==').decode(),db="helloBikeDB",charset="utf8")
		self.cursor = db.cursor()


	def getTokenInfos(self):
		sql = "select helloBikeToken,user_agent from helloBikeDB.helloBikeUserInfo where id=1" 
		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall()[0]
			# print(results)
			return results[0],results[1]
		except Exception as e:
			raise Exception("获取token信息失败")

if __name__ == '__main__':
	us = UseMysql()
	print(us.getTokenInfos())
