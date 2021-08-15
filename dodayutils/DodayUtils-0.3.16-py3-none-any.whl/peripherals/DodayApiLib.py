import logging
import sys, os
import time
import json
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

import glob
import re
import subprocess
from ctypes import *

class DodayApiLib:
	"""
	This is the Doday Api lib that connects
	C code and perform printing, qr scan, etc.
	"""
	@dutils 
	def __init__(self, doday_api_lib="", **configs):
		"""
		Input:
			* doday_api_lib: path to the dynamic library. 
		"""
		self.terminate_qr_process = False

		# Get default lib from api lib files
		doday_api_lib_load = os.path.dirname(os.path.abspath(__file__))+doday_api_lib.replace('@', '/') \
			if '@' in doday_api_lib else doday_api_lib

		self.doday_lib = cdll.LoadLibrary(doday_api_lib_load)
		self.doday_lib.minc_init_api()

	@dutils
	def order_print(self, order_info, **kwargs):
		"""
		This is the function to print the order
		"""
		self.doday_lib.minc_print_order(*DodayRawInvoice.order_info_to_printer_args(order_info))

	@dutils
	def get_qr_scan_data_com(self, tout, **kwargs):
		"""
		This is the main function that the checkin front end should
		call. It turns on the camera and scan the qr code and extract
		the data for checkin functionality.  
		"""
		self.terminate_qr_process = False

		tout_start_time = time.time()
		while True:
			qrcode_str = create_string_buffer(b'\000' * 32)
			self.doday_lib.minc_read_qrcode(c_int(5), qrcode_str)
			data = qrcode_str.value.decode('utf-8')
			
			if self.terminate_qr_process:
				logging.info("manual terminate qr loop")
				data = "Terminated"

			# payment timeout -> set to timeout
			if time.time() - tout_start_time >= tout:
				break

			if len(data)>0:
				break

		return data

	@dutils
	def simple_get_qr_scan(self, tout, **kwargs):
		"""
		This is the simple scan without any
		repeat check. 
		"""
		qrcode_str = create_string_buffer(b'\000' * 32)
		self.doday_lib.minc_read_qrcode(c_int(5), qrcode_str)
		return qrcode_str.value.decode('utf-8')
