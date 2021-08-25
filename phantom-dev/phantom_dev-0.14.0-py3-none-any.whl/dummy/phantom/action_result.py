from copy import deepcopy
from typing import Any, List

from phantom_dev.dummy.phantom.app import AppStatus

from .app import APP_SUCCESS, APP_ERROR


class ActionResult:
	"""
	Dummy ActionResult interface
	"""
	def __init__(self, param):
		self.__state = {
			'context': {},
			'data': [],
			'extra_data': [],
			'message': '',
			'parameter': param,
			'summary': {},
		}
		self.__debug_data = []
		self.__exceptions = []
		self.__status = APP_SUCCESS

	def add_data(self, item: dict) -> dict:
		"""
		Add a data item as a dictionary to the list. Returns the item added.

		:param item:
			This is a dictionary that needs to be added as a new element to the
			current data list.
		"""
		self.__state['data'].append(item)

	def update_data(self, item: List[dict]):
		"""
		Extend the data list with elements in the item list.

		:param item:
			This is a list of items that needs to be added to the current data
			list. 
		"""
		self.__state['data'].extend(item)

	def get_data(self) -> List[dict]:
		"""
		Get the current data list.
		"""
		return self.__state['data']

	def get_data_size(self) -> int:
		"""
		Get the current data list size.
		"""
		return len(self.__state['data'])

	def add_debug_data(self, item: Any):
		"""
		Add a debug data item to the list.
		The item will be converted to a string object through the str(...) call
		before it is added to the list.
		This list is dumped in the spawn.log file if the action result fails.
		"""
		self.__debug_data.append(str(item))

	def get_debug_data_size(self) -> int:
		"""
		Get the current debug data list size.
		"""
		return len(self.__debug_data)

	def add_extra_data(self, item: dict) -> dict:
		"""
		Add an extra data item as a dictionary to the list.

		Extra data is different from data that is added through the
		add_data(...) API.
		Apps can add data as extra data if the data is huge and none of it is
		rendered.
		Typically, this is something that needs to be recorded and can
		potentially be used from a playbook, but not rendered.
		Returns the item added.
		"""
		self.__state['extra_data'].append(item)
		return item

	def get_extra_data(self) -> List[dict]:
		"""
		Get the current extra data list.
		"""
		return self.__state['extra_data']

	def get_extra_data_size(self) -> int:
		"""
		Get the current extra data list size.
		"""
		return len(self.__state['extra_data'])

	def update_extra_data(self, item: List[dict]):
		"""
		Extend the extra data list with elements in the item list.
		"""
		self.__state['extra_data'].extend(item)

	def add_exception_details(self, exception: Exception) -> AppStatus:
		"""
		Add details of an exception into the action result.
		These details are appended to the message in the resultant dictionary.
		Returns the current status code of the object.

		:param exception:
			The Python exception object that has occurred.
			ActionResult will convert this exception object to string format
			and append it to the message.
		"""
		# Cannot confirm the above?
		self.__exceptions.append(exception)
		return self.get_status()

	def append_to_message(self, message_str: str):
		"""
		Append the text to the message

		:param message_str: The string to append to the existing message.
		"""
		self.__state['message'].append(message_str)

	def get_dict(self) -> dict:
		"""
		Create a dictionary from the current state of the object.
		This is usually called from BaseConnector.
		"""
		value = deepcopy(self.__state)
		try:
			value['status']
		except KeyError:
			if self.__status == APP_ERROR:
				value['status'] = 'failed'
			else:
				value['status'] = 'success'

		return value

	def get_message(self) -> str:
		"""
		Get the current action result message.
		"""
		return self.__state['message']

	def get_param(self) -> dict:
		"""
		Get the current parameter dictionary.
		"""
		return self.__state['parameter']

	def get_status(self) -> AppStatus:
		"""
		Get the current result.
		It returns either phantom.APP_SUCCESS or phantom.APP_ERROR.
		"""
		return self.__status

	def get_summary(self) -> dict:
		"""
		Return the current summary dictionary.
		"""
		return self.__state['summary']

	def is_fail(self) -> bool:
		"""
		Returns 'True' if the ActionResult status is a failure.
		"""
		return self.__status == APP_ERROR

	def is_success(self) -> bool:
		"""
		Returns 'True' if the ActionResult status is success.
		"""
		return self.__status == APP_SUCCESS

	def set_status(
			self,
			status_code: AppStatus,
			status_message: str = '',
			exception: Exception = None,
			*unnamed_format_args: Any,
			**named_format_args: Any,
	) -> AppStatus:
		"""
		Set the status of a result.
		To call this function with unnamed format arguments, pass a message.
		Pass "" as the status_message, if you want to set an exception
		parameter instead of a message.
		Pass 'None' if an exception is not to be used.
		status_code has to be phantom.APP_SUCCESS or phantom.APP_ERROR.
		Returns the status_code set.

		:param status_code:
			The status of the connector run.
			It is either phantom.APP_SUCCESS or phantom.APP_ERROR. 
		:param status_message:
			The message to set.
			Typically, this is a short description of the error or success.
		:param exception:
			The Python exception object that has occurred.
			BaseConnector will convert this exception object to string format
			and append it to the message. 
		:param unnamed_format_args:
			The various parameters that need to be formatted into the
			status_message string. 
		:param named_format_args:
			The various parameters that need to be formatted into the
			status_message string. 
		"""
		self.__status = status_code
		if status_message:
			positional_formatted = status_message % unnamed_format_args
			self.__state['status'] = positional_formatted.format_map(
				named_format_args)
		
		if exception is not None:
			self.add_exception_details(exception)

		return self.__status

	def set_param(self, param_dict: dict):
		"""
		Set the parameter dictionary with the passed param_dict.
		This overwrites the current parameter dictionary

		:param param_dict:
			The Python dictionary that overwrites the current parameter. 
		"""
		self.__state['parameter'] = param_dict

	def update_param(self, param_dict: dict):
		"""
		Update the parameter dictionary with 'param_dict'

		:param param_dict:
			The Python dictionary that is to be updated into the current
			parameter.
		"""
		self.__state['parameter'].update(param_dict)

	def set_summary(self, summary: dict) -> dict:
		"""
		Replace the summary with the passed summary dictionary.
		Returns the summary set.

		:param summary:
			The Python dictionary that overwrites the current summary.
		"""
		self.__state['summary'] = summary
		return summary

	def update_summary(self, summary: dict) -> dict:
		"""
		Updates the summary with the passed summary dictionary.
		Returns the updated summary.
		"""
		self.__state['summary'].update(summary)
		return self.__state['summary']
