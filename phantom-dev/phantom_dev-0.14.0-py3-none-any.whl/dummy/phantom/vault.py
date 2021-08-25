"""
During the execution of any action other than test connectivity, the app can
add attachments to a container.
These files are placed in the vault, which is a location within each container.
The app requires the container id to add a file in the vault.
The BaseConnector::get_container_id() API can be used to get this information.

Every vault item within a container is denoted by a vault_id.
"""
from typing import List, Tuple

from .app import AppStatus
from .base_connector import stub_method


@stub_method
def vault_add(
		container: int = None,
		file_location: str = None,
		file_name: str = None,
		metadata: dict = None,
		trace: bool = False,
):
	# This documentation is clearly not correct
	"""
	Add an ActionResult object into the Connector Run result.
	Returns the object added.

	:param container:
		The container to add the attachment to.
		The return value of BaseConnector::get_container_id() is sufficient.
	:param file_location:
		This is the location of the file on the Splunk Phantom file system.
		The file has to be written to the path returned by
		Vault.get_vault_tmp_dir() before calling this API.
	:param file_name: The file name to use.
	:param metadata:
		A dictionary containing metadata information the app can set about this
		attachment, dictionary keys that can be set are 'size' in bytes,
		'contains' is the contains of the file, 'action' is the action name,
		returned through the BaseConnector::get_action_name() API) and
		'app_run_id', which is the unique ID of this particular app run,
		returned by BaseConnector::get_app_run_id()).
	:param trace: Set to 'True' to return debug information.
	"""


@stub_method
def create_attachment(
	file_contents: bytes,
	container_id: int,
	file_name: str = None,
	metadata: dict = None,
):
	"""
	Create a file with the specified contents, and add that to the vault.
	Returns the object added.
	Other than accepting file_contents instead of a file_location, this API is
	the same as vault_add.

	:param file_contents:
		The contents of the file.
		A temporary file with these contents will be created, which will then
		be added to the vault.
	:param container_id:
		This is the container to add the attachment to.
		The return value of BaseConnector::get_container_id() is sufficient.
	:param file_name: The file name to use.
	:param metadata:
		A dictionary containing metadata information the app can set about this
		attachment, dictionary keys that can be set are 'size' in bytes,
		'contains' is the contains of the file, 'action' is the action name,
		returned through the BaseConnector::get_action_name() API) and
		'app_run_id', which is the unique ID of this particular app run,
		returned by BaseConnector::get_app_run_id()).
	"""


@stub_method
def get_vault_tmp_dir() -> str:
	"""
	Returns the path to the vault's temporary file directory.
	Files have to be added here before calling vault_add.
	"""


@stub_method
def vault_info(
		vault_id: str = None,
		file_name: str = None,
		container_id: int = None,
		trace: bool = False,
) -> Tuple[AppStatus, str, List[dict]]:
	"""
	The vault_info API returns a tuple; of a success flag either True or False,
	any response messages as strings, and information for all vault items that
	match either of the input parameters as a list.
	If neither of the parameters are specified, an empty list is returned.

	:param vault_id:
		The alphanumeric file hash of the vault file, such as
		41c4e1e9abe08b218f5ea60d8ae41a5f523e7534.
	:param file_name: The file name of the vault file.
	:param container_id:
		Container ID to query vault items for.
		To get the current container_id value from an app that is executing an
		action, use the return value of BaseConnector::get_container_id().
	:param trace: Set to 'True' to return debug information.
	"""


class Vault:
	"""
	Minimal dummy for the deprecated Phantom 4.8 interface
	"""
	@stub_method
	def get_file_path(self, vault_id: str) -> str: ...
