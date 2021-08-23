from DodayUtils.formats._Basic import BasicFormat
from DodayUtils.formats._Graphic import GraphicFormat
from PIL import Image, ImageDraw, ImageFont

class DodayInventorySticker(GraphicFormat):
	"""
	This represents the doday inventory sticker
	that is in used for inventory. 
	tmpfile_path: required by graphic format
	
	Need these info to generate inventory sticker
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
		self.filename_header = "InventorySticker-"

	def inventory_item_to_sticker(self, inv_item):
		# This is for printing food sticker. With expirary date
		for i in range(inv_item.subitems_count):
			img = Image.new('RGB', (self.graphic_width, self.graphic_height), color = (255, 255, 255))
			d = ImageDraw.ImageDraw(img)

			sf = BasicFormat(default_font_path=self.default_font_path, 
				left_header="庫存%s"%inv_item.invid, right_header="%02d/%02d"%(i, inv_item.subitems_count))
			sf.append({"string": inv_item.name, "font": "big_font"})
			sf.add_repeat_char(" ", "small_font")
			sf.append({"string": "製造日期 : {}".format(inv_item.made_date), "font": "default_font"})
			sf.append({"string": "有效期限 : {}".format(inv_item.expirary_date), "font": "default_font"})
			sf.append({"string": sf.spread_string(inv_item.upstream_name, inv_item.upstream_phone, sf.small_font),
				"font": "small_font"}, end_header=True)

			# Generate images and save to pdf
			self.generate_img(sf, filename="img_%s_%d.png"%(inv_item.invid, i))
			pdf_file_path = self.output_pdf()

		return pdf_file_path, self.filename_header+inv_item.invid
