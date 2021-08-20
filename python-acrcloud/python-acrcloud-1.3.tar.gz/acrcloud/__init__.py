#!/usr/bin/python3

from time import time
from hashlib import sha1
from base64 import b64encode
from hmac import new as hmac_new
from requests import post as req_post
from .exceptions import InvalidConfig

bytes_to_read = 1000000

class ACRcloud:
	def __init__(self, config):
		self.__key = config['key']
		self.__secret = config['secret'].encode()
		self.__host = config['host']
		self.__path = "/v1/identify"
		self.__url = f"https://{self.__host}{self.__path}"
		self.__is_valid()

	def __is_valid(self):
		sample = b""
		data = self.__recognize(sample)
		status = data['status']
		code = status['code']

		if code != 2004:
			raise InvalidConfig

	def __recognize(self, sample):
		timestamp = str(
			time()
		)

		method = "POST"
		data_type = "audio"
		signature_version = "1"

		string_to_sign = (
			"%s\n%s\n%s\n%s\n%s\n%s" 
			% (
				method,
				self.__path, 
				self.__key, 
				data_type, 
				signature_version, 
				timestamp
			)
		).encode()

		c_hmac = hmac_new(
			self.__secret, 
			string_to_sign,
			digestmod = sha1
		).digest()

		sign = b64encode(c_hmac)

		data = {
			"access_key": self.__key,
			"sample_bytes": bytes_to_read,
			"sample": sample,
			"timestamp": timestamp,
			"signature": sign,
			"data_type": data_type,
			"signature_version": signature_version
		}

		result = req_post(self.__url, data)
		result.encoding = "utf-8"
		json = result.json()
		return json

	def recognize_audio(self, audio):
		f = open(audio, "rb")
		f_bytes = f.read(bytes_to_read)
		sample = b64encode(f_bytes)
		f.close()
		data = self.__recognize(sample)
		return data