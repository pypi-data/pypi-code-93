import websocket
import logging
import _thread
import sys, os
import time
import json
import urllib.parse
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from websocket_server import WebsocketServer
from gadgethiServerUtils.file_basics import *

class DodayWebsocketServer:
	"""
	This is the websocket server for 
	doday business.
	"""
	@dutils 
	def __init__(self, api_context, **configs):
		self.server_instance = WebsocketServer(configs["websocket_port"], host=configs["websocket_ip"])
		self.server_instance.set_fn_new_client(self.client_join_msg)
		self.server_instance.set_fn_client_left(self.client_leave_msg)
		self.server_instance.set_fn_message_received(self.receive_msg_handler)
		self.passargs = configs
		self.api_context = api_context
		self.msg_handler = lambda self, m: {"indicator": False, "message": "No msg handler assigned"}

	def assign_msg_handler(self, func):
		self.msg_handler = func

	# Called for every client connecting
	def client_join_msg(self, client, server):
		logging.info("[WebsocketServer] New client connected and was given id %d" % client['id'])

	# Called for every client disconnecting
	def client_leave_msg(self, client, server):
		logging.info("[WebsocketServer] Client(%d) disconnected" % client['id'])

	# Called when a client sends a message
	@dutils
	def receive_msg_handler(self, client, server, message, **kwargs):
		msg = urllib.parse.unquote(message)
		logging.info("[WebsocketServer] Message Handle: " + msg)
		response = self.msg_handler(msg, self.api_context, **self.passargs)
		logging.info("[WebsocketServer] Message Handle Response: " + response["message"])

		# Currently it is self or all scheme. If in the future, we will
		# need to send to specific client, we would need more information. 
		if response["indicator"]:
			server.send_message_to_all(urllib.parse.quote(response["message"]))
		else:
			server.send_message(client, urllib.parse.quote(response["message"]))

	def run(self):
		self.server_instance.run_forever()


class DodayWebsocketClient(object):
	"""
	This is the websocket client for 
	doday business.
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
		while True:
			try:
				message = self.ws.recv()
				msg = urllib.parse.unquote(message)
				logging.info(msg)
				json_msg = json.loads(msg)
				self.msg_handler(json_msg, **self.msg_parameters)
			except Exception as e:
				_, _, exc_tb = sys.exc_info()
				fobj = traceback.extract_tb(exc_tb)[-1]
				fname = fobj.filename
				line_no = fobj.lineno

				ddyerror = DodayUtilError.buildfromexc(str(e), fname, line_no, ''.join(traceback.format_tb(exc_tb)))
				logging.error("[WebsocketClient Inner Thread Error] DodayUtilError: "+str(ddyerror))

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


class DodayWebsocket:
	"""
	This is for all the doday related
	websocket functions
	"""
	@dutils 
	def __init__(self, websocket_mode="client", **configs):
		# mode can be 'server' or 'client'
		if websocket_mode == 'client':
			self.client = DodayWebsocketClient(**configs)
		elif websocket_mode == 'server':
			self.websocket_api_path = configs["websocket_api_path"]
			self.websocket_api_dict = read_config_yaml(self.websocket_api_path)
			self.server = DodayWebsocketServer(self.websocket_api_dict["services"], **configs)
		else:
			raise DodayUtilError("Unsupported mode for doday websocket")

