from abc import ABCMeta, abstractmethod
from logging import getLogger
from functools import wraps
import json
from pathlib import Path
from pprint import pformat
from tempfile import TemporaryDirectory
from types import FunctionType
from typing import Any, List, Tuple

from .action_result import ActionResult
from .app import APP_ERROR, APP_SUCCESS, AppStatus


dummy_logger = getLogger(name=__name__)


def stub_method(method):
	"""
	Raise a NotImplementedError if the decorated method is called and doesn't
	return a non-None result
	"""
	error = NotImplementedError(
		f'Stub method {method.__qualname__}'
		' requires patching before this test'
	)
	@wraps(method)
	def wrapper(*args, **kwargs):
		try:
			result = method(*args, **kwargs)
		except Exception as raised_error:
			raise error from raised_error

		if result is None:
			raise error

		return result

	return wrapper


class BaseConnector(metaclass=ABCMeta):
	"""
	Dummy BaseConnector interface
	"""
	def __init__(self):
		self.__action_json = None
		self.__current_param = None
		self.__action_results = []
		self.__state = None
		self.__status = APP_SUCCESS
		self.__status_message = None
		self.__was_cancelled = False
		self.__summary = {}

	def add_action_result(self, action_result: ActionResult) -> ActionResult:
		"""
		Add an ActionResult object into the connector run result.
		Returns the object added.

		:param action_result:
			The ActionResult object to add to the connector run.
		"""
		self.__action_results.append(action_result)
		return action_result

	def append_to_message(self, message: str):
		"""
		Appends a string to the current result message.

		:param message:
			The string that is to be appended to the existing message.
		"""
		self.get_action_results()[-1].append_to_message(message)

	def debug_print(self, tag: str, dump_object: Any =''):
		"""
		Dumps a pretty printed version of the 'dump_object' in the
		<syslog>/phantom/spawn.log file, where <syslog> typically is /var/log/.

		:param tag:
			The string that is prefixed before the dump_object is dumped.
		:param dump_object:
			The dump_object to dump.
			If the object is a list, dictionary and so on it is automatically
			pretty printed.
		"""
		dummy_logger.debug('%s%s', tag, _dump_str(dump_object))

	def error_print(self, tag: str, dump_object: Any = ''):
		"""
		Dumps an ERROR as a pretty printed version of the 'dump_object' in the
		<syslog>/phantom/spawn.log file, where <syslog> typically is /var/log/.
		Refrain from using this API to dump an error that is handled by the App.
		By default the log level of the platform is set to ERROR.
		"""
		dummy_logger.error('%s%s', tag, _dump_str(dump_object))

	def finalize(self):
		"""
		Optional function that can be implemented by the AppConnector.
		Called by the BaseConnector once all the elements in the parameter list
		are processed.
		"""

	@stub_method
	def get_action_identifier(self) -> str:
		"""
		Returns the action identifier that the AppConnector is supposed to run.
		"""
		return self.__action_json['identifier']

	def get_action_results(self) -> List[ActionResult]:
		"""
		Returns the list of ActionResult objects added to the connector run.
		"""
		return self.__action_results

	@stub_method
	def get_action_config(self) -> dict:
		"""
		Returns the app configuration dictionary.
		"""
		return self.__action_json['config']

	def get_app_id(self) -> str:
		"""
		Returns the appid of the app that was specified in the app JSON.
		"""
		return self.get_app_json()['appid']

	@stub_method
	def get_app_json(self) -> dict:
		"""
		Returns the appid of the app that was specified in the app JSON.
		"""

	@stub_method
	def get_asset_id(self) -> str:
		"""
		Returns the current asset ID passed in the connector run action JSON.
		"""
		return self.__action_json['asset_id']

	@stub_method
	def get_ca_bundle(self) -> str:
		"""
		Returns the current CA bundle file.
		"""

	@stub_method
	def get_config(self) -> dict:
		"""
		Returns the current connector run configuration dictionary.
		"""
		return self.__action_json['config']

	@stub_method
	def get_connector_id(self) -> int:
		"""
		Returns the appid of the app that was specified in the app JSON.
		"""

	@stub_method
	def get_container_id(self) -> int:
		"""
		Returns the current container ID passed in the connector run action
		JSON.
		"""
		return self.__action_json['container_id']

	@stub_method
	def get_container_info(self, container_id: int = None) -> dict:
		"""
		Returns info about the container.
		If container_id is not passed, returns info about the current container.
		"""

	@stub_method
	def get_current_param(self) -> dict:
		"""
		Returns the current parameter dictionary that the app is working on.
		"""
		return self.__current_param

	@stub_method
	def get_product_installation_id(self) -> str:
		"""
		Returns the unique ID of the Splunk Phantom product installation.
		"""

	@stub_method
	def get_product_version(self) -> str:
		"""
		Returns the version of the Splunk Phantom product.
		"""

	def get_state(self) -> dict:
		"""
		Get the current state dictionary of the asset.
		Will return None if load_state() has not been previously called.
		"""
		return self.__state

	def get_state_file_path(self) -> str:
		"""
		Get the full current state file path.
		"""
		return str(Path(self.get_state_dir(), 'state.json'))

	@stub_method
	def get_state_dir(self) -> str:
		"""
		An app might require to create files to access during action executions.
		It can use the state directory returned by this API to store such files.
		"""

	def get_status(self) -> AppStatus:
		"""
		Get the current status of the connector run.
		Returns either phantom.APP_SUCCESS or phantom.APP_ERROR.
		"""
		return self.__status

	def get_status_message(self) -> str:
		"""
		Get the current status message of the connector run.
		"""
		return self.__status_message

	@abstractmethod
	def handle_action(self, param: dict):
		"""
		Every AppConnector is required to implement this function
		It is called for every parameter dictionary in the parameter list.

		:param param:
			The current parameter dictionary that needs to be acted on.
		"""

	def handle_cancel(self):
		"""
		Optional function that can be implemented by the AppConnector.
		This is called if the action was cancelled.
		"""

	def handle_exception(self, exception: Exception) -> Any:
		"""
		Optional function that can be implemented by the AppConnector.
		Called if the BaseConnector::_handle_action function code throws an
		exception that is not handled.
		"""
		raise exception

	def initialize(self):
		"""
		Optional function that can be implemented by the AppConnector.
		This is called once before starting the parameter list iteration,
		for example, before the first call to AppConnector::handle_action()
		"""

	def is_action_cancelled(self) -> bool:
		"""
		Returns 'True' if the connector run was cancelled.
		Otherwise, it returns as 'False'.
		"""
		return self.__was_cancelled

	def is_fail(self) -> bool:
		"""
		Returns 'True' if the status of the connector run result is failure.
		Otherwise, it returns as 'False'.
		"""
		return self.__status == APP_ERROR

	@stub_method
	def is_poll_now(self) -> bool:
		"""
		The on_poll action is called during Poll Now and scheduled polling.
		Returns 'True' if the current on_poll is run through the Poll Now
		button.
		Otherwise, it returns as 'False'.
		"""

	def is_success(self) -> bool:
		"""
		Returns 'True' if the status of the Connector Run result is success.
		Otherwise, it returns as 'False'.
		"""
		return self.__status == APP_SUCCESS

	def load_state(self):
		"""
		Load the current state file into the state dictionary.
		If a state file does not exist, it creates one with the app_version
		field.
		This returns the state dictionary.
		If an error occurs, this returns None.
		"""
		state_path = Path(self.get_state_file_path())
		if state_path.exists():
			with Path(self.get_state_file_path()).open() as state_file:
				self.__state = json.load(state_file)
		else:
			self.__state = {}

	def remove_action_result(self, action_result: ActionResult) -> ActionResult:
		"""
		Remove an ActionResult object from the connector run result.
		Returns the removed object.

		:param action_result:
			The ActionResult object that is to be removed from the connector
			run. 
		"""
		self.__action_results.remove(action_result)
		return action_result

	@stub_method
	def save_artifact(self, artifact: dict) -> Tuple[AppStatus, str, int]:
		"""
		Save an artifact to the Splunk Phantom platform.

		Save artifacts more efficiently with the save_container API, since a
		single function call can add a container and all its artifacts.
		
		See [Active playbooks](http://docs.splunk.com/Documentation/Phantom/latest/DevelopApps/AppDevAPIRef#Active_playbooks)
		to learn how to set the run_automation key in the artifact dictionary.

		:param artifact: Dictionary containing information about an artifact.
		:return:
			Returns the following tuple:
				status: phantom.APP_SUCCESS or phantom.APP_ERROR.
				message: Status message.
				id: Saved artifact ID if success. 
		"""

	@stub_method
	def save_artifacts(
			self, artifacts: List[dict]) -> Tuple[AppStatus, str, List[int]]:
		"""
		Save a list of artifacts to the Splunk Phantom platform.

		Save artifacts more efficiently with the save_container API, since a
		single function call can add a container and all its artifacts.
		
		See \
		[Active playbooks](http://docs.splunk.com/Documentation/Phantom/latest/DevelopApps/AppDevAPIRef#Active_playbooks)
		to learn how to set the run_automation key in the artifact dictionary.

		:param artifacts:
			A list of dictionaries that each contain artifact data.
			Don't set the run_automation key for the any artifacts as the API
			will automatically set this value to 'False' for all but the last
			artifact in the list to start any active playbooks after the last
			artifact is ingested. 

		:return:
			Returns the following tuple:
				status: phantom.APP_SUCCESS or phantom.APP_ERROR.
				message: Status message.
				id_list:\
					List of saved artifact IDs if successful; none otherwise.
		"""

	@stub_method
	def save_container(self, container: dict) -> Tuple[AppStatus, str, int]:
		"""
		Save a container and artifacts to the Splunk Phantom platform.

		See \
		[Active playbooks](http://docs.splunk.com/Documentation/Phantom/latest/DevelopApps/AppDevAPIRef#Active_playbooks)
		to learn how to set the run_automation key in the artifact dictionary.

		:param container:
			Dictionary containing info about a container.
			To ingest a container and artifacts in a single call, add a key
			called artifacts to the container dictionary.
			This key contains a list of dictionaries, each item in the list
			representing a single artifact.
			Don't set the run_automation key for the container or artifacts.
			The API will automatically set this value to 'False' for all but
			the last artifact in the list to start any active playbooks after
			the last artifact is ingested.

		:return:
			Returns the following tuple
				status: phantom.APP_SUCCESS or phantom.APP_ERROR.
				message: Status message.
				id: Saved container ID if success, none otherwise.
		"""

	@stub_method
	def save_containers(
			self, containers: List[dict]) -> Tuple[AppStatus, str, List[dict]]:
		"""
		Save a list of containers to the phantom platform.

		This is the most performant API to use during ingestion as you can
		create all the artifacts and containers at once.

		As long as at least one container is successfully added, the status is
		success.
		During ingestion, BaseConnector automatically keeps track of how many
		containers and artifacts are successfully added, though if you do want
		to know more about an individual failure you need to iterate over the
		list in the response and check the message.

		:param containers:
			A list of dictionaries that each contain information about a
			container.
			Each dictionary follows the same rules as the input to
			save_container. 

		:return:
			Returns the following tuple:
				status:
					phantom.APP_SUCCESS or phantom.APP_ERROR.
					This is successful when at least one container is
					successfully created.
				message: Status message.
				container_responses:
					A list of responses for each container.
					There will be one response for each container in the input
					list.
					This is a dictionary with the following keys:
						success (phantom.APP_SUCCESS or phantom.APP_ERROR),
						message, and id. 
		"""

	def save_progress(
			self,
			progress_str_const: str,
			*unnamed_format_args: Any,
			**named_format_args: Any
	):
		"""
		This function sends a progress message to the Splunk Phantom core,
		which is saved in persistent storage.

		:param progress_str_const:
			The progress message to send to the Spunk Phantom core.
			Typically, this is a short description of the current task.
		:param unnamed_format_args:
			The various parameters that need to be formatted into the
			progress_str_config string
		:param named_format_args:
			The various parameters that need to be formatted into the
			progress_str_config string.
		"""
		dummy_logger.info(
			(progress_str_const % unnamed_format_args).format_map(
				named_format_args)
		)

	def save_state(self, state_dict: dict):
		"""
		Write a given dictionary to a state file that can be loaded during
		future app runs.
		This is especially crucial with ingestion apps.
		The saved state is unique per asset.
		An app_version field will be added to the dictionary before saving.

		:param state_dict: The dictionary to write to the state file.
		"""
		with Path(self.get_state_file_path()).open('w') as state_file:
			state_dict.setdefault('app_version', None)
			json.dump(state_dict, state_file)

	def send_progress(
			self,
			progress_str_const: str,
			*unnamed_format_args: Any,
			**named_format_args: Any,
	):
		"""
		This function sends a progress message to the Splunk Phantom core.
		It is written to persistent storage, but is overwritten by the message
		that comes in through the next send_progress call.
		Use this function to send messages that need not be stored over a
		period of time like percent completion messages while downloading a
		file.

		:param progress_str_const:
			The progress message to send to the Splunk Phantom core.
			Typically, this is a short description of the current task being
			carried out.
		:param unnamed_format_args:
			The various parameters that need to be formatted into the
			progress_str_config string.
		:param named_format_args:
			The various parameters that need to be formatted into the
			progress_str_config string. 
		"""
		self.save_progress(
			progress_str_const, *unnamed_format_args, **named_format_args)

	def set_status_save_progress(
			self,
			status_code: AppStatus,
			status_message: str = '',
			exception: Exception = None,
			*unnamed_format_args,
			**named_format_args,
	) -> AppStatus:
		"""
		Helper function that sets the status of the connector run.
		This needs to be phantom.APP_SUCCESS or phantom.APP_ERROR.
		This function sends a persistent progress message to the Splunk Phantom
		Core in a single call.
		Returns the status_code set.

		:param status_code:
			The status to set of the connector run.
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
			status_message string
		"""
		self.__status = status_code
		self.__status_message = status_message
		self.save_progress(
			status_message + str(exception),
			*unnamed_format_args,
			**named_format_args,
		)
		return self.__status

	@stub_method
	def set_validator(self, contains, validator) -> Tuple[AppStatus, str]:
		"""
		Set the validator of a particular contains, this is set for the current
		connector run only.
		Call this from the initialize function.

		:return:
			Returns the following tuple:
				status: phantom.APP_SUCCESS or phantom.APP_ERROR.
				message: Status message.
		"""

	@stub_method
	def validate_parameters(self, param: dict):
		"""
		BaseConnector uses this function to validate the current parameter
		dictionary based on the contains of the parameter.
		The AppConnector can override it to specify its own validations.
		"""

	def update_summary(self, summary: dict):
		"""
		Update the connector run summary dictionary with the passed dictionary.

		:param summary:
			The Python dictionary that needs to be updated to the current
			connector run summary.
		"""
		self.__summary.update(summary)

	def _handle_action(self, in_json, handle) -> str:
		self.__action_json = json.loads(in_json)
		with TemporaryDirectory() as tmp_dir:
			self.get_state_dir = lambda: tmp_dir
			for param in self.__action_json['parameters']:
				self.__current_param = param
				try:
					self.handle_action(param)
				except KeyboardInterrupt:
					self.__was_cancelled = True
					self.handle_cancel()
				except Exception as error:
					dummy_logger.exception(error)
					self.handle_exception(error)

		return json.dumps(list(r.get_dict() for r in self.__action_results))


def _dump_str(obj):
	if isinstance(obj, str):
		return obj

	return pformat(obj)
