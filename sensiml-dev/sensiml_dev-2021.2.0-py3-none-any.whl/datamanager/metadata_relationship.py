import sensiml.base.utility as utility
import logging
from sensiml.datamanager.base import Base, BaseSet


logger = logging.getLogger(__name__)


class MetadataType(object):
    Int = "integer"
    Float = "float"
    String = "string"


class MetadataRelationship(Base):
    """Base class for a metadata object."""

    _fields = ["uuid", "metadata", "metadata_value", "created_at", "last_modified"]
    _field_map = {"metadata": "label", "metadata_value": "label_value"}

    def __init__(
        self, connection, project, capture=None, metadata=None, metadata_value=None
    ):
        """
        Initialize a metadata object.

            Args:
                connection
                project
                capture

        """

        self._uuid = None
        self._project = project
        self._capture = capture
        self._metadata = metadata
        self._metadata_value = metadata_value

    @property
    def uuid(self):
        """Auto generated unique identifier for the metadata object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def capture(self):
        if isinstance(self._capture, str):
            return self._capture
        else:
            return self._capture.uuid

    @capture.setter
    def capture(self, value):
        self._capture = value

    @property
    def metadata(self):
        if isinstance(self._metadata, str):
            return self._metadata
        else:
            return self._metadata.uuid

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def metadata_value(self):
        if isinstance(self._metadata_value, str):
            return self._metadata_value
        else:
            return self._metadata_value.uuid

    @metadata_value.setter
    def metadata_value(self, value):
        self._metadata_value = value

    def insert(self):
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""

        url = "v2/project/{0}/capture/{1}/metadata-relationship/".format(
            self._project.uuid, self.capture
        )

        data = self._to_representation()

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self):
        """Calls the REST API and updates the object on the server."""
        url = "v2/project/{0}/capture/{1}/metadata-relationship/{2}/".format(
            self._project.uuid, self.capture, self.uuid
        )

        data = self._to_representation()

        response = self._connection.request("put", url, data)
        response_data, err = utility.check_server_response(response)

        return response

    def delete(self):
        """Calls the REST API and deletes the object from the server."""

        url = "v2/project/{0}/capture/{1}/metadata-relationship/{2}/".format(
            self._project.uuid, self.capture, self.uuid
        )

        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return response

    def refresh(self):
        """Calls the REST API and populates the local object's properties from the server."""

        url = "v2/project/{0}/capture/{1}/metadata-relationship/{2}/".format(
            self._project.uuid, self.capture, self.uuid
        )

        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def initialize_from_dict(self, data):
        """Reads a json dictionary and populates a single metadata object.

            Args:
                dict (dict): contains the uuid, name, type, value, properties
        """

        if self._capture is None:
            self._capture = data["capture"]

        super(MetadataRelationship, self).initialize_from_dict(data)


class MetadataRelationshipSet(BaseSet):
    """Base class for a collection of metadata"""

    def __init__(self, connection, project, capture, initialize_set=True):
        self._connection = connection
        self._project = project
        self._capture = capture

        self._set = None
        self._objclass = MetadataRelationship
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def capture(self):
        if isinstance(self._capture, str):
            return self._capture
        else:
            return self._capture.uuid

    @property
    def get_set_url(self):
        # Query the server and get the json
        return "v2/project/{0}/capture/{1}/metadata-relationship/".format(
            self._project.uuid, self.capture
        )

    def _new_obj_from_dict(self, data):
        """Creates a new metadata from data in the dictionary.

            Args:
                dict (dict): contains metadata properties uuid, name, type, value,

            Returns:
                metadata object

        """

        metadata = MetadataRelationship(self._connection, self._project, self._capture)
        metadata.initialize_from_dict(data)

        return metadata


class BulkMetadataRelationshipSet(MetadataRelationshipSet):
    """Base class for a collection of metadata"""

    def __init__(self, connection, project, initialize_set=True):
        self._connection = connection
        self._project = project
        self._objclass = MetadataRelationship
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    def bulk_create(self, metadataset=None):
        """
        Calls the REST API and bulk inserts objects onto the server using the local object's properties.
        """

        if metadataset:
            self._set = metadataset

        url = "project/{0}/metadata-relationship/".format(self._project.uuid)

        data = [
            {
                "label": obj.metadata,
                "label_value": obj.metadata_value,
                "capture": obj.capture,
            }
            for obj in self.objs
        ]

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)

        if err:
            raise Exception(err)

        # Populate each label from the server
        objs = []
        for obj in response_data:
            objs.append(self._new_obj_from_dict(obj))

        self._set.extend(objs)

        return objs

    @property
    def get_set_url(self):
        # Query the server and get the json
        return "project/{0}/metadata-relationship/".format(self._project.uuid)

    def _new_obj_from_dict(self, data):
        """Creates a new metadata from data in the dictionary.

            Args:
                dict (dict): contains metadata properties uuid, name, type, value,

            Returns:
                metadata object

        """
        metadata = MetadataRelationship(self._connection, self._project)
        metadata.initialize_from_dict(data)

        return metadata
