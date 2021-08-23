from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from DodayUtils.assets.DodayAsset import *

import time
import copy
import json
import urllib


class AssetRequestItem:
	"""
	Description of properties:
		- req_no: Int type. The no of request item in one request
		- request_item_str: String type. The template_id of items which we request for
		- req_item_name: String type. The name of items which we request for
		- request_no: Int type.
		- handler: String type. The code for who handle(send) the request_item. 
			Could be central_kitchen or central_backend
		- send_id_list: list of String type. List of Asset id which is send out for this request.
		- send_time: Epoch time in Int type. The time when the assets are send out
		- get_id_list: list of String type. List of Asset id which is received by the store for this request.
		- get_time: Epoch time in Int type. The time when the assets are received
		- status: String type. Supported status type are listed below:
			1. request: init status. Means that the request has NOT been handled
			2. served: means that the request has been handled, but has NOT been send out yet
			3. send: means that the objects are on the way to store
			4. get: means that the objects are received by store
			5. canceled: the request is canceled by the store before central send out them
		- comment: String type.
	"""
	def __init__(self, **asset_request_item_properties):
		self.req_no = asset_request_item_properties.get("req_no", None)
		self.req_item_str = asset_request_item_properties.get("req_item_str", "")
		self.req_item_name = asset_request_item_properties.get("req_item_name", "")
		self.req_amount = asset_request_item_properties.get("req_amount", 0)
		self.handler = asset_request_item_properties.get("handler", "")
		self.send_id_list = asset_request_item_properties.get("send_id_list", [])
		self.send_time = asset_request_item_properties.get("send_time", None)
		self.get_id_list = asset_request_item_properties.get("get_id_list", [])
		self.get_time = asset_request_item_properties.get("get_time", None)
		self.status = asset_request_item_properties.get("status", "request")
		self.comment = asset_request_item_properties.get("comment", "")

		if type(self.send_id_list) != list:
			try:
				self.send_id_list = json.loads(self.send_id_list)
			except:
				pass

		if type(self.get_id_list) != list:
			try:
				self.get_id_list = json.loads(self.get_id_list)
			except:
				pass

	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	def __eq__(self, item):
		if item == None or type(item) != AssetRequestItem:
			return False
		return self.req_item_str == item.req_item_str and \
			self.status == item.status and self.comment == item.comment

	def __lt__(self, other):
		"""
		This defines how to sort the items. 
		If req_no is defined, use req_no to cmp
		"""
		self_cmp = int(self.req_no) if self.req_no != None else self.req_item_str
		other_cmp = int(other.req_no) if other.req_no != None else other.req_item_str
		
		# The one who has the req_no should be front of the one who hasn't req_no
		if self.req_no == None and other.req_no != None:
			return True
		elif self.req_no != None and other.req_no == None:
			return False
		return self_cmp < other_cmp

	def __len__(self, **kwargs):
		return self.req_amount

	@dutils
	def __getitem__(self, key, **kwargs):
		return getattr(self, key)

	@dutils
	def __setitem__(self, key, value, **kwargs):
		setattr(self, key, value)

	@dutils
	def tojson(self, str_format=False, **kwargs):
		return {
			"req_no": self.req_no,
			"req_item_str": self.req_item_str,
			"req_item_name": self.req_item_name,
			"req_amount": self.req_amount,
			"handler": self.handler,
			"send_id_list": self.send_id_list if not str_format else json.dumps(self.send_id_list, ensure_ascii=False),
			"send_time": self.send_time,
			"get_id_list": self.get_id_list if not str_format else json.dumps(self.get_id_list, ensure_ascii=False),
			"get_time": self.get_time,
			"status": self.status,
			"comment": self.comment
		}



class AssetRequest:
	"""
	Description of properties:
		- receiver: String type. The id of the store which will receive the request.
		- request_item_list: list of AssetRequestItem type.
		- reauest_id: String type. This will be assigned by the central server.
			The structure of request_id looks like [receiver]-[add request date, format:YYYYMMDD]-[number of request in 3 digits]
		- request_time: Epoch time in Int type. When the receiver send the request to server.
			If the user did not input this data, system will set the time when we generate this class to the init_time.
	"""
	def __init__(self, receiver="", request_item_list=[], **kwargs):
		self.receiver = receiver
		self.request_item_list = copy.deepcopy(request_item_list)

		self.request_id = kwargs.get("request_id", "undefined")
		self.request_time = kwargs.get("request_time", int(time.time()))

	@dutils
	def __len__(self, **kwargs):
		return len(self.request_item_list)

	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __eq__(self, item, **kwargs):
		if item == None or type(item) != AssetRequest:
			return False
		return self.request_id == item.request_id and self.receiver == item.receiver

	@dutils
	def __lt__(self, item, **kwargs):
		return str(self.request_time) < str(item.request_time)

	@dutils
	def __iter__(self, **kwargs):
		for item in self.request_item_list:
			yield item

	@dutils
	def __getitem__(self, key, **kwargs):
		return getattr(self, key)

	@dutils
	def __setitem__(self, key, value, **kwargs):
		setattr(self, key, value)

	@dutils
	def get_info_json(self, **kwargs):
		return {
			"receiver": self.receiver,
			"request_id": self.request_id,
			"request_time": self.request_time,
		}

	@dutils
	def tosplitted(self, **kwargs):
		self.request_item_list.sort()
		splitted_list = []
		basic_info = self.get_info_json()

		for i in range(1, len(self.request_item_list)+1):
			item_dict = self.request_item_list[i-1].tojson(str_format=True)
			item_dict["req_no"] = str(i)
			item_dict.update(basic_info)
			splitted_list.append(item_dict)

		return splitted_list

	@classmethod
	@dutils
	def check_valid_db_format(cls, db_data, **kwargs):
		return set(["receiver", "request_id", "request_time", "req_no", \
			"req_item_str", "req_item_name", "req_amount", "handler", "send_id_list", "send_time", \
			"get_id_list", "get_time", "status", "comment"]).issubset(set(db_data.keys()))

	@classmethod
	@dutils
	def db_format_to_asset_request(cls, db_data, **kwargs):
		db_clone = copy.deepcopy(db_data)

		if len(db_data) == 0:
			raise DodayAssetError("No Data from Db")

		if not cls.check_valid_db_format(db_data[0]):
			raise DodayAssetError("Dbdata format not valid")

		sorted_db_data = sorted(db_clone, key=lambda k: int(k['req_no']))
		item_list = []

		for i in range(len(sorted_db_data)):
			item_init_dict = {
				"req_item_str": sorted_db_data[i]["req_item_str"],
				"req_item_name": sorted_db_data[i]["req_item_name"],
				"req_amount": sorted_db_data[i]["req_amount"], 
				"handler": sorted_db_data[i]["handler"],
				"send_id_list": sorted_db_data[i]["send_id_list"], 
				"send_time": sorted_db_data[i]["send_time"],
				"get_id_list": sorted_db_data[i]["get_id_list"], 
				"get_time": sorted_db_data[i]["get_time"],
				"req_no": int(sorted_db_data[i]["req_no"]),
				"status": sorted_db_data[i]["status"],
				"comment": sorted_db_data[i]["comment"],
			}
			item_list.append(AssetRequestItem(**item_init_dict)) 
		
		# pick the last one for getting the request info
		model_request_data = sorted_db_data[-1]
		model_request_data.update({"request_item_list": item_list})

		return cls(**model_request_data)


	@dutils
	def tojson(self, **kwargs):
		self.request_item_list.sort()

		json_raw_data = {
			"req_no": [i for i in range(1, len(self.request_item_list)+1)],
			"req_item_str": [item.req_item_str for item in self.request_item_list],
			"req_item_name": [item.req_item_name for item in self.request_item_list],
			"req_amount": [item.req_amount for item in self.request_item_list],
			"handler": [item.handler for item in self.request_item_list],
			"send_id_list": [item.send_id_list for item in self.request_item_list],
			"send_time": [item.send_time for item in self.request_item_list],
			"get_id_list": [item.get_id_list for item in self.request_item_list],
			"get_time": [item.get_time for item in self.request_item_list],
			"status": [item.status for item in self.request_item_list],
			"comment": [item.comment for item in self.request_item_list],
		}
		
		json_raw_data.update(self.get_info_json())

		return json_raw_data

	@classmethod
	@dutils
	def check_valid_json_format(cls, json_data, **kwargs):
		print ("json_data in check_valid_json_format= ",(json_data))
		try:
			json_data = json.loads(json_data)
			print ("Successful loads")
		except:
			print ("Fail to loads")
			pass
		length_flag = all(x == len(json_data["req_item_str"]) for x in (len(json_data["req_item_name"]), len(json_data["req_amount"]), \
			len(json_data["handler"]), len(json_data["send_id_list"]), len(json_data["send_time"]), len(json_data["get_id_list"]), \
			len(json_data["get_time"]), len(json_data["status"]), len(json_data["comment"])))

		print ("length_flag = ",length_flag)
		keys_exist_flag = set(["receiver", "request_id", "request_time"]).issubset(set(json_data.keys()))
		print ("keys_exist_flag = ",keys_exist_flag)
		return length_flag and keys_exist_flag

	@classmethod
	@dutils
	def json_format_to_asset_request(cls, json_data, **kwargs):
		try:
			json_data = json.loads(json_data)
			print ("Successful loads")
		except:
			print ("Fail to loads")
			pass

		print ("json_data after loads = ",json_data)
		json_clone = copy.deepcopy(json_data)


		if not cls.check_valid_json_format(json_data):
			raise DodayAssetError("Json data format not valid")

		item_list = []
		for index in range(len(json_clone["req_item_str"])):
			item_init_dict = {
				"req_item_str": json_clone["req_item_str"][index],
				"req_item_name": json_clone["req_item_name"][index],
				"req_amount": json_clone["req_amount"][index], 
				"handler": json_clone["handler"][index],
				"send_id_list": json_clone["send_id_list"][index], 
				"send_time": json_clone["send_time"][index],
				"get_id_list": json_clone["get_id_list"][index], 
				"get_time": json_clone["get_time"][index],
				"req_no": json_clone["req_no"][index],
				"status": json_clone["status"][index],
				"comment": json_clone["comment"][index],
			}
			item_list.append(AssetRequestItem(**item_init_dict))
		
		json_clone["request_item_list"] = copy.deepcopy(item_list)
		return cls(**json_clone)

	@dutils
	def assign_req_no(self, **kwargs):
		for i in range(1, len(self.request_item_list)+1):
			self.request_item_list[i-1]["req_no"] = i

	def to_check_list_pdf(self):
		"""
		This function will return the data which will list on the check_list for receiver.
		"""
		pass

	def to_send_qrcode(self):
		"""
		This function will return the data which will be scanned by the received store's POS
		"""
		return_dict = {"request_id": self.request_id}
		asset_dict = {}
		for item in self.request_item_list:
			asset_dict[item.req_no] = item.send_id_list
		return_dict["asset_dict"] = asset_dict

		return urllib.parse.quote(json.dumps(return_dict))

if __name__ == '__main__':
	req_item1 = AssetRequestItem(req_item_str="test_item1", req_amount=1)
	req_item2 = AssetRequestItem(req_item_str="test_item2", req_amount=1)
	req = AssetRequest("DDA", [req_item1, req_item2])
	print(req)
	req_json = req.tojson()
	print(req_json)
	print("for db: ")
	splitted_data = req.tosplitted()
	print(splitted_data)
	print(AssetRequest.db_format_to_asset_request(splitted_data))
	print("========")
	parse_back = AssetRequest.json_format_to_asset_request(req_json)
	print(parse_back)






