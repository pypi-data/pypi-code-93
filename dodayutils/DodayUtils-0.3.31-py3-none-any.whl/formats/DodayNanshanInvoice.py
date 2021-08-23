import copy

from DodayUtils.formats._Barcode import *
from DodayUtils.formats._QRCode import *
from DodayUtils.formats._Basic import BasicFormat
from DodayUtils.formats._Graphic import GraphicFormat
from gadgethiServerUtils.time_basics import *
from PIL import Image, ImageDraw, ImageFont

class DodayNanshanInvoice(GraphicFormat):
	"""
	This represents the doday nanshan invoice
	that is in used for nanshan orders.

	Required by Graphic Format
	---------
	tmpfile_path: file save path
	invoice_height: height of the invoice artboard
	
	Need these info to generate order sticker
	---------
	filename_header: DodayNanshanInvoice-
	invoice_for: kitchen or customer
	logo_path: logo image filepath for the receipt
	"""
	def __init__(self, **configs):
		super().__init__(**configs)
		self.graphic_width = 380 # mm
		self.graphic_height = int(configs.get("invoice_height", 2620)) # mm
		self.pdf_width = 58 # mm
		self.pdf_height = 400 # mm
		self.pdf_scale = 0.41

		# -- order sticker properties
		self.filename_header = "DodayNanshanInvoice-"
		self.invoice_for = configs.get("invoice_for", "")
		self.logo_path = configs.get("logo_path", "/home/pi/Desktop/doday_pro_logo.png")

	def order_info_to_order_invoice(self, order_info):
		img = Image.new('RGB', (self.graphic_width, self.graphic_height), color = (255, 255, 255))
		d = ImageDraw.ImageDraw(img)

		# Copy all properties of orderinfo and merge all same items
		order_info_clone = copy.deepcopy(order_info)
		order_info_clone.merge_same_item()

		# Start doing layout
		# -----------
		# 1. Artboard and Header images
		if self.invoice_for == "kitchen":
			sf = BasicFormat(default_font_path=self.default_font_path)
		else:
			# handle logo
			logo_img = Image.open(self.logo_path, 'r')
			offset = (int((self.graphic_width-logo_img.size[0])/2),0)
				# int(sf.sticker_lines[0]["pos"][1]-logo_img.size[1]/2))
			img.paste(logo_img, offset)
			# end of handle logo
			
			# Generate Sticker
			sf = BasicFormat(default_font_path=self.default_font_path, init_y=logo_img.size[1]+2)
		
		# 2. Headers and serial number
		sf.append({"string": "結帳單     %s"%(order_info_clone.get_stayortogo_str()), "font": "big_font"})
		sf.append({"string": "單號: %s"%(str(order_info_clone.serial_number)), "font": "big_font"})
		
		# 3. Title
		if self.invoice_for == "customer":
			sf.add_repeat_char(" ", "small_font")
			sf.append({"string": sf.spread_string("", "%s   "%("顧客收執聯"), sf.small_font), "font": "small_font"})
		elif self.invoice_for == "kitchen":
			sf.add_repeat_char(" ", "small_font")
			sf.append({"string": sf.spread_string("", "%s   "%("廚房收執聯"), sf.small_font), "font": "small_font"})
		
		# 4. Time
		now = serverTime(TimeMode.DATETIME_NOW)
		print_time_str = now.strftime("%H:%M:%S")
		print_date_str = now.strftime("%Y-%m-%d")
		sf.add_repeat_char(" ", "small_font")
		sf.append({"string": "日期: %s  時間: %s"%(str(print_date_str), str(print_time_str)), "font": "small_font"})
		
		# 5. Column Headers
		sf.add_repeat_char(" ", "small_font")
		sf.append({"string": "      品 項                  數量   小計", "font": "small_font"})
		sf.add_repeat_char("=", "small_font")
		sf.add_repeat_char(" ", "small_font")

		# 6. Column Items
		total_price = 0
		for i in range(len(order_info_clone.orders)):
			total_price += order_info_clone.orders[i].price

			# handle the title string
			# title_list = order_info_clone.orders[i].title.split(" ")
			# sf.append({"string": "%-2d %-20s %d        %d"%(i+1, title_list[0], order_info_clone.orders[i].amount, order_info_clone.orders[i].price), "font": "small_font"})
			self.append_order_item(sf, i+1, order_info_clone.orders[i].title, order_info_clone.orders[i].amount, order_info_clone.orders[i].price)

			# handle the option string
			if order_info_clone.orders[i].get_options_str() != "":
				option_str = sf.split_string(sf.small_font, "    %s"%(order_info_clone.orders[i].get_options_str()))
				sf.append({"string": option_str[0], "font": "small_font"})
				sf.add_repeat_char(" ", "small_font")
				for j in range(1, len(option_str)):
					sf.append({"string": "    %s"%(option_str[j]), "font": "small_font"})
					sf.add_repeat_char(" ", "small_font")
			sf.add_repeat_char(" ", "small_font")

		# 7. Plastic bag
		if int(order_info_clone["plastic_bag"]) > 0:
			total_price += int(order_info_clone["plastic_bag"])
			self.append_order_item(sf, len(order_info_clone.orders)+1, order_info_clone.get_plastic_bag_str(), 1, int(order_info_clone["plastic_bag"]))

		# 8. Separation
		sf.add_repeat_char("=", "small_font")
		sf.add_repeat_char(" ", "small_font")

		# 9. Amount and final price
		sf.append({"string": "小 計 %37d"%(total_price), "font": "small_font"})
		sf.add_repeat_char(" ", "small_font")
		sf.append({"string": "折 扣 %37d"%(order_info_clone["total_discount"]), "font": "small_font"})
		sf.add_repeat_char(" ", "small_font")

		sf.add_repeat_char("=", "small_font")
		sf.add_repeat_char(" ", "small_font")

		sf.append({"string": "總 計 %37d"%(total_price - order_info_clone["total_discount"]), "font": "small_font"})
		
		self.img_draw_string(d, sf)

		# 10. handle barcode printing
		if self.invoice_for == "kitchen":
			# only print the qrcode and barcode on the invoice for kitchen
			# ============== handle order qrcode ============== 
			qrcode_img = generate_qrcode_and_save(order_info_clone.order_id)

			# offset = (int((self.invoice_width-qrcode_img.size[0])/2), 
			# 	sf.sticker_lines[-1]["pos"][1]+sf.sticker_lines[-1]["font"].getsize(sf.sticker_lines[-1]["string"])[1]+10)
			qr_offset = (0, 
				sf.sticker_lines[-1]["pos"][1]+sf.sticker_lines[-1]["font"].getsize(sf.sticker_lines[-1]["string"])[1]+10)
			img.paste(qrcode_img, qr_offset)
			# ============== end of handle order qrcode ============== 

			# ============== handle barcode for nanshan ============== 
			barcode_price_data = code128_format("{:0>8d}".format(total_price - order_info_clone["total_discount"]))
			barcode_price_image = code128_image(barcode_price_data)

			barcode_class_data = code128_format(self.get_nanshan_class_code(order_info_clone))
			barcode_class_image = code128_image(barcode_class_data)

			# resize the image to fit the space area
			max_width = self.graphic_width - qrcode_img.size[0]
			if barcode_price_image.size[0] > max_width:
				new_h = int(qrcode_img.size[1]/2.0)
				barcode_price_image = barcode_price_image.resize((max_width, new_h), Image.ANTIALIAS)
				barcode_class_image = barcode_class_image.resize((max_width, new_h), Image.ANTIALIAS)

			barcode_class_offset = (qrcode_img.size[0], qr_offset[1])
			barcode_price_offset = (qrcode_img.size[0], qr_offset[1]+barcode_class_image.size[1]+15)
			img.paste(barcode_class_image, barcode_class_offset)
			if total_price - order_info_clone["total_discount"] > 0:
				img.paste(barcode_price_image, barcode_price_offset)
			# ============== end of handle barcode for nanshan ============== 

		# Image save to folder
		img_fp = self.tmpfile_path+"/img_%s.png"%(order_info_clone["order_id"])
		self.save_img_to_location(img, img_fp)
		pdf_file_path = self.output_pdf()

		return pdf_file_path, self.filename_header+order_info_clone["order_id"]

	# Helper function
	# -----------------
	def order_title_split(self, order_title):
		"""
		This is the helper function to split the order title to two lines
		The maximum number for the first line is 7 now.
		"""
		output_list = []
		input_title = order_title

		# replace the special char
		input_title = input_title.replace(':', ' ')
		input_title = input_title.replace('+', ' ')

		# use the first space to split the first line
		temp_list = input_title.split(' ')
		# check if the first line is more than 7 chinese words
		count = 0
		index = 0 # where is the end of first line
		for i in temp_list[0]:
			count += 1
			if ord(i) > 127:
				count += 1 # chinese word
			if count <= 14:
				index += 1

		output_list.append(temp_list[0][:index+1])
		left_str = input_title.split(output_list[0])[1]
		if left_str != "":
			# delete the space in the front of the second line
			index = 0
			for i in left_str:
				if i == " ":
					index += 1
				else:
					break
			output_list.append(left_str[index:])

		return output_list

	def append_order_item(self, sticker_format, no, title, amount, price):
		"""
		This is the helper function to put the order item into the sticker_format
		"""
		title_list = self.order_title_split(title)
		sticker_format.append({"string": sticker_format.spread_string("%-2d %s"%(no, title_list[0]), "%-2d      %3d     "%(amount, price), sticker_format.small_font), "font": "small_font"})
		sticker_format.add_repeat_char(" ", "small_font")
		if len(title_list) > 1:
			left_title_list = sticker_format.split_string(sticker_format.small_font, "    %s"%(title_list[1]))
			for j in range(len(left_title_list)):
				if j == 0:
					sticker_format.append({"string": "%s"%(left_title_list[j]), "font": "small_font"})
				else:
					sticker_format.append({"string": "    %s"%(left_title_list[j]), "font": "small_font"})
				sticker_format.add_repeat_char(" ", "small_font")

	def get_nanshan_class_code(self, order_info):
		"""
		Hardcode for nanshan barcode number
		"""
		delivery_way = order_info.info["stayortogo"]
		if delivery_way == "delivery-ubereats":
			return "21766138"
		elif delivery_way == "delivery-foodpanda":
			return "21766145"

		represent_str = order_info.orders[0].title
		if "豆花" in represent_str:
			return "21766077"
		elif "紫米粥" in represent_str:
			return "21766091"
		elif "豆漿" in represent_str:
			return "21766107"
		elif "湯" in represent_str:
			return "21766084"


		return "21766077" # default result