import sensiml.base.utility as utility
import logging
from sensiml.datamanager.base import Base, BaseSet


logger = logging.getLogger(__name__)


class LabelValue(object):
    Int = "integer"
    Float = "float"
    String = "string"


class LabelValue(Base):
    """Base class for a label object."""

    _fields = ["uuid", "value", "created_at", "last_modified"]

    def __init__(self, connection, project, label):
        """Initialize a metadata object.

            Args:
                connection
                project
                label
        """
        if label._metadata:
            raise Exception("Must be label not metadata")

        self._uuid = ""
        self._value = ""
        self._last_modified = ""
        self._created_at = ""
        self._connection = connection
        self._project = project
        self._label = label

    @property
    def uuid(self):
        """Auto generated unique identifier for the  label value object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def value(self):
        """The data type of the label value object"""
        return self._value

    @value.setter
    def value(self, value):
        """The data type of the label value object"""
        self._value = value

    @property
    def created_at(self):
        """The creatd time of the label value object"""
        return self._created_at

    @property
    def label(self):

        return self._label

    def insert(self):
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = "project/{0}/{1}/{2}/labelvalue/".format(
            self._project.uuid, self._label._label_or_metadata, self._label.uuid
        )
        data = {
            "value": self.value,
        }
        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data["uuid"]

        return response

    def update(self):
        """Calls the REST API and updates the object on the server."""
        url = "project/{0}/{1}/{2}/labelvalue/{3}".format(
            self._project.uuid,
            self._label._label_or_metadata,
            self._label.uuid,
            self.uuid,
        )

        data = {
            "value": self.value,
        }

        response = self._connection.request("put", url, data)
        response_data, err = utility.check_server_response(response)

        return response

    def delete(self):
        """Calls the REST API and deletes the object from the server."""
        url = "project/{0}/{1}/{2}/labelvalue/{3}".format(
            self._project.uuid,
            self._label._label_or_metadata,
            self._label.uuid,
            self.uuid,
        )
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return response

    def refresh(self):
        """Calls the REST API and populates the local object's properties from the server."""
        url = "project/{0}/{1}/{2}/labelvalue/{3}".format(
            self._project.uuid,
            self._label._label_or_metadata,
            self._label.uuid,
            self.uuid,
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def initialize_from_dict(self, data):
        """Reads a json dictionary and populates a single metadata object.

            Args:
                dict (dict): contains the uuid, value
        """
        self.uuid = data["uuid"]
        self.value = data["value"]
        self._data = data


class LabelValueSet(BaseSet):
    def __init__(self, connection, project, label, initialize_set=True):
        """Initialize a metadata object.

            Args:
                connection
                project
        """
        self._connection = connection
        self._project = project
        self._label = label
        self._set = None
        self._objclass = LabelValue
        self._attr_key = "value"

        if initialize_set:
            self.refresh()

    @property
    def label_values(self):
        return self.objs

    @property
    def get_set_url(self):
        return "project/{0}/{1}/{2}/labelvalue/".format(
            self._project.uuid, self._label._label_or_metadata, self._label.uuid
        )

    def _new_obj_from_dict(self, data):
        """Creates a new label from data in the dictionary.

            Args:
                data (dict): contains label_value properties value, uuid

            Returns:
                label object

        """

        obj = self._objclass(self._connection, self._project, self._label)
        obj.initialize_from_dict(data)
        return obj

    def __str__(self):
        s = ""
        if self._set:
            label = self._set[0]._label
            s = "LABEL\n"
            s += "\tname: " + str(label.name) + " uuid: " + str(label.uuid) + "\n"
            s += "LABEL VALUES\n"
            for lbv in self._set:
                s += "\tvalue: " + str(lbv.value) + " uuid:" + str(lbv.uuid) + "\n"

        return s
