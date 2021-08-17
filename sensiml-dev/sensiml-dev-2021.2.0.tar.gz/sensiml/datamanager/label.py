import json
from numpy import float64, int64
import sensiml.base.utility as utility
import logging
import time
from sensiml.datamanager.base import Base, BaseSet


logger = logging.getLogger(__name__)


class LabelType(object):
    Int = "integer"
    Float = "float"
    String = "string"


class Label(Base):
    """Base class for a label object."""

    _fields = [
        "uuid",
        "name",
        "value_type",
        "is_dropdown",
        "last_modified",
        "created_at",
    ]

    _field_map = {"value_type": "type"}

    def __init__(self, connection, project):
        """Initialize a metadata object.

            Args:
                connection
                project
        """
        self._uuid = ""
        self._name = ""
        self._value_type = "string"
        self._is_dropdown = False
        self._last_modified = ""
        self._created_at = ""
        self._connection = connection
        self._project = project

    @property
    def uuid(self):
        """Auto generated unique identifier for the metadata object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        """The name property of the metadata object"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def value_type(self):
        """The data type of the metadata object"""
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        if value not in ["string", "int", "float"]:
            raise Exception("Invalid value type")
        self._value_type = value

    @property
    def _label_or_metadata(self):
        return "label"

    @property
    def _metadata(self):
        return False

    @property
    def is_dropdown(self):
        return self._is_dropdown

    @is_dropdown.setter
    def is_dropdown(self, value):
        if not isinstance(value, bool):
            raise Exception("Invalid Value")

        self._is_dropdown = value

    def insert(self):
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = "project/{0}/{1}/".format(self._project.uuid, self._label_or_metadata,)
        data = self._to_representation()
        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self):
        """Calls the REST API and updates the object on the server."""
        url = "project/{0}/{1}/{2}/".format(
            self._project.uuid, self._label_or_metadata, self.uuid
        )

        data = self._to_representation()
        response = self._connection.request("put", url, data)
        response_data, err = utility.check_server_response(response)

        return response

    def delete(self):
        """Calls the REST API and deletes the object from the server."""
        url = "project/{0}/{1}/{2}/".format(
            self._project.uuid, self._label_or_metadata, self.uuid
        )
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return response

    def refresh(self):
        """Calls the REST API and populates the local object's properties from the server."""
        url = "project/{0}/{1}/{2}/".format(
            self._project.uuid, self._label_or_metadata, self.uuid
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def initialize_from_dict(self, data):
        """Reads a json dictionary and populates a single metadata object.

            Args:
                data (dict): contains the uuid, name, type
        """
        self.uuid = data["uuid"]
        self.name = data["name"]
        if data["type"] == LabelType.Int:
            self.value_type = int(data["type"])
        elif data["type"] == LabelType.Float:
            self.value_type = float(data["type"])
        else:
            self.value_type = data["type"]

        self._data = data


class LabelSet(BaseSet):
    def __init__(self, connection, project, initialize_set=True):
        """Initialize a metadata object.

            Args:
                connection
                project
        """
        self._connection = connection
        self._project = project
        self._set = None
        self._objclass = Label
        self._attr_key = "name"

        if initialize_set:
            self.refresh()

    @property
    def labels(self):
        return self.objs

    @property
    def get_set_url(self):
        return "project/{0}/label/".format(self._project.uuid)
