# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-12-11 16:44:14
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-06-29 14:03:11
import serial
import os
from fixtureMr.worker.worker import Worker

class Operator(object):
	def __init__(self):
		pass

	def closeLock(self,num):
		"""
		num 指定关闭哪台治具上的锁
		"""
		if num not in [1,2,3,4]:
			raise Exception("The serial number you entered does not exist")

		wk = Worker(num)
		if wk.closeLock():
			del wk
			return True
		else:
			del wk
			return False

	def reback(self,num):
		if num not in [1,2,3,4]:
			raise Exception("The serial number you entered does not exist")

		wk = Worker(num)
		wk.reback()
		del wk

	def getPort(self):
		temp = []
		content = os.popen("cd /dev;ls tty.*").read()
		for loop in content.split('\n'):
			if 'usb' in loop:
				temp.append(loop)
		return temp

if __name__ == '__main__':
	a = Operator()
	a.getPort()





