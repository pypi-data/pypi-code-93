import logging
import sys, os
import time
import datetime
import json
import copy
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from DodayUtils._helpers import *
from DodayUtils.order.DodayItem import *
from gadgethiServerUtils.time_basics import *

class OrderInfo:
	"""
	This is the main order info class. I'm thinking
	that it should contain following functions
	OrderInfo.append(DodayItem)

	Variable Definition
	* stayortogo:
	stay
	togo
	delivery

	* comment2
	DDAPos -> local-pay
	DDA01
	online-pay
	pay-on-arrival
	delivery-platform

	* payment_method
	cash
	easycard
	linepay
	jkopay
	credit
	delivery-platform
	counter-cash -> 櫃檯結
	counter-* -> add this prefix
				for pos payment
	"""
	NUMBER_VALUE_ENTRIES = ["deducted_point", "total_discount", \
			"plastic_bag", "special_day_index", "spin_times", \
			"order_time", "priority", "total_price"]

	# Key : Values = OrderInfo Attr : (Json key, defaults)
	#	'-->' means under a dictionary
	SPECIAL_ORDER_INFO_JSON_MAPPING = {
		"otime": ("time", serverTime()),
		"machine_id": ("comment2", ""),
		"status": ("status", "not_paid"),
		"member_update_status": ("comment6", "not_updated"),
		"sync_flag":("sync_flag",False),

		# ---- Below are info that puts in info dict ----
		"special_day_info": {
			"spin_times": ("spin_times", 0),
			"special_day_index": ("special_day_index", -1),
		},

		"customer_info": {
			"payment_method": ("payment_method", ""),
			"stayortogo": ("stayortogo", ""),
			"plastic_bag": ("comment1", 0),
			"return_changes": ("comment5", ""),
			"receipt_number": ("receipt_number", ""),
			"cookie_key": ("comment8", ""),
		},

		"promotion_info": {
			"promotion_key": ("promotion_key", ""),
			"promotion_description": ("promotion_description", ""),
			"one_time_code": ("comment7-->one_time_code", ""),
			"total_discount": ("discount", 0),
		},

		"member_info": {
			"deducted_point": ("comment7-->deducted_point", 0),
			"member_flag": ("member_flag", False),
			"member_phone": ("comment3", "")
		},

		"delivery_info": {
			"pick_up_time": ("comment4-->pick_up_time", ""),
			"phone_number": ("comment4-->phone_number", ""),
			"delivery_location": ("comment4-->delivery_location", "")
		},
	}

	# These are all the direct mapping list that have the same
	# key names and default empty string if not in NUMBER_VALUE_ENTRIES
	# 0 if in NUMBER_VALUE_ENTRIES
	DIRECT_MAPPING_LIST = ["store_id", "order_id", "serial_number", "username", \
		"print_flag", "xml_flag", "order_time", "priority", "total_price"]

	def __init__(self, current_doday_item=[], current_info={}, **kwargs):
		# Assign all external variables before doing the orders operations
		self.info = copy.deepcopy(current_info)
		handle_direct_mapping(self, self.DIRECT_MAPPING_LIST, **kwargs)
		handle_special_mapping(self, self.SPECIAL_ORDER_INFO_JSON_MAPPING, **kwargs)

		# update everything into a big dict
		for d in [self.special_day_info, self.customer_info, self.promotion_info, self.member_info, self.delivery_info]:
			self.info.update(d)

		# The Doday Item object is different from the instance address that is passed in. 
		self.orders = copy.deepcopy(current_doday_item)
		# Split the orders if the imported amount is not 1
		new_orders = []
		for order in self.orders:
			if order.amount == 1:
				new_orders.append(order)
			else:
				tmp_item_list = [copy.deepcopy(order) for _ in range(order.amount)]
				for item in tmp_item_list:
					item.amount = 1
					item.price = order.price // order.amount
					item.final_price = item.price
				new_orders.extend(tmp_item_list)
		self.orders = new_orders
		print("[OrderInfo] Initialized...")
		logging.info("[OrderInfo] Initialized...")

	@dutils
	def __len__(self, **kwargs):
		amount = 0
		for item in self.orders:
			amount += item.amount
		return amount

	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __eq__(self, item, **kwargs):
		if item == None or type(item) != OrderInfo:
			return False
		return self.order_id == item.order_id and self.serial_number == item.serial_number

	@dutils
	def __lt__(self, item, **kwargs):
		return str(self.otime) < str(item.otime)

	@dutils
	def __iter__(self, **kwargs):
		for item in self.orders:
			yield item

	@dutils
	def __getitem__(self, key, **kwargs):
		if key in self.info.keys():
			return self.info[key]

		return getattr(self, key)

	@dutils
	def __setitem__(self, key, value, **kwargs):
		if key in self.info.keys():
			if key in self.NUMBER_VALUE_ENTRIES:
				# These are defined int
				self.info[key] = int(value)
			else:
				self.info[key] = value
		else:
			setattr(self, key, value)

	@classmethod
	@dutils
	def db_format_to_order_info(cls, db_data, **kwargs):
		"""
		db data is the data return by gadgethiServerUtils
		get_data function. it formats like the splitted list
		"""
		# Clone the db data
		db_clone = copy.deepcopy(db_data)

		# Check there exists db data
		if len(db_clone) == 0:
			raise DodayUtilError("No order data from db")

		# Check whether db format is valid
		if not cls.check_valid_db_format(db_clone[0]):
			raise DodayUtilError("Dbdata format not valid")

		sorted_db_data = sorted(db_clone, key=lambda k: k['order_no']) 

		item_list = []
		for i in range(len(sorted_db_data)):
			item_list.append(DodayItem(sorted_db_data[i]["name1"], sorted_db_data[i]["name2"], \
				json.loads(sorted_db_data[i]["name3with4"]), int(sorted_db_data[i]["price"]), comments=sorted_db_data[i]["name5"], \
				order_no=int(sorted_db_data[i]["order_no"]), final_price=int(sorted_db_data[i]["final_price"])))

		# pick the last one for getting the order info
		model_order_data = sorted_db_data[-1]

		# make sure comment4, comment7 are in dictionary format
		model_order_data["comment4"] = json.loads(model_order_data["comment4"])
		model_order_data["comment7"] = json.loads(model_order_data["comment7"])
		model_order_data.update({"current_doday_item": item_list})
		return cls(**model_order_data)


	@classmethod
	@dutils
	def json_format_to_order_info(cls, json_data, **kwargs):
		"""
		Do json load before sending in
		"""
		# Clone the json data
		json_clone = copy.deepcopy(json_data)

		# Check whether json format is valid
		if not cls.check_valid_json_format(json_data):
			raise DodayUtilError("Json data format not valid")

		item_list = []
		for iidx in range(len(json_clone["name1"])):
			# handle comments and order_no. Optional variables
			optionals = {}
			if "name5" in json_clone.keys() and json_clone["name5"] != "None":
				optionals["comments"] = json_clone["name5"][iidx]

			if "order_no" in json_clone.keys() and json_clone["order_no"] != "None":
				optionals["order_no"] = int(json_clone["order_no"][iidx])

			if "final_price" in json_clone.keys() and json_clone["final_price"] != "None":
				optionals["final_price"] = int(json_clone["final_price"][iidx])

			# Main adding area
			item_list.append(DodayItem(json_clone["name1"][iidx], json_clone["name2"][iidx], \
				json_clone["name3with4"][iidx], int(json_clone["price"][iidx]), **optionals))

		json_clone["current_doday_item"] = copy.deepcopy(item_list)
		return cls(**json_clone)

	@classmethod
	@dutils
	def uber_eats_format_to_order_info(uber_order, uber_name_mapping={}, **kwargs):
		"""
		This is the helper function to help parse uber
		eats order format to order info. 
		"""
		# Ubers Deliver knows this id. This is the id that
		# Delivery man needs to know. 
		display_id = uber_order['display_id']

		# List of information
		order_items = uber_order['cart']['items']

		# This converts the yaml to item -> title, category
		uber_item_category_dict = self._parse_uber_naming_section(uber_name_mapping, section="category")
		# This converts the yaml to addon -> addon category, addon title 
		uber_item_addons_dict = self._parse_uber_naming_section(uber_name_mapping, section="addons")

		doday_items_list = []
		soymilk_counter = 0
		
		for item in order_items:
			item_addons = {}
			# Get all the modifier groups of this item
			all_uber_modifier_groups = item.get('selected_modifier_groups',{})
			
			# Modifier group none exception
			if all_uber_modifier_groups != None:
				for mod_group in all_uber_modifier_groups:
					for addon_item in mod_group['selected_items']:
						# Get all the addon item key from uber and get its title
						uber_addon_title = addon_item.get('title', None)
						# print("uber_addon_title",uber_addon_title)
						# Guard the case when selected items are empty
						if uber_addon_title:
							# addon category key for doday item options
							addon_category = uber_item_addons_dict[uber_addon_title]["addons"]
							addon_title = uber_item_addons_dict[uber_addon_title]["title"]
							try:
								item_addons[addon_category].append(addon_title)
							except:
								item_addons[addon_category] = [addon_title]

							# TODO: Currently this is the workaround
							# method to uber menu dynamic mapping. 
							# Need to address this and remove the magic number
							if uber_addon_title == "無糖豆漿":
								soymilk_counter = 1
							# -------------------------------

			# This part handle when the menu on the uber does not match to the store operations
			add_on_list_loop = list(set(list(item_addons.keys())+list(uber_item_category_dict[item['title']]['special_request'].keys())))
			if uber_item_category_dict[item['title']]['special_request'] != {}:
				for key in add_on_list_loop:
					if key in list(uber_item_category_dict[item['title']]['special_request'].keys()):
						try:
							item_addons[key].extend(uber_item_category_dict[item['title']]['special_request'][key])
						except:
							item_addons[key] = uber_item_category_dict[item['title']]['special_request'][key]

			# TODO: Currently this is the workaround
			# method to uber menu dynamic mapping. 
			# Need to address this and remove the magic number
			if soymilk_counter == 1:
				item_addons["甜度"] = ['無糖']
				soymilk_counter = 0
			# ---------------------------------

			doday_items_list.append(DodayItem(
				uber_item_category_dict[item['title']]["category"],
				uber_item_category_dict[item['title']]["title"],
				item_addons,
				(item['price']['unit_price']['amount']//100) * int(item['quantity']), # should multiply quantity
				amount=int(item['quantity']),
				comments=item.get('special_instructions',''),
				))

		# Hardcoded here but should be passed in the future
		# TODO try to eliminate this hardcoding
		uber_specific_order_properties = {
			"order_id": "UBER-"+display_id, # This is temporary before sending to each store
			"stayortogo": "delivery",
			"payment_method": "delivery-platform",
			"promotion_key": "0000-1-1-20200101-21000101-foodpanda",
			"comment2": "delivery-platform", # machine id
			"comment4": { # delivery info
				"pick_up_time": uber_order["estimated_ready_for_pickup_at"],
				"phone_number": uber_order["eater"]["phone"] + "; "+uber_order["eater"]["phone_code"]
			}
		}

		return OrderInfo(doday_items_list, **uber_specific_order_properties)

	@classmethod
	@dutils
	def check_valid_json_format(cls, json_data, **kwargs):
		"""
		Check json format. Focus on the
		length of the orders
		"""
		order_length_flag = all(x == len(json_data["name1"]) for x in (len(json_data["name2"]), \
			len(json_data["name3with4"]), len(json_data["price"])))

		key_exist_flag = set(["store_id", "stayortogo", "payment_method"]).issubset(set(json_data.keys()))

		return key_exist_flag and order_length_flag

	@classmethod
	@dutils
	def check_valid_db_format(cls, db_data, **kwargs):
		"""
		Check db format. Focus on the
		existence of the keys
		"""
		return set(["order_id", "store_id", "stayortogo", "name1", "name2", "name3with4",\
			"price", "payment_method", "order_no"]).issubset(set(db_data.keys()))

	@dutils
	def append(self, dodayitem, **kwargs):
		self.orders.append(dodayitem)

	@dutils
	def merge_same_item(self, **kwargs):
		"""
		This is the helper function to merge
		the same order item with the same 
		item type. 
		"""
		orders_clone = copy.deepcopy(self.orders)
		new_order_list = []
		while orders_clone != []:
			i1 = orders_clone[0]
			# This list holds all the i1 and i2s that are the same
			i1_identical_list = [i1]
			for iid in range(1, len(orders_clone)):
				# Loop through all i2s and catch all identical items
				i2 = orders_clone[iid]
				if i1 == i2:
					i1_identical_list.append(i2)

			new_order_list.append(i1_identical_list)
			# After we caught all identical items, remove all of them from 
			# clone list
			for item in i1_identical_list:
				orders_clone.remove(item)

		# Loop through all identical orders and sum them up
		merged_list = []
		for idlist in new_order_list:
			print(idlist)
			merged_list.append(sum(idlist))

		self.orders = copy.deepcopy(merged_list)
		self.assign_order_no()

	@dutils
	def assign_order_no(self, **kwargs):
		for i in range(1, len(self.orders)+1):
			self.orders[i-1]["order_no"] = i

	@dutils
	def update_special_day(self, special_day_generator, **kwargs):
		if self.get_order_type != "local-pay":
			# All online methods
			for order in self.orders:
				if order["title"] == "special day":
					[new_base, new_topping1, new_topping2, new_topping3] = special_day_generator()
					order["options"]["基底"] = [new_base]
					order["options"]["加料專區"] = [new_topping1, new_topping2, new_topping3]

	@dutils
	def tosplitted(self, **kwargs):
		splitted_list = []
		self.orders.sort()

		for i in range(1, len(self.orders)+1):
			ind_info = self.get_info_json(str_format=True)
			ind_info.update(self.orders[i-1].tojson(str_format=True))
			ind_info["order_no"] = i
			splitted_list.append(ind_info)

		return splitted_list

	@dutils
	def tojson(self, options_to_list=False, **kwargs):
		"""
		This is the function to transform
		order info into json format. do
		json dumps before sending it. 
		"""
		self.orders.sort()

		if len(self.orders) == 0:
			return copy.deepcopy(self.get_info_json())

		# Check if order_no is assigned
		if self.orders[-1]["order_no"] == None:
			self.assign_order_no()

		if options_to_list:
			# Backward compatible change everything to list
			name3with4_list= []
			for item in self.orders:
				item_option = {}
				for option in item.options:
					# Loop through all options
					if type(item.options[option]) == str:
						item_option[option] = [item.options[option]]
					else:
						item_option[option] = item.options[option]
				name3with4_list.append(item_option)
		else:
			name3with4_list = [item.options for item in self.orders]


		json_raw_data = {
			"order_no": [i for i in range(1, len(self.orders)+1)],
			"name1": [item.category for item in self.orders],
			"name2": [item.title for item in self.orders],
			"name3with4": name3with4_list,
			"name5": [item.comments for item in self.orders],
			"price": [item.price for item in self.orders],
			"amount": [item.amount for item in self.orders],
			"final_price": [item.final_price for item in self.orders],
		}

		json_raw_data.update(self.get_info_json())
		return json_raw_data

	@dutils
	def get_pos_info(self, **kwargs):
		"""
		This is the helper function to get
		the pos information
		"""
		pick_up_time_post_str = ": "+self["pick_up_time"] if self["pick_up_time"] != "" else ""
		c_list = ["塑膠袋: 無" if self.get_plastic_bag_str() == "" else self.get_plastic_bag_str()]
		if self["delivery_location"] != "":
			c_list.append("外送地址: "+self["delivery_location"])
		c_list.append("狀態: 未付款" if self["machine_id"] == "pay-on-arrival" else "狀態: 已付款")

		return {
			"stayortogo_label": self.get_stayortogo_str()+pick_up_time_post_str,
			"order_id_label": str(self["serial_number"]),
			"phone_number": self["phone_number"],
			"comment_list": c_list
		}

	@dutils
	def get_plastic_bag_str(self, **kwargs):
		plastic_bag = int(self["plastic_bag"])
		if plastic_bag > 0:
			# Calculate number of bags
			big_bag_count = plastic_bag//2
			small_bag_count = plastic_bag%2
			
			# This generates the plastic bag string
			pstr_list = []
			if big_bag_count > 0:
				pstr_list.append(str(big_bag_count)+"個大袋")
			if small_bag_count > 0:
				pstr_list.append(str(small_bag_count)+"個小袋")
			return "+".join(pstr_list)
		else:
			return ""

	@dutils
	def get_stayortogo_str(self, **kwargs):
		stayortogo = self["stayortogo"]
		if stayortogo == "stay":
			stayortogostr = "內用"
		elif stayortogo == "togo":
			stayortogostr = "外帶"
		elif stayortogo == "delivery":
			stayortogostr = "外送"
		else:
			stayortogostr = " "
		return stayortogostr

	@dutils
	def get_total_price(self, **kwargs):
		tprice = 0
		for item in self.orders:
			tprice += item.price
		return tprice

	@dutils
	def get_info_json(self, str_format=False, **kwargs):
		member_point_info = {"one_time_code": self["one_time_code"], "deducted_point": self["deducted_point"]}
		return {
			"order_id": self.order_id,
			"store_id": self.store_id,
			"serial_number": self.serial_number,
			"stayortogo": self["stayortogo"],
			"time": self["otime"],
			"number_of_data": len(self),
			"total_price": self.get_total_price() + int(self["plastic_bag"]) - self["total_discount"],
			"payment_method": self["payment_method"],
			"receipt_number": self["receipt_number"],
			"promotion_key": self["promotion_key"],
			"discount": self["total_discount"],
			"comment1": self["plastic_bag"],
			"comment2": self.machine_id,
			"comment3": self["member_phone"],
			"comment4": self.delivery_info if not str_format else json.dumps(self.delivery_info, ensure_ascii=False),
			"comment5": self["return_changes"],
			"comment6": self["member_update_status"],
			"comment7": member_point_info if not str_format else json.dumps(member_point_info, ensure_ascii=False), 
			"comment8": self["cookie_key"],
			'username': self["username"], 
			'promotion': self["promotion_description"], 
			'print_flag': self["print_flag"],
			'xml_flag': self["xml_flag"],
			'order_time': self["order_time"], 
			'priority':self["priority"], 
			"status": self["status"],
			"sync_flag": self["sync_flag"]
		}

	@dutils
	def get_order_type(self, **kwargs):
		"""
		Currently there are three types
		1. local-pay: need to reset cashier
		2. online-pay: need to redirect
		3. pay-on-arrival: send to websocket first
		4. delivery-platform: send to websocket first (future API integration)
		"""
		if self["store_id"] in self["machine_id"]:
			return "local-pay"
		else:
			return self["machine_id"]

	@dutils
	def get_serial_header(self, **kwargs):
		"""
		Currently there are five headers
		1: stay, local-pay
		3: togo (or delivery), pay-on-arrival
		5: togo (or delivery), local-pay
		7: togo (or delivery), online-pay
		9: delivery, delivery-platform

		Exception: Since Nanshan DodayPro uses REACT tablet
		for ordering, its machine_id would always be "pay-on-arrival".
		Should distinguish between stay/togo. 
		If store_id = "DDC" -> Return special case

		LEAVE THE EXCEPTION MESSAGE ABOVE ^^
		"""
		if self["stayortogo"] == "stay" and self["machine_id"] == "local-pay":
			return "1"
		elif self["machine_id"] == "pay-on-arrival":
			return "3"
		elif self["stayortogo"] != "stay" and self["machine_id"] == "local-pay":
			return "5"
		elif self["machine_id"] == "online-pay":
			return "7"
		elif self["stayortogo"] == "delivery" and self["machine_id"] == "delivery-platform":
			return "9"
		else:
			raise DodayUtilError("Serial Header Not Exist")

	# Private helper functions that shouldn't be access outside
	# -------------------------------------------------------
	def _parse_uber_naming_section(self, input_dict, section="category"):
		"""
		This is the function to parse uber mapping
		yaml dict to the desired format used by
		the order info parser. 
		- Input:
			raw yaml from uber_mapping
		"""
		return_dict = {}

		for section_key in input_dict[section]:
			for item in input_dict[section][section_key]:
				return_dict[item] = {
					str(section): section_key,
					"title": input_dict[section][section_key][item][0],
					"special_request": input_dict[section][section_key][item][1]
				}

		return return_dict


