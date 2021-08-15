from DodayUtils.formats._Basic import BasicFormat
from DodayUtils.formats._Graphic import GraphicFormat
from PIL import Image, ImageDraw, ImageFont

class DodayOrderSticker(GraphicFormat):
	"""
	This represents the doday order sticker
	that is in used for orders. 
	tmpfile_path: required by graphic format
	
	Need these info to generate order sticker
	----
	filename_header: DodaySticker-
	store_str_bottom: True/False
	store_phone_bottom: True/False
	"""
	def __init__(self, **configs):
		super().__init__(**configs)
		self.graphic_width = 380 # mm
		self.graphic_height = 300 # mm
		self.pdf_width = 38 # mm
		self.pdf_height = 30 # mm
		self.pdf_scale = 0.27

		# -- order sticker properties
		self.filename_header = "DodaySticker-"
		self.store_str_bottom = configs.get("store_name_str", " ")
		self.store_phone_bottom = configs.get("store_phone_str", " ")
		
	def order_info_to_order_sticker(self, order_info):
		# print order sticker. order info class.
		for i in range(len(order_info)):
			img = Image.new('RGB', (self.graphic_width, self.graphic_height), color = (255, 255, 255))
			d = ImageDraw.ImageDraw(img)
			
			# Generate Sticker
			sf = BasicFormat(default_font_path=self.default_font_path, 
				left_header="編號%s"%str(order_info["serial_number"]), right_header="%02d/%02d"%(i+1, len(order_info)))
			
			# Handle special day
			if "special day" in order_info.orders[i].title:
				title_str = order_info.orders[i].title + "@ "+str(order_info.orders[i]["基底"]).replace("[", "").replace("]", "")
			else:
				title_str = order_info.orders[i].title
			sf.append({"string": "{} - ${}".format(title_str,str(order_info.orders[i]["final_price"])), "font": "big_font"})
			sf.add_repeat_char(" ", "small_font")

			sf.append({"string": "選配: "+order_info.orders[i].get_options_str(), "font": "default_font"}, delimiter=',')
			# Handle bottom header string
			left_bottom = self.store_str_bottom
			right_bottom = self.store_phone_bottom

			sf.append({"string": sf.spread_string(left_bottom, right_bottom, sf.small_font),"font": "small_font"}, end_header=True)

			# Generate images and save to pdf
			self.generate_img(sf, filename="img_%s_%d.png"%(order_info["order_id"], i))
			pdf_file_path = self.output_pdf()

		return pdf_file_path, self.filename_header+order_info["order_id"]
