import websocket
import logging
import _thread
import sys, os
import time
import json
import urllib.parse
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

class DodayWebsocketClient(object):
	"""
	This is the websocket client for 
	doday business.

	- Input:
		need websocket_ip, websocket_port
	"""
	@dutils
	def __init__(self, **configs):
		self.ws = websocket.create_connection("ws://" + configs["websocket_ip"] + ":" +str(configs["websocket_port"]))
		self.msg_handler = lambda self, m: {"indicator": False, "message": "No msg handler assigned"}

	def assign_msg_handler(self, func, **kwargs):
		self.msg_handler = func
		self.msg_parameters = kwargs

	# The websocket communication function
	# ====================================================================================
	def receiving(self, **kwargs):
		"""
		The function which will receive the websocket message continuously
		"""
		fail_count = 0
		fail_consecutive_threshold = 5

		while True:
			try:
				message = self.ws.recv()
				msg = urllib.parse.unquote(message)
				logging.info(msg)
				json_msg = json.loads(msg)
				self.msg_handler(json_msg, **self.msg_parameters)
				# Reset fail count every time it succeeds
				fail_count = 0
			except Exception as e:
				_, _, exc_tb = sys.exc_info()
				fobj = traceback.extract_tb(exc_tb)[-1]
				fname = fobj.filename
				line_no = fobj.lineno

				ddyerror = DodayUtilError.buildfromexc(str(e), fname, line_no, ''.join(traceback.format_tb(exc_tb)))
				logging.error("[WebsocketClient Inner Thread Error] DodayUtilError: "+str(ddyerror))
				
				# Sleep and check whether exceeds threshold
				time.sleep(0.1)
				fail_count += 1
				if fail_count > fail_consecutive_threshold:
					logging.error("[WebsocketClient Thread Error] === Retry Limit Reached ===")
					break

		_thread.exit_thread()

	@dutils
	def send_to_websocket(self, input_dict, **kwargs):
		"""
		The function to send message to websocket OnMessage.
		This function will prepare the basic information of the service from authentication.txt file.
		Input:
			- input_dict: the data which want to send, MUST contain the action type and data etc.
				ex. {"action":"modify_queue", "data":"test"}
		"""
		send_text = json.dumps(input_dict, ensure_ascii=False)
		self.ws.send(urllib.parse.quote(send_text))