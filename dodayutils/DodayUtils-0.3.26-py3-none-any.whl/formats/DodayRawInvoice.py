from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

class DodayRawInvoice:
	"""
	This represents the raw module printer
	for the doday order. 

	TODO: Should also be compatible with
	basic or graphic format. 
	"""
	def __init__(self):
		pass

	@dutils
	def order_info_to_printer_args(self, order_info, **kwargs):
		"""
		This is the function to prepare the
		order info for printer arguments
		"""
		print_order_args = []
		# payment_method
		print_order_args.append(c_char_p(order_info["payment_method"].encode('big5')))
		# stayortogo
		stayortogo = order_info.get_stayortogo_str()
		print_order_args.append(c_char_p(stayortogo.encode('big5')))

		# serial number
		print_order_args.append(c_char_p(str(order_info["serial_number"]).encode('utf-8')))

		# ordertime
		now = datetime.datetime.now()
		print_time_str = now.strftime("%H:%M:%S")
		print_date_str = now.strftime("%Y-%m-%d")
		print_order_args.append(c_char_p(print_date_str.encode('utf-8')))
		print_order_args.append(c_char_p(print_time_str.encode('utf-8')))

		# Total item counts
		total_cnt = len(order_info.orders)
		
		if order_info["plastic_bag"] > 0:
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
			sub_item_str = order_info.orders[i].get_options_str()
			subitemnames[i].value = sub_item_str.encode('big5')
			itemnames[i].value = order_info.orders[i].title[:].encode('big5')
			itemcounts_list.append(order_info.orders[i].amount)
			item_price = order_info.orders[i].price
			itemprices_list.append(item_price)
			total_price += item_price

		if order_info["plastic_bag"] > 0:
			itemnames[total_cnt].value = order_info.get_plastic_bag_str().encode('big5')
			subitemnames[total_cnt].value = b''
			itemcounts_list.append(1)
			itemprices_list.append(order_info["plastic_bag"])
			total_price += order_info["plastic_bag"]
		
		print_order_args.append(itemnames)
		print_order_args.append(subitemnames)
		print_order_args.append(itemcounts(*itemcounts_list))
		print_order_args.append(itemprices(*itemprices_list))

		print_order_args.append(c_int(total_price))
		print_order_args.append(c_int(order_info["total_discount"]))
		print_order_args.append(c_int(int(total_price) - order_info["total_discount"]))

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