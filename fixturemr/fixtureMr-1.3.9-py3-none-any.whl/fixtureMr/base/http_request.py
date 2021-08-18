# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2021-01-26 15:16:41
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2021-01-26 16:15:12

import requests
import json
import traceback
import logging


class HttpRequest(object):
	"""
	"""
	headers = {
		"Content-Type":"application/json"
		}

	
	def __init__(self):
		pass

	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, '_instance'):
			with HttpRequest._instance_lock:
				if not hasattr(cls, '_instance'):
					HttpRequest._instance = super().__new__(cls)

		return HttpRequest._instance

	@classmethod
	def post(cls,url,data='',headers='',returnType='json',**kwargs):
		res = {}
		if headers:
			for loop in headers:
				cls.headers[loop] = headers[loop]
			headers = cls.headers
		else:
			headers	= cls.headers

		try:
			# print(headers)
			response = requests.post(url, headers = headers,json=data,timeout=350)
			print('post请求返回码',response.status_code)
			if response.status_code == 200: 
				if returnType == 'json':
					# print(dir(response))
					# print(response.text)
					result = response.json()
				elif returnType == 'text':
					result = response.text
				elif returnType == 'zip':
					result = response.content
				res['status'] = True
				res['code'] = 200
				res['result'] = result
			else:
				print("post请求返回码",response.status_code)
				res['status']=False
				res['code']=response.status_code
				res['message'] = response.text
			return res
		except Exception as e:
			errormsg = traceback.format_exc()
			print (errormsg)
			try:
				if "统一登录中心" in response.text:
					res['message']= 'token过期需更新'
					print ('token过期需更新')
			except:
				logging.error("post请求 %s 出错,出错请求报文为%s,出错内容为:\n%s"%(url,json.dumps(data),errormsg))
				res['status']=False
				res['code']=500
				res['message']="post请求 %s 出错,出错请求报文为%s,出错内容为:\n%s"%(url,json.dumps(data),errormsg)
			return res

	@classmethod
	def get(cls,url,headers='',returnType='json'):
		res = {}
		if headers:
			for loop in headers:
				cls.headers[loop] = headers[loop]
			headers = cls.headers
		else:
			headers	= cls.headers
		try:
			# print(headers)
			response = requests.get(url, headers = headers,timeout=120)

			if response.status_code == 200: 
				if returnType == 'json':
					# print(dir(response))
					# print(response.text)
					result = response.json()
				elif returnType == 'text':
					result = response.text
				elif returnType == 'zip':
					result = response.content
				res['status'] = True
				res['code'] = 200
				res['result'] = result
			else:
				print(response.status_code)
				res['status']=False
				res['code']=502
				res['message'] = response.text
			return res
		except Exception as e:
			errormsg = traceback.format_exc()
			logging.error("get请求 %s 出错,出错内容为:\n%s"%(url,errormsg))
			res['status']=False
			res['code']=500
			res['message']="get请求 %s 出错,出错内容为:\n%s"%(url,errormsg)
			return res


	@classmethod
	def download(cls,url,filePath,headers=''):
		r = requests.get(url, headers = headers)
		with open(filePath, "wb") as code:
			code.write(r.content)
		# print("----------")
		# print(r)
		print(r.status_code)
		# print(dir(r))
		# if r.status_code == 200:
		# 	return True
		# else:
		# 	return False

if __name__ == '__main__':
	print(
		HttpRequest.post('https://admin.ttbike.com.cn:40011/systemUser/getLoginUserInfo',
			headers={"token":"1a037c71929cf8be78928d3c2aa596a9",
			'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",

			}) 
		)



