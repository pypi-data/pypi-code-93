import logging
import sys, os
import time
import datetime
import json
import copy
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from os.path import expanduser
from ctypes import *

# This is the dummy for report lab functions
canvas, letter = None, None

"""
Represent a menu item in Doday. The
properties are mutable from client side. 
"""
class DodayItem:
	"""
	* Mutability
	-------------------
	This is designed so that if you do this DodayItem["sweetness"]
	you change the properties of the options. 
	If you want to change the price and title, just use the class
	member method. DodayItem.title = "updated_title"
	
	AF, rep invariant, safety from exposure
	--------------------------------------
	* AF(category, title, options, price, amount, comments, order_no, discount, final_price): 
		A menu item in `category` with `title` and options of adjustment. The item is sold with 
		`price` and if there are multiple bowls, pass in `amount`. For further adjustment, send 
		`comments`. If this item has assigned order number to it, set the order_no. For discounted 
		items, pass in discount number and send in the final price so that it is able to be 
		printed on stickers. 
	
	* Rep invariant:
	"""
	def __init__(self, category, title, options, price, amount=1, comments="", order_no=None, \
		discount=0, final_price=None):
		self.order_no = order_no
		self.category = category
		self.title = title
		self.options = options
		self.comments = comments
		self.amount = amount
		self.price = price
		self.final_price = price if final_price == None else final_price
		self.discount = discount

	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	def __eq__(self, item):
		if item == None or type(item) != DodayItem:
			return False
		return self.category == item.category and self.title == item.title and \
			self.options == item.options and self.comments == item.comments

	def __lt__(self, other):
		"""
		This defines how to sort the items. If
		order_no is defined, use order_no to cmp
		"""
		self_cmp = int(self.order_no) if self.order_no != None else self.title
		other_cmp = int(other.order_no) if other.order_no != None else other.title
		return self_cmp < other_cmp

	def __len__(self, **kwargs):
		return self.amount

	@dutils
	def __getitem__(self, key, **kwargs):
		if key in self.options:
			return self.options[key]
		return getattr(self, key)

	@dutils
	def __setitem__(self, key, value, **kwargs):
		if key in self.options:
			self.options[key] = value
		return setattr(self, key, value)

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
			raise DodayUtilError("Two Doday Items not equal")

		new_amount = self.amount + item.amount

		# Unit price: (self.price//self.amount)
		return DodayItem(self.category, self.title, self.options, (self.price//self.amount)*new_amount, new_amount, self.comments)

	@dutils
	def tojson(self, str_format=False, **kwargs):
		return {
			"name1": self.category,
			"name2": self.title,
			"name3with4": self.options if not str_format else json.dumps(self.options, ensure_ascii=False),
			"name5": self.comments,
			"price": self.price,
			"amount": self.amount,
			"final_price": self.final_price
		}

	@dutils
	def handle_str_list(self, arg, **kwargs):
		"""
		This is the helper function to
		help handle type str and list
		"""
		if type(arg) == str:
			return [arg]
		elif type(arg) == list:
			return arg
		else:
			return arg

	@dutils
	def get_options_str(self, **kwargs):
		"""
		Expect options key
		加料專區
		冷熱冰量
		附加選項
		湯底
		基底 -> only special day
		甜度
		"""
		g_list = []
		str_b = self.handle_str_list(self.options.get("冷熱冰量", []))
		if str_b == ["正常"]:
			str_b = ["冰"]
		g_list.extend(str_b)
		g_list.extend(self.handle_str_list(self.options.get("湯底", [])))
		g_list.extend(self.handle_str_list(self.options.get("加料專區", [])))
		g_list.extend(self.handle_str_list(self.options.get("附加選項", [])))
		g_list.extend(self.handle_str_list(self.options.get("甜度", [])))

		option_str_before_prune = ",".join(g_list)
		option_str = option_str_before_prune.replace("(+15)", "")
		option_str = option_str.replace("(+5)", "")
		option_str = option_str.replace(" ", "")
		return option_str


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
	def __init__(self, current_doday_item=[], current_info={}, **kwargs):
		# Assign all external variables before doing the orders operations
		self.info = copy.deepcopy(current_info)
		self.otime = kwargs.get("time", int(time.time()))
		self.total_price = kwargs.get("total_price", "")
		self.store_id = kwargs.get("store_id", "")
		self.machine_id = kwargs.get("comment2", "")
		self.order_id = kwargs.get("order_id", "")
		self.serial_number = kwargs.get("serial_number", "")
		self.special_day_info = {
			"spin_times": kwargs.get("spin_times", 0), #define int
			"special_day_index": kwargs.get("special_day_index", -1) #define int
		}
		self.customer_info = {
			"payment_method": kwargs.get("payment_method", ""),
			"stayortogo": kwargs.get("stayortogo", ""),
			"plastic_bag": kwargs.get("comment1", 0), #define int
			"return_changes": kwargs.get("comment5", ""),
			"receipt_number": kwargs.get("receipt_number", ""),
			"cookie_key": kwargs.get("comment8", "")
		}
		self.promotion_info = {
			"promotion_key":kwargs.get("promotion_key", ""),
			"promotion_description":kwargs.get("promotion_description", ""),
			"one_time_code": kwargs.get("comment7", {}).get("one_time_code", ""),
			"total_discount": kwargs.get("discount", 0) #define int
		}
		self.member_info = {
			"deducted_point": kwargs.get("comment7", {}).get("deducted_point", 0), #define int
			"member_flag": kwargs.get("member_flag", False), 
			"member_phone": kwargs.get("comment3", "")
		}
		self.delivery_info = {
			"pick_up_time":kwargs.get("comment4", {}).get("pick_up_time", ""),
			"phone_number":kwargs.get("comment4", {}).get("phone_number", ""),
			"delivery_location":kwargs.get("comment4", {}).get("delivery_location", ""),
		}
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
			if key in ["deducted_point", "total_discount", \
			"plastic_bag", "special_day_index", "spin_times"]:
				# These are defined int
				self.info[key] = int(value)
			else:
				self.info[key] = value
		else:
			setattr(self, key, value)

	@classmethod
	@dutils
	def getStoreStr(cls, _store_id, **kwargs):
		store_mapping = {
			"DDA": "豆日子木柵店", 
			"DDB": "豆日子辛亥店", 
			"DDC": "豆日子微風南山店",
			"DDD": "豆日子測試店"
		}
		return store_mapping[_store_id]

	@classmethod
	@dutils
	def getStorePhone(cls, _store_id, **kwargs):
		store_mapping = {
			"DDA": "(02)86617800", 
			"DDB": "(02)29330006", 
			"DDC": "(02)77296890",
			"DDD": "(09)83030465"
		}
		return store_mapping[_store_id]

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
	def toprinterargs(self, **kwargs):
		"""
		This is the function to prepare the
		order info for printer arguments
		"""
		print_order_args = []
		# payment_method
		print_order_args.append(c_char_p(self["payment_method"].encode('big5')))
		# stayortogo
		stayortogo = self.get_stayortogo_str()
		print_order_args.append(c_char_p(stayortogo.encode('big5')))

		# serial number
		print_order_args.append(c_char_p(str(self["serial_number"]).encode('utf-8')))

		# ordertime
		now = datetime.datetime.now()
		print_time_str = now.strftime("%H:%M:%S")
		print_date_str = now.strftime("%Y-%m-%d")
		print_order_args.append(c_char_p(print_date_str.encode('utf-8')))
		print_order_args.append(c_char_p(print_time_str.encode('utf-8')))

		# Total item counts
		total_cnt = len(self.orders)
		
		if self["plastic_bag"] > 0:
			# itemnames
			itemnames = ((c_char * 50) * (total_cnt+1))()
			subitemnames = ((c_char * 50) * (total_cnt+1))()
			itemcounts = c_int * (total_cnt + 1)
			itemprices = c_int * (total_cnt + 1)
			print_order_args.append(c_int(total_cnt+1))
		else:
			itemnames = ((c_char * 50) * total_cnt)()
			subitemnames = ((c_char * 50) * total_cnt)()
			itemcounts = c_int * total_cnt
			itemprices = c_int * total_cnt
			print_order_args.append(c_int(total_cnt))
		
		itemcounts_list = []
		itemprices_list = []
		total_price = 0
		for i in range(total_cnt):
			sub_item_str = self.orders[i].get_options_str()
			subitemnames[i].value = sub_item_str.encode('big5')
			itemnames[i].value = self.orders[i].title[:].encode('big5')
			itemcounts_list.append(self.orders[i].amount)
			item_price = self.orders[i].price
			itemprices_list.append(item_price)
			total_price += item_price

		if self["plastic_bag"] > 0:
			itemnames[total_cnt].value = self.get_plastic_bag_str().encode('big5')
			subitemnames[total_cnt].value = b''
			itemcounts_list.append(1)
			itemprices_list.append(self["plastic_bag"])
			total_price += self["plastic_bag"]
		
		print_order_args.append(itemnames)
		print_order_args.append(subitemnames)
		print_order_args.append(itemcounts(*itemcounts_list))
		print_order_args.append(itemprices(*itemprices_list))

		print_order_args.append(c_int(total_price))
		print_order_args.append(c_int(self["total_discount"]))
		print_order_args.append(c_int(int(total_price) - self["total_discount"]))

		print_order_args.append(c_char_p("結帳單".encode('big5')))
		print_order_args.append(c_char_p("單號".encode('big5')))
		print_order_args.append(c_char_p("日期".encode('big5')))
		print_order_args.append(c_char_p("時間".encode('big5')))
		print_order_args.append(c_char_p("品 項".encode('big5')))
		print_order_args.append(c_char_p("數量".encode('big5')))
		print_order_args.append(c_char_p("小計".encode('big5')))
		print_order_args.append(c_char_p("小 計".encode('big5')))
		print_order_args.append(c_char_p("折 扣".encode('big5')))
		print_order_args.append(c_char_p("總 計".encode('big5')))

		return print_order_args

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
		

	def recursive_change_page_helper(self, cvs, start_height, prod_list, price_list):
		"""
		This is the helper function
		to recursively generate the product page portion
		"""
		changeline_offset = 0
		for p in range(len(prod_list)):
			if start_height-p*20-changeline_offset < 120:
				cvs.line(50, 50, 580, 50)#FROM TOP LAST LINE
				cvs.showPage()
				cvs.setLineWidth(.3)
				cvs.setFont('msyh', 11)
				cvs.line(50, 747, 580, 747) #FROM TOP 1ST LINE
				cvs.line(50, 748, 50, 50)#LEFT LINE
				cvs.line(580, 748, 580, 50)# RIGHT LINE
				self.recursive_change_page_helper(cvs, 720, prod_list[p:], price_list[p:])
				break

			prod_name = prod_list[p]
			cvs.drawString(460, start_height-p*20-changeline_offset, price_list[p])
			if len(prod_name) > 36:
				cvs.drawString(60, start_height-p*20-changeline_offset, prod_name[:36])
				changeline_offset += 12
				cvs.drawString(60, start_height-p*20-changeline_offset, prod_name[36:])
			else:
				cvs.drawString(60, start_height-p*20-changeline_offset, prod_name)

	def invoice_pdf_setting_init(self):
		"""
		This inits invoice pdf reportlab setting
		"""
		global canvas, letter
		from reportlab.pdfgen import canvas
		from reportlab.lib.pagesizes import letter
		from reportlab.pdfbase import pdfmetrics
		from reportlab.pdfbase.cidfonts import UnicodeCIDFont

		from reportlab.pdfbase.ttfonts import TTFont 
		pdfmetrics.registerFont(TTFont('msyh', expanduser("~")+'/.dutils/msyh.ttf'))  

	# generate invoice pdf
	def to_invoice_pdf(self, current_time):
		"""
		This is the function to generate invoice pdf
		"""
		product_list = []
		price_list = []
		price_sum = 0
		for idv_order in self:
			product_str = idv_order["title"] + " - "
			addon_dict = idv_order["options"]
			
			for k in addon_dict.keys():
				product_str+=k
				product_str+=": "
				product_str+=str(addon_dict[k])
				product_str+=", "

			product_str = product_str[:-2]
			product_list.append(product_str)

			price_sum += int(idv_order["price"])
			price_str = str(idv_order["price"])
			price_list.append(price_str)

		# add plastic bag cost
		product_list.append("包裝費")
		price_list.append(self["plastic_bag"])

		discount = int(self["total_price"]) - int(self["plastic_bag"]) - price_sum

		cvs = canvas.Canvas("test.pdf", pagesize=letter)
		cvs.setLineWidth(.3)
		cvs.setFont('msyh', 11)
		cvs.line(50, 747, 580, 747) #FROM TOP 1ST LINE
		cvs.drawString(280, 750, "豆日子豆花甜品店 - 收據")
		cvs.drawString(60, 730, "店名:- "+ OrderInfo.getStoreStr(self["store_id"]))
		cvs.drawString(60, 710, "單號:- "+ self["order_id"])
		cvs.drawString(60, 690, "電話:- "+ self["phone_number"])
		cvs.drawString(420, 730, "時間 :- "+ str(current_time))
		cvs.line(450, 720, 560, 720)

		cvs.line(50, 670, 580, 670)#FROM TOP 2ST LINE
		cvs.line(50, 748, 50, 50)#LEFT LINE
		cvs.line(400, 670, 400, 50)# MIDDLE LINE
		cvs.line(580, 748, 580, 50)# RIGHT LINE
		cvs.drawString(475, 650, '價錢')
		cvs.drawString(100, 650, '品項')
		cvs.line(50, 635, 580, 635)#FROM TOP 3rd LINE

		self.recursive_change_page_helper(cvs, 620, product_list, price_list)

		cvs.line(50, 100, 580, 100)#FROM TOP 4th LINE
		cvs.drawString(60, 80, " 折扣")
		cvs.drawString(500, 80, str(discount))
		cvs.drawString(60, 60, " 總價")
		cvs.drawString(500, 60, self["total_price"])
		cvs.line(50, 50, 580, 50)#FROM TOP LAST LINE
		
		return cvs

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
			"comment6": "not_updated",
			"comment7": member_point_info if not str_format else json.dumps(member_point_info, ensure_ascii=False), 
			"comment8": self["cookie_key"],
			'username': "None", 
			'promotion': "None", 
			'print_flag': "None",
			'xml_flag': "None",
			'order_time': 0, 
			'priority':0, 
			"status": "not_paid"
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
		"""
		# Check if from Nanshan
		if self["store_id"] == "DDC":
			if self["stayortogo"] == "stay":
				return "1"
			else:
				return "5"
		elif self["stayortogo"] == "stay" and self["machine_id"] == "local-pay":
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

class MultiOrderSummary:
	# append order info. 
	pass




