import os

from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

from gadgethiServerUtils.time_basics import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.rl_config import TTFSearchPath

# Import Chinese font
# --------------
# directory = os.path.dirname(__file__)
# font_directory = os.path.join(directory, 'font')
# TTFSearchPath.append(font_directory)
pdfmetrics.registerFont(TTFont('msyh', 'utils/msyh.ttf'))

class OnlineInvoice:
	"""
	Represent the online invoice 
	for doday online order. This can
	be expanded to online unified receipt
	in the future. 

	TODO: definitely make it compatible with 
	Online Invoice. 
	"""
	def __init__(self, **configs):
		self.store_name_str = configs.get("store_name_str", " ")

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
		
	@dutils
	def order_info_to_invoice_pdf(self, order_info, **kwargs):
		"""
		This is the function to generate invoice pdf
		"""
		product_list = []
		price_list = []
		price_sum = 0
		for idv_order in order_info:
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
		price_list.append(order_info["plastic_bag"])

		discount = int(order_info["total_price"]) - int(order_info["plastic_bag"]) - price_sum

		cvs = canvas.Canvas("test.pdf", pagesize=letter)
		cvs.setLineWidth(.3)
		cvs.setFont('msyh', 11)
		cvs.line(50, 747, 580, 747) #FROM TOP 1ST LINE
		cvs.drawString(280, 750, "豆日子豆花甜品店 - 收據")
		cvs.drawString(60, 730, "店名:- "+ self.store_name_str)
		cvs.drawString(60, 710, "單號:- "+ order_info["order_id"])
		cvs.drawString(60, 690, "電話:- "+ order_info["phone_number"])
		cvs.drawString(420, 730, "時間 :- "+ serverTime(TimeMode.STRING))
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
		cvs.drawString(500, 60, order_info["total_price"])
		cvs.line(50, 50, 580, 50)#FROM TOP LAST LINE
		
		return cvs