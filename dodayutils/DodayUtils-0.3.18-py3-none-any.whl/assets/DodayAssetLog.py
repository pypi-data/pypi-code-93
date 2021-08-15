from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

import time
import copy
import json

class AssetLog:
	"""
	Description of Properties:
		- time: Epoch time in Int type. The time we generate this log.
		- operator: String type. The code for who execute the operation,
			the structure of operator looks like [store id]-[machine id]
		- event_type: String type. The category of events, supported event_types are listed below:
			1. Error: the event about the system error
				e.g. the data can't be added into db because the server is not working well.
			2. Warning: the event about some error which is blocked by the system
				e.g. someone wants to send an expired asset to another store
			3. Processing: the event which works successfully
		- event_detail: String type. The detail description about the event.
		- comment: String type.
	"""
	def __init__(self, operator, **log_properties):
		self.time = log_properties.get("time", int(time.time()))
		self.operator = operator
		self.asset_id_list = log_properties.get("asset_id_list", [])
		self.event_type = log_properties.get("event_type", "")
		self.event_detail = log_properties.get("event_detail", "")
		self.comment = log_properties.get("comment", "")

		try:
			self.asset_id_list = json.loads(self.asset_id_list)
		except:
			pass
		# check the type of asset_id_list 
		if type(self.asset_id_list) != list:
			raise DodayAssetError("Input asset_id_list should be a list")

	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def tojson(self, str_format=False, **kwargs):
		return {
			"time": self.time,
			"operator": self.operator,
			"asset_id_list": self.asset_id_list if not str_format else json.dumps(self.asset_id_list, ensure_ascii=False),
			"event_type": self.event_type,
			"event_detail": self.event_detail,
			"comment": self.comment
		}


	@classmethod
	@dutils
	def check_valid_json_format(cls, json_data, **kwargs):
		return set(["time", "operator", "asset_id_list", "event_type", \
			"event_detail", "comment"]).issubset(set(json_data.keys()))

	@classmethod
	@dutils
	def json_format_to_asset_log(cls, json_data, **kwargs):
		"""
		Do json load before sending in
		"""
		json_clone = copy.deepcopy(json_data)

		if not cls.check_valid_json_format(json_clone):
			raise DodayAssetError("Json data format not valid")

		if type(json_clone["asset_id_list"]) != list:
			json_clone["asset_id_list"] = json.loads(json_clone["asset_id_list"])

		return cls(**json_clone)


	@dutils
	def tosplitted(self, **kwargs):
		"""
		This is the function to parse class data to db format
		"""
		return [self.tojson(str_format=True)]

	@classmethod
	@dutils
	def check_valid_db_format(cls, db_data, **kwargs):
		return set(["time", "operator", "asset_id_list", "event_type", \
			"event_detail", "comment"]).issubset(set(db_data.keys()))

	@classmethod
	@dutils
	def db_format_to_asset_log(cls, db_data, **kwargs):
		db_clone = copy.deepcopy(db_data)

		if len(db_clone) == 0:
			raise DodayAssetError("No Asset Data from Db")

		# Check whether db format is valid
		if not cls.check_valid_db_format(db_clone[0]):
			raise DodayAssetError("Dbdata format not valid")

		log_list = []
		for i in range(len(db_clone)):
			if type(db_clone[i]["asset_id_list"]) != list:
				db_clone[i]["asset_id_list"] = json.loads(db_clone[i]["asset_id_list"])
			log_list.append(cls(**db_clone[i]))

		return log_list

if __name__ == '__main__':
	a = AssetLog(operator="test_terminal")
	db_data = a.tosplitted()
	print(db_data)
	parse_back = AssetLog.db_format_to_asset_log(db_data)
	print(parse_back)