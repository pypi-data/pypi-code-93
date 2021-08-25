from collections.abc import Mapping, MutableMapping
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List

from phantom.app import APP_SUCCESS
from phantom.base_connector import BaseConnector


class RemoteError(Exception):
	def __init__(self, *args, responses, **kwargs):
		super().__init__(*args, **kwargs)
		self.responses = list(responses)


class data_member(property):
	def __init__(self, method: Callable, *args, **kwargs):
		self.data_key = None
		self.data_type = method.__annotations__.get('return')
		super().__init__(method, *args, **kwargs)

	def __set_name__(self, owner, name):
		self.data_key = name

	def __get__(self, instance, owner=None):
		if instance is None:
			return self

		value = instance[self.data_key]
		if value is None:
			return value

		try:
			is_expected_type = isinstance(value, self.data_type)
		except TypeError:
			return value
		
		if is_expected_type:
			return value

		return self.data_type(value)

	def __set__(self, instance, value):
		instance[self.data_key] = value


def datetime_data_member(format='%Y-%m-%d %H:%M:%S.%f%z'):
	class _wrapper(data_member):
		FORMAT = format

		def __get__(self, instance, owner=None):
			if instance is None:
				return self

			value: str = instance[self.data_key]

			if not value:
				return None

			if value.endswith('Z'):
				naive = datetime.strptime(value, self.FORMAT)
				return naive.replace(tzinfo=timezone.utc)

			# Container datetime strings only use a two-digit offset;
			# Pad minute digits to match format expected by strptime
			datetime_string = value + '00'
			return datetime.strptime(datetime_string, self.FORMAT)

		def __set__(self, instance, value):
			if value is not None:
				value = datetime.strftime(value, self.FORMAT)
				if value.endswith('00'):
					value = value[:-2]

			super().__set__(instance, value)

	return _wrapper


contains_map = {}


def contains(*args):
    """
    A parameterised decorator that sets the global contains map entry for the
    decorated type to the specified argument values.
    """
    def type_decorator(type_obj):
        contains_map.setdefault(type_obj, [*args])
        return type_obj

    return type_decorator


_NULL = object()


class _DictProxy(MutableMapping):
	_NULL = object()

	def __init__(self, mapping: MutableMapping):
		self._data = mapping

	def __getitem__(self, key):
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = value

	def __delitem__(self, key):
		del self._data[key]

	def __iter__(self):
		return iter(self._data)

	def __len__(self):
		return len(self._data)

	def __hash__(self):
		return hash(self._data)

	@classmethod
	def from_fields(
			cls,
			**kwargs,
	):
		instance = cls(mapping={})
		for name in cls._field_names():
			try:
				value = kwargs.pop(name)
			except KeyError:
				continue

			if value is _NULL:
				continue
			
			setattr(instance, name, value)

		if kwargs:
			raise ValueError(f'Unrecognised field values {kwargs}')

		return instance

	@classmethod
	def _field_names(cls):
		for name, value in cls.__dict__.items():
			if isinstance(value, data_member):
				yield name


class Container(_DictProxy):
	"""
	An interface to an underlying Phantom container JSON object.
	To create a JSON dict compatible with the `phantom.base_connector` API from
	a `container: Container` object, call `dict(container)`.

	Containers are the top-level data structure that Splunk Phantom playbook
	APIs operate on.
	Every container is a structured JSON object which can nest more arbitrary
	JSON objects, that represent artifacts.
	A container is the top-level object against which automation is run.

	Assign a label to a container to dictate the kind of content it contains.
	This label defines how the respective elements are managed within the
	platform and where they are organized.
	Assign this label during the ingest phase and in the ingest configuration
	when you configure an asset as a data source.

	Following this model, you might label containers imported from a SIEM as
	"Incidents".
	Or you might label containers imported from a vulnerability management
	product as "Vulnerabilities", or containers imported from an IP
	intelligence source as "Intelligence".
	For each label that the system ingests, a new top-level menu item appears
	within the top-level product navigation to allow you to navigate to the
	list of respective containers for that label.
	In addition, playbooks, the mechanism by which automated actions are run on
	a container, are container-specific and run only on containers that match
	their label.

	This architecture allows for arbitrary data to be imported and run across
	the security operations domain, beyond the management of security incidents
	alone.

	Data can be imported from various sources and can be structured or
	unstructured.
	Even in the case of structured data, information might be categorized,
	classified, named, and represented in incompatible and disparate formats.
	In either case, the data has to be normalized to be accessible and
	actionable by the platform.
	The Splunk Phantom platform uses apps that support ingest and interface
	with these assets.
	These apps provide the necessary functionality to map the raw data format
	from the source to a standard Common Event Format (CEF) schema, if
	applicable.

	CEF is an open log management standard that improves the interoperability
	of security-related information from different network and security devices
	and applications.
	After the data is normalized into CEF format, automation can leverage
	accessing various attributes without any ambiguity.
	Splunk Phantom makes both the original data in its native format and
	normalized format available because there is an information fidelity and
	application-specific detail in the raw data that might not be
	well-represented in CEF format.
	"""
	@contains('phantom container id')
	class Id(int):
		"""An integer representing a container ID"""

	@data_member
	def id(self) -> Id:
		"""
		A unique identifier for the incident, generated by the Splunk Phantom
		platform. 
		"""

	@data_member
	def version(self) -> str:
		"""
		The version of this schema, for schema migration purposes.
		"""

	@data_member
	def label(self) -> str:
		"""
		The label as specified in the ingest asset.
		When you configure an ingestion asset, you can define a label for the
		containers ingested from that asset.
		For example, you might define "Incident" from a Splunk asset or "Email"
		from an IMAP asset. 
		"""

	@data_member
	def name(self) -> str:
		"""
		The name of the item, as found in the ingest or source application and
		incident name in a SIEM. 
		"""

	@data_member
	def source_data_identifier(self) -> str:
		"""
		The identifier of the container object as found in the ingestion
		source.
		An incident in a SIEM can have an identifier of its own that might be
		passed on to Splunk Phantom as part of the ingestion.
		In the absence of any source data identifier provided, a GUID is
		generated and provided. 
		"""

	@data_member
	def description(self) -> str:
		"""
		The description for the container as found in the ingest source.
		"""

	@data_member
	def status(self) -> str:
		"""
		The status of this container. For example, you can define a status as
		new, open, closed, or as a custom status defined by an administrator.
		"""

	@data_member
	def sensitivity(self) -> str:
		"""
		The sensitivity of this container such as red, amber, green, or white.
		"""

	@data_member
	def severity(self) -> str:
		"""
		The severity of this container.
		For example, you can define severity as medium, high, or as a custom
		severity defined by an administrator.
		"""

	@datetime_data_member()
	def create_time(self) -> datetime:
		"""
		The timestamp of when this container was created in Splunk Phantom.
		"""

	@datetime_data_member()
	def start_time(self) -> datetime:
		"""
		The timestamp of when activity related to this container was first
		seen.
		This is also the time when the first artifact was created for this
		container.
		As artifacts are added to the container, the start time might change if
		an older artifact for that incident is added to the container.
		"""

	@datetime_data_member()
	def end_time(self) -> datetime:
		"""
		The timestamp of when activity related to this container was last seen.
		This is also the time when the last artifact was created for this
		container.
		As artifacts are added to the container, start time may change if a
		later artifact for that incident is added to the container.
		"""

	@datetime_data_member('%Y-%m-%d %H:%M:%S%z')
	def due_time(self) -> datetime:
		"""
		The timestamp of when the SLA for this container expires and it is
		considered to be in breach of its SLA.
		The SLAs for the container are either set by the user or default
		determined by the platform depending on the severity and the Event
		Settings.
		You can define default SLAs for container severity from Main Menu >
		Administration > Event Settings > Response.
		"""

	@datetime_data_member()
	def close_time(self) -> datetime:
		"""
		The timestamp of when this container was closed or resolved by the user
		or playbook.
		"""

	@data_member
	def kill_chain(self) -> str:
		"""
		If the ingestion source and app provide kill-chain information about
		the incident, it's stored in this field.
		"""

	@data_member
	def owner(self) -> str:
		"""
		The user who currently owns the incident.
		Administrators can assign the container to any user in the system.
		"""

	@data_member
	def hash(self) -> str:
		"""
		This is the hash of the container data as ingested and is used to avoid
		duplicate containers being added to the system tags assigned to a
		container.
		"""

	@data_member
	def asset(self) -> int:
		"""
		The ID of the asset from which the container was ingested.
		If the user created this incident, this field does not contain a value.
		"""

	@data_member
	def asset_name(self) -> str:
		"""
		The name of the asset from which the container was ingested.
		If the user created this incident, this field does not contain a value.
		"""

	@datetime_data_member()
	def artifact_update_time(self) -> datetime:
		"""
		The time when the artifact was last added to the container.
		"""

	@datetime_data_member()
	def container_update_time(self) -> datetime:
		"""
		The time when the container was last updated.
		This includes adding an artifact or changing any state or field of the
		container.
		"""

	@data_member
	def data(self) -> dict:
		"""
		This is a dictionary of the raw container data as seen in the ingestion
		asset or application.
		This is the data that is parsed to populate the artifacts and its CEF
		fields.
		"""

	@data_member
	def artifact_count(self) -> int:
		"""
		This is the count of total artifacts that belong to this container.
		"""

	@data_member
	def tags(self) -> List[str]:
		"""
		Missing from the API documentation
		"""

	@data_member
	def ingest_app_id(self) -> str:
		"""
		Missing from the API documentation
		"""

	@property
	def artifacts(self) -> Iterable:
		return (Artifact(a) for a in self._data.get('artifacts', []))

	def add_artifact(self, artifact: MutableMapping):
		"""
		Add artifact data to the container
		"""
		if not isinstance(artifact, Artifact):
			artifact = Artifact(artifact)

		self.setdefault('artifacts', []).append(artifact._data)
		return artifact

	@classmethod
	def from_fields(
			cls,
			*,
			id: Id = _NULL,
			label: str = _NULL,
			name: str = _NULL,
			source_data_identifier: str = _NULL,
			description: str = _NULL,
			status: str = _NULL,
			sensitivity: str = _NULL,
			severity: str = _NULL,
			due_time: datetime = _NULL,
			kill_chain: str = _NULL,
			owner: str = _NULL,
			asset: int = _NULL,
			data: dict = _NULL,
			tags: List[str] = _NULL,
	):
		"""
		Create a Container with the specified field values
		"""
		fields = {
			k: v for k, v in locals().items() if k not in ['cls', '__class__']}
		return super().from_fields(**fields)


class Artifact(_DictProxy):
	"""
	An interface to an underlying Phantom artifact JSON object.
	To create a JSON dict compatible with the `phantom.base_connector` API from
	an `artifact: Artifact` object, call `dict(artifact)`.

	Artifacts are JSON objects that are stored in a container.
	Artifacts are objects that are associated with a container and serve as
	corroboration or evidence related to the container.
	Much like the container schema, the artifact schema has a common header
	that can be operated on, and also contains a Common Event Format (CEF) body
	and raw data body to store elements that can be accessed by Splunk Phantom
	playbooks.
	"""
	@contains('phantom artifact id')
	class Id(int):
		"""An integer representing an artifact ID"""

	@data_member
	def id(self) -> Id:
		"""
		A unique identifier for the artifact, generated by the Splunk Phantom
		platform.
		"""

	@data_member
	def version(self) -> int:
		"""
		The version of this schema.
		"""

	@data_member
	def name(self) -> str:
		"""
		A name of the artifact as identified by the ingestion app from the data
		source.
		"""

	@data_member
	def label(self) -> str:
		"""
		The label as identified by the app that is ingesting the data.
		Labels can be anything that is found to be the label of the data or
		event in the ingestion data source.
		For example, labels can be event, FWAlert, AVAlert, to name a few.
		"""

	@data_member
	def source_data_identifier(self) -> str:
		"""
		The identifier of the artifact as found in the ingestion data source.
		"""

	@datetime_data_member('%Y-%m-%dT%H:%M:%S.%fZ')
	def create_time(self) -> datetime:
		"""
		The timestamp of when this artifact was created in Splunk Phantom.
		"""

	@datetime_data_member('%Y-%m-%dT%H:%M:%S.%fZ')
	def start_time(self) -> datetime:
		"""
		The timestamp of when this artifact was first seen.
		This timestamp typically coincides with when the artifact was initially
		detected or produced by the device that generated it.
		"""

	@datetime_data_member()
	def end_time(self) -> datetime:
		"""
		The timestamp of this artifact as last seen in the ingestion data
		source.
		"""

	@data_member
	def severity(self) -> str:
		"""
		The severity of this artifact.
		For example, medium, high, or a custom severity created by an
		administrator.
		"""

	@data_member
	def type(self) -> str:
		"""
		The type of artifact. The type is used to identify the origin of this
		artifact, such as "network" or "host".
		"""

	@data_member
	def kill_chain(self) -> str:
		"""
		The kill-chain value as specified by the ingestion app and data source.
		"""

	@data_member
	def hash(self) -> str:
		"""
		The hash of the contents of the artifact.
		The hash is used by the platform to avoid saving duplicate artifacts
		for the same container.
		"""

	@data_member
	def cef(self) -> Dict[str, Any]:
		"""
		A normalized representation of the data mapped to each field's
		representative CEF key.
		"""

	@data_member
	def container(self) -> int:
		"""
		The ID of the container that contains this artifact.
		"""

	@data_member
	def tags(self) -> List[str]:
		"""
		The list of tags assigned to this artifact.
		"""

	@data_member
	def data(self) -> Any:
		"""
		The raw representation of the data.
		"""

	@data_member
	def description(self) -> str:
		"""
		Missing from the API documentation
		"""

	@classmethod
	def from_fields(
			cls,
			*,
			id: Id = _NULL,
			name: str = _NULL,
			label: str = _NULL,
			source_data_identifier: str = _NULL,
			severity: str = _NULL,
			type: str = _NULL,
			kill_chain: str = _NULL,
			cef: Dict[str, Any] = _NULL,
			container: Container.Id = _NULL,
			tags: List[str] = _NULL,
			data: dict = _NULL,
			description: str = _NULL,
	):
		"""
		Create an Artifact with the specified field values
		"""
		fields = {
			k: v for k, v in locals().items() if k not in ['cls', '__class__']}
		return super().from_fields(**fields)
