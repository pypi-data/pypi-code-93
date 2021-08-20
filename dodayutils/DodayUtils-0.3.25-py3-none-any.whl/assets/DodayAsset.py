from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

import time
import copy
import json
import urllib


class AssetItem:
	"""
	Description of Properties:
		- asset_id: String type. the id of an asset. This will be assigned by the central inventory server.
			The structure of asset id looks like [template id]-[add asset date, format:YYYYMMDD]-[serial no]-[asset no]
			e.g. im-ck-001-20210310-1-1
		- template_id: String type. id of the template of this asset. We get this data from inventory.yaml .
			The structure of template id looks like [code for template type]-[code for handler]-[number of template in 3 digits]
			e.g. im-ck-001
		- category: String type. which kind of category the asset is. We get this data from inventory.yaml .
		- name: String type. Could be written in Chinese. The name of the asset. We get this data from inventory.yaml .
		- amount: Int type. This amount could be more than 1 only when the asset_id is undefined. 
			As the asset_id is defined, the amount must be 1.
		- unit: String type. We get this data from inventory.yaml .
		- status: String type. The supported status are listed below
			1. po
			2. ship
			3. storage
			4. onboard
			5. finished	(End Status) -> means that we send this asset to other holder, we won't keep tracking it
			6. retired	(End Status) -> means that this asset is not working or is empty
			*. dropped (End Status) -> means that this asset is end with non-regular way, the description must be written in comment.
		- holder: String type. Where the asset is. This should be the id of the store or central kitchen.
		- price: Int type. The singal price of the asset. We should get this from inventory.yaml. 
			However, if noone defined teh singal price of this asset, the price could be None.
		- storage_life: Epoch time in Int type. We get this data from inventory.yaml .
		- expiry_time: Epoch time in Int type. This sould be assigned by user.
		- init_type: String type. How we get the asset. Now there are 2 ways to get an asset: purchase, production.
			This will be defined by the child class.
		- init_time: Epoch time in Int type. When we get this asset. 
			If the user did not input this data, system will set the time when we generate this class to the init_time.
		- comment: String type. If this asset is dropped, the reason will be written in comment.
	"""
	def __init__(self, **asset_properties):
		self.asset_id = asset_properties.get("asset_id", "undefined")
		self.template_id = asset_properties.get("template_id", "")
		self.category = asset_properties.get("category", "")
		self.name = asset_properties.get("name", "")
		self.amount = asset_properties.get("amount", 0)
		self.unit = asset_properties.get("unit", "Unit")
		self.status = asset_properties.get("status", "")
		self.holder = asset_properties.get("holder", "") # where the asset is
		self.price = asset_properties.get("price", None)
		self.storage_life = asset_properties.get("storage_life", None)
		self.expiry_time = asset_properties.get("expiry_time", None)
		self.init_type = asset_properties.get("init_type", "")
		self.init_time = asset_properties.get("init_time", int(time.time()))
		self.comment = asset_properties.get("comment", "")

		try:
			# check the input types which should be int
			self.amount = int(self.amount)
			self.price = int(self.price) if self.price!=None else self.price
			self.storage_life = int(self.storage_life) if self.storage_life!=None else self.storage_life
			self.expiry_time = int(self.expiry_time) if self.expiry_time!=None else self.expiry_time
			self.init_time = int(self.init_time)
		except:
			raise DodayAssetError("Invalid Input type. The type of amount, price, storage_life, expiry_time, and init_time should be int.")

		


	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	def __eq__(self, item):
		"""
		check the attributes without holder, amount, asset_id
		"""
		if item == None or type(item) != AssetItem:
			return False

		return self.template_id == item.template_id and self.category == item.category and \
			self.name == item.name and self.unit == item.unit and self.price == item.price and \
			self.storage_life == item.storage_life and self.expiry_time == item.expiry_time and \
			self.init_type == item.init_type and self.init_time == item.init_time and \
			self.status == item.status and self.comment == item.comment


	def __lt__(self, other):
		"""
		This defines how to sort the items. If
		asset_id is defined, use template_id to cmp
		"""
		self_cmp = self.asset_id if self.asset_id != "undefined" else self.template_id
		other_cmp = other.asset_id if other.asset_id != "undefined" else other.template_id
		return self_cmp < other_cmp

	@dutils
	def __radd__(self, other, **kwargs):
		# for sum function implementation
		if other == 0:
			return self
		else:
			return self.__add__(other)

	@dutils
	def __add__(self, item, **kwargs):
		if self != item:
			raise DodayAssetError("Two Doday Assets not equal")

		if self.asset_id != "undefined" or item.asset_id != "undefined":
			# only two assets w/o id can be added
			raise DodayAssetError("One of Assets has been defined an id")

		new_amount = self.amount + item.amount
		new_asset_info = self.tojson()
		new_asset_info["amount"] = new_amount

		return AssetItem(new_asset_info)
		

	@dutils
	def tojson(self, **kwargs):
		return {
			"asset_id": self.asset_id,
			"template_id": self.template_id,
			"category": self.category,
			"name": self.name,
			"amount": self.amount,
			"unit": self.unit,
			"status": self.status,
			"holder": self.holder,
			"price": self.price,
			"storage_life": self.storage_life,
			"expiry_time": self.expiry_time,
			"init_type": self.init_type,
			"init_time": self.init_time,
			"comment": self.comment
		}


	@classmethod
	@dutils
	def check_valid_json_format(cls, json_data, **kwargs):
		"""
		Input data must be dictionary, do json.loads before sending in
		"""
		return set(["category", "name", "amount", "unit"]).issubset(set(json_data.keys()))

	@classmethod
	@dutils
	def json_format_to_asset(cls, json_data, **kwargs):
		"""
		Input data must be dictionary, do json.loads before sending in
		"""
		json_clone = copy.deepcopy(json_data)

		print ("json_clone = ",json_clone)

		if not cls.check_valid_json_format(json_clone):
			raise DodayAssetError("Json data format not valid")

		return cls(**json_clone)

	@dutils
	def toqrcode(self, **kwargs):
		"""
		This will generat a qrcode string for printing on sticker.
		We only want to store the asset_id in qr_code.
		"""
		return urllib.parse.quote(self.asset_id)

	@dutils
	def tosplitted(self, **kwargs):
		"""
		This is the function to parse class data to db format
		"""
		splitted_list = []
		for i in range(self.amount):
			asset_info = self.tojson()
			# parse python None type to str type
			asset_info["price"] = -1 if asset_info["price"]==None else asset_info["price"]
			asset_info["storage_life"] = -1 if asset_info["storage_life"]==None else asset_info["storage_life"]
			asset_info["expiry_time"] = -1 if asset_info["expiry_time"]==None else asset_info["expiry_time"]
			# add index in the end of asset_id
			# check the format of asset_id, a completed asset_id should have 5 "-"
			if self.asset_id.count("-") == 4:
				asset_info["asset_id"] = self.asset_id + "-" + str(i+1)
			else:
				asset_info["asset_id"] = self.asset_id
			splitted_list.append(asset_info)

		return splitted_list

	@classmethod
	@dutils
	def check_valid_db_format(cls, db_data, **kwargs):
		"""
		Input data type must be dictionary.(get the data from database)
		"""
		return set(["asset_id", "template_id", "category", "name", "amount", "unit"]).issubset(set(db_data.keys()))

	@classmethod
	@dutils
	def db_format_to_asset(cls, db_data, **kwargs):
		"""
		Input data type could be list or dicttionary.(get the data from database)

		No matter how many data we get, the output will be ALWAYS a list
		"""
		db_clone = copy.deepcopy(db_data)
		if type(db_clone) != list:
			# parse data format to list
			db_clone = [db_clone]

		if len(db_clone) == 0:
			raise DodayAssetError("No Asset Data from Db")


		# Check whether db format is valid
		if not cls.check_valid_db_format(db_clone[0]):
			raise DodayAssetError("Dbdata format not valid")

		asset_list = []
		for i in range(len(db_clone)):
			asset_list.append(cls(**db_clone[i]))

		return asset_list

	@dutils
	def check_operation_avail(self, operation="onboard", **kwargs):
		"""
		This function will return if the operation is available

		The optional input argument will be put in kwargs

		Optional input:
			- check_operator_flag: should system check the holder. 
				default value is True, means that the system will check the validation about asset's holder
		"""

		def check_holder(check_arg):
			"""
			This helper function will check if the validation about self.holder and operation
			If the optional input "check_operator_flag" == False, we won't check and the answer will always be True.
			"""
			check_operator_flag = kwargs.get("check_operator_flag", True)
			if check_arg == "operator":
				return self.holder in kwargs["operator"] or not check_operator_flag
			elif check_arg == "sender":
				return self.holder == kwargs["sender"] or not check_operator_flag
			else:
				return not check_operator_flag


		result = {"indicator": False, "message": ("Undefined operation: "+operation)}

		if self.expiry_time == None or self.expiry_time == -1:
			result["message"] = "This asset has no expiry time."
			return result

		# check expiry_time
		if int(time.time()) >= self.expiry_time:
			result["message"] = "This asset is expired!!!"
			# only drop or retired could execute for an expired asset
			if not(operation == "drop" or operation == "retired"):
				return result


		if operation == "onboard":
			if not check_holder("operator"):
				result["message"] = "Invalid Operator, the asset's holder is " + self.holder + " now!"
			else:
				result = {"indicator": True, "message": "This asset is ok for onboard."}


		elif operation == "transform":
			"""
			check the status==storage and holder==sender
			"""
			if self.status != "storage" or not check_holder("sender"):
				result["message"] = "Invalid Asset for Transform, status: " + \
				self.status + ", holder: " + self.holder
			else:
				result = {"indicator": True, "message": "This asset is ok for transform."}		
					
		elif operation == "receive":
			"""
			check the status==ship
			"""
			if self.status != "ship":
				result["message"] = "Invalid Asset for Receive, status: " + self.status
			else:
				result = {"indicator": True, "message": "This asset is ok for receive."}			

		elif operation == "drop":
			if self.status=="dropped" or self.status=="finished" or self.status=="retired":
				result["message"] = "Invalid Asset for Drop, status: " + self.status
			else:
				if not check_holder("operator"):
					result["message"] = "Invalid Operator, the asset's holder is " + self.holder + " now!"
				else:
					result = {"indicator": True, "message": "This asset is ok for drop."}		

		elif operation == "retire":
			if self.status!="onboard":
				result["message"] = "Invalid Asset for Drop, status: " + self.status
			else:
				if not check_holder("operator"):
					result["message"] = "Invalid Operator, the asset's holder is " + self.holder + " now!"
				else:
					result = {"indicator": True, "message": "This asset is ok for retired."}

		
		return result


	def to_sticker_info(self):
		"""
		This function will return the necessary info for sticker printing
		"""
		# TODO 
		return {
			
		}



class EquipmentItem(AssetItem):
	def __init__(self, **equip_properties):
		equip_properties.update({"init_type": "purchase"})
		super().__init__(**equip_properties)
		self.life_cycle = ["po", "ship", "storage", "onboard", "retired"]


class InventoryHardwareItem(AssetItem):
	def __init__(self, **inv_hard_properties):
		inv_hard_properties.update({"init_type": "purchase"})
		super().__init__(**inv_hard_properties)
		self.life_cycle = ["po", "ship", "storage", "finished"]


class InventoryMaterialItem(AssetItem):
	def __init__(self, **inv_material_properties):
		inv_material_properties.update({"init_type": "purchase"})
		super().__init__(**inv_material_properties)
		self.life_cycle = ["po", "ship", "storage", "onboard", "finished"]


class InventoryFoodItem(AssetItem):
	def __init__(self, **inv_food_properties):
		inv_food_properties.update({"init_type": "production"})
		super().__init__(**inv_food_properties)
		if self.storage_life != None and self.expiry_time == None:
			self.expiry_time = self.storage_life * 86400 + self.init_time
		self.life_cycle = ["storage", "ship", "finished"]


def select_class_from_assetid(asset_id):
	class_code = asset_id[:asset_id.find("-")]

	if class_code == "e":
		return EquipmentItem
	elif class_code == "ih":
		return InventoryHardwareItem
	elif class_code == "im":
		return InventoryMaterialItem
	elif class_code == "if":
		return InventoryFoodItem
	else:
		return AssetItem

def generate_class_from_asset_data(asset_data, data_format="json"):
	"""
	default input is json format
	"""
	if data_format=="json":
		_cls = select_class_from_assetid(asset_data["asset_id"])
		return _cls.json_format_to_asset(asset_data)
	elif data_format=="db":
		_cls = select_class_from_assetid(asset_data["asset_id"])
		return _cls.db_format_to_asset(asset_data)

