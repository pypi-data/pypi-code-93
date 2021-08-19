import logging
import sys, os
import time
import datetime
import json
import copy
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

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