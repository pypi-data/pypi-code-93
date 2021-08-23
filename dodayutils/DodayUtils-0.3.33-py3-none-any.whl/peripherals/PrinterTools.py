import cups
import glob
import logging

from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

def deviceprint(printer_name, folder_path=None):
	"""
	This is the decorator that pass in
	the printer name string and perform
	printing. 
	- Input:
		* printer_name: e.g. 
			- ARGOX_D2-250_PPLB
			- ARGOX_D2-250_PPLZ
	"""
	def print_func(func):
		# usb printing function wrapper
		@dutils
		def handle_print(*args, **kwargs):
			# clean tmp filepath
			files = glob.glob(folder_path+'/*')
			safe_remove_set = {".pdf", ".png", ".jpg"}
			# guard for specific filetype
			for f in files:
				if f[-4:] in safe_remove_set:
					os.remove(f)

			temp_file_path, job_name = func(*args, **kwargs)

			print(temp_file_path, printer_name, job_name)
			conn = cups.Connection()
			conn.printFile(printer_name,temp_file_path,job_name,{})

		return handle_print
	return print_func