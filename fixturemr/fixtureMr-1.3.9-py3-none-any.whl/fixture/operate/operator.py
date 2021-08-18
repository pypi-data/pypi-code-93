# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-12-11 16:44:14
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2020-12-11 19:12:41
import serial
from fixture.worker.worker import Worker

class Operator(object):
	def __init__(self):
		pass

	def closeLock(self,num):
		"""
		num 指定关闭哪台治具上的锁
		"""
		if num not in [1,2,3,4]:
			raise Exception("你输入的序号不存在")

		wk = Worker(num)
		if wk.closeLock():
			return True
		else:
			return False




