import logging
import sys, os
import time
import json
import copy
from PIL import Image, ImageDraw, ImageFont

class BasicFormat:
	"""
	Represent the basic format for 
	laying out words and repeating characters. 
	Original Sticker Format. 
	"""
	def __init__(self, sticker_lines=[], **kwargs):
		self.sticker_width = kwargs.get("sticker_width", 380)
		self.sticker_height = kwargs.get("sticker_height", 300)

		self.init_x = kwargs.get("init_x", 8)
		self.init_y = kwargs.get("init_y", 10)

		self.default_font_path = kwargs.get("default_font_path", "@font/msyh.ttf")
		# Get default font from dodayutils
		self.default_font_path = os.path.dirname(os.path.abspath(__file__))+self.default_font_path.replace('@', '/') \
			if '@' in self.default_font_path else self.default_font_path

		self.sticker_lines = copy.deepcopy(sticker_lines)
		logging.info("[BasicFormat] Init sticker lines: "+ str(self.sticker_lines))

		self.edge_space = kwargs.get("edge_space", 10)
		self.small_font = self.get_d2250_font(23)
		self.default_font = self.get_d2250_font(35)
		self.big_font = self.get_d2250_font(40)
		self.left_header = kwargs.get("left_header", "")
		self.right_header = kwargs.get("right_header", "")

		a = self.spread_string(self.left_header, self.right_header, self.default_font)
		# Header
		self.append({"string": self.spread_string(self.left_header, self.right_header, self.default_font), 
			"font": "default_font"})
		self.add_repeat_char("-", "small_font")
		# self.add_repeat_char(" ", "small_font")

	def __len__(self):
		return len(self.sticker_lines)

	def __iter__(self):
		for line in self.sticker_lines:
			yield line

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def __add__(self, other):
		return BasicFormat(sticker_lines=self["sticker_lines"]+other["sticker_lines"])

	def get_d2250_font(self, size):
		return ImageFont.truetype(self.default_font_path, size)

	def add_repeat_char(self, character, font):
		cstr = ""
		while getattr(self,font).getsize(cstr)[0] < self.sticker_width-self.edge_space:
			cstr += character

		self.append({"string": cstr[:-1], "font": "small_font"})

	def append(self, item, delimiter=None, end_header=False):
		"""
		Add lines for sticker
		"""
		assert type(item) == dict 
		# Mandatory keys
		for key in ("string", "font"):
			if key not in item:
				raise DodayUtilError("Sticker Line Format Incorrect")

		try:
			item["font"] = getattr(self, item["font"])
		except:
			raise DodayUtilError("No Such Font")

		item["color"] = (0, 0, 0)
		if self.sticker_lines == []:
			item["pos"] = (self.init_x, self.init_y)
			self.sticker_lines.append(item)
		elif end_header:
			item["pos"] = (8, self.sticker_height - item["font"].getsize(item["string"])[1] - \
				self.v_offset(item["font"]))
			self.sticker_lines.append(item)
		else:
			str_list = self.split_string(item["font"], item["string"], delimiter=delimiter)
			last_line = self.sticker_lines[-1]
			for str_line in str_list:
				current_line = item.copy()
				current_line["string"] = str_line
				vertical_pos = last_line["pos"][1] + last_line["font"].getsize(last_line["string"])[1]\
					- self.v_offset(current_line["font"])
				current_line["pos"] = (8, vertical_pos)
				self.sticker_lines.append(current_line)
				last_line = current_line.copy()

	def spread_string(self, left, right, font, start_width=40):
		"""
		This is the function to spread the string
		out to the left and right. 
		"""
		header_list = [left]
		header_list.extend([" " for _ in range(start_width - len(left) - len(right))])
		header_list.append(right)
		res_str = "".join(header_list)
		if font.getsize(res_str)[0] > self.sticker_width-self.edge_space:
			return self.spread_string(left, right, font, start_width-1)
		return res_str

	def find_all(self, string, delimiter):
		"""
		Helper function to find all the delimiter
		in the string. 
		"""
		start = 0
		while True:
			start = string.find(delimiter, start)
			if start == -1: return
			yield start
			start += len(delimiter) # use start += 1 to find overlapping matches

	def split_string(self, font, string, delimiter=None):
		"""
		This is the function to find the best way to split
		the string into possible ways that fits the sticker
		"""
		if font.getsize(string)[0] < self.sticker_width-self.edge_space:
			# This is base case. If the entire string fits
			return [string]

		if delimiter:
			idx = -1
			reverse_dindex_list = list(self.find_all(string, delimiter))[::-1]
			for dindex in reverse_dindex_list:
				if font.getsize(string[:dindex])[0] < self.sticker_width-self.edge_space:
					# If the string gets in the range of the sticker
					idx = dindex
					break

			return [string[:dindex]] + self.split_string(font, string[dindex:],delimiter=delimiter)

		else:
			idx = -1
			for i in range(len(string), -1, -1):
				if font.getsize(string[:i])[0] < self.sticker_width-self.edge_space:
					# If the string gets in the range of the sticker
					idx = i
					break

			return [string[:idx]] + self.split_string(font, string[idx:])

	def v_offset(self, font):
		if font == self.small_font:
			return 10
		else:
			return -2