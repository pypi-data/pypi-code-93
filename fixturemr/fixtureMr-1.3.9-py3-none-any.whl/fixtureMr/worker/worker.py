# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-12-11 17:08:05
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-08-18 15:53:48
import serial
import time
# from fixtureMr.base.con_mysql import UseMysql

class Worker(object):
	def __init__(self,port):
		# useMysql = UseMysql()
		# port = useMysql.getFixturePort(num)
		port = '/dev/' + port
		self.open_com = None 
		try:
			self.open_com = serial.Serial(port,115200)
		except:
			raise Exception("Connection failed, please confirm whether the port number is correct or whether the USB is connecting")
		self.get_data_flag = True


	def closeLock(self):
		"""
		num 指定关闭哪台治具上的锁
		"""
		
		#关锁前先确认锁的状态
		if self.isOpenStatus():
			
			# if self.closeLockIsSuccess():
				# print("关锁成功")

				# if self.isCloseStatus():
			# self.closeLockIsSuccess()
			self.open_com.write("AT+SETUP_ROTATION_ANGLE:90\r\n".encode())
			time.sleep(1)
			self.open_com.write("AT+SETUP_ROTATION_ANGLE:-90\r\n".encode())
			time.sleep(1)


			if not self.isOpenStatus():
				# self.get_data(checkString="success")
				# print("关锁成功,并复位")
				return {"lockStatus": "close","status": True,"msg": "关锁成功"}

			else:
				return {"lockStatus": "open","status": False, "msg": "关锁后锁仍是打开的状态"}
		else:	
			self.open_com.write("AT+SETUP_ROTATION_ANGLE:-90\r\n".encode())
			time.sleep(1)
			self.open_com.close()
			return {"lockStatus": "close","status": False, "msg": "关锁时锁是关着的"}



	def reback(self):
		self.open_com.write("AT+SETUP_ROTATION_ANGLE:-90\r\n".encode())
		time.sleep(1)
		return {"status": True, "msg": "复位成功"}
		# self.get_data()


	def isOpenStatus(self):
		self.open_com.write("AT+GET_LOCK_STATE\r\n".encode())
		time.sleep(1)

		content = self.get_data()
		print(content)

		if "1" in content:
			return True
		else:
			return False

	def isCloseStatus(self):
		self.open_com.write("AT+GET_LOCK_STATE\r\n".encode())
		time.sleep(1)


		content = self.get_data()

		if "0" in content:
			return True
		else:
			return False

	def closeLockIsSuccess(self):
		"""
		要等success,不然会影响后面的执行
		"""
		self.open_com.write("AT+SETUP_ROTATION_ANGLE:90\r\n".encode())
		time.sleep(1)

		content = self.get_data(checkString="success")
		print(content)

		if "success" in content:
			return True
		else:
			return False

	def get_data(self,over_time=20,checkString=""):
		start_time = time.time()
		data = ""

		while True:
			end_time = time.time()
			# print("时间间隔为:",end_time - start_time)
			if (end_time - start_time) < over_time:
				waitNum = self.open_com.inWaiting()
				if waitNum>0:
					data += str(self.open_com.read(waitNum))

					if data:
						# print("接收的内容为:",data)

						if not checkString:
							return data
						else:
							if checkString in data:
								return data

			else:
				break

		if not checkString:
			print("超时,无消息")
		else:
			print("超时,没有等到期望数据")
		return data

	def __del__(self):
		if self.open_com:
			self.open_com.close()

if __name__ == '__main__':
	w = Worker('tty.usbmodem8D72139C53531')
	print(w.closeLock())

