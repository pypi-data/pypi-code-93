from DodayUtils._exceptions import *

configs = {}

def dutils(function):
	"""
	This is the wrapper function to wrap
	the utility functions and handle error
	"""
	def handle_error(*args, **kwargs):
		"""
		This wraps try except clause around the function
		and return the error message. 
		"""
		response = None
		try:
			kwargs.update(configs)
			response = function(*args, **kwargs)
			ret = {"indicator": True, "message": response}
		except Exception as e:
			_, _, exc_tb = sys.exc_info()
			fobj = traceback.extract_tb(exc_tb)[-1]
			fname = fobj.filename
			line_no = fobj.lineno

			ddyerror = DodayUtilError.buildfromexc(str(e), fname, line_no, ''.join(traceback.format_tb(exc_tb)))
			logging.error("DodayUtilError = "+str(ddyerror))
			print("DodayUtilError = "+str(ddyerror))
			ret = ddyerror.json_response

		if response != None:
			return ret["message"]

	return handle_error

def initialize_doday_configs(cfg):
	global configs
	configs.update(cfg)
	