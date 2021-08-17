from uuid import UUID
import sensiml.base.utility as utility
from sensiml.datamanager.base import Base, BaseSet


class Segmenter(Base):
    """Base class for a segmenter object."""

    _data = None
    _fields = [
        "uuid",
        "name",
        "parameters",
        "preprocess",
        "custom",
        "parent",
        "last_modified",
        "created_at",
    ]
    _field_map = {
        "uuid": "id",
    }

    def __init__(self, connection, project):
        """Initialize a metadata object.

            Args:
                connection
                project
        """
        self._uuid = ""
        self._name = ""
        self._parameters = None
        self._preprocess = None
        self._custom = True
        self._parent = None
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
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def preprocess(self):
        return self._preprocess

    @preprocess.setter
    def preprocess(self, value):
        self._preprocess = value

    @property
    def custom(self):
        return self._custom

    @custom.setter
    def custom(self, value):
        if not isinstance(value, bool):
            raise ValueError("custom must be a bool.")

        self._custom = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is None:
            self._parent = None
        else:
            self._parent = UUID(value)

    def insert(self):
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = "project/{0}/segmenter/".format(self._project.uuid)

        data = self._to_representation()

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)

        if err is False:
            self.uuid = response_data["id"]

        return response

    def update(self):
        """Calls the REST API and updates the object on the server."""
        url = "project/{0}/segmenter/{1}/".format(self._project.uuid, self.uuid)

        data = self._to_representation()

        response = self._connection.request("put", url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def delete(self):
        """Calls the REST API and deletes the object from the server."""
        url = "project/{0}/segmenter/{1}/".format(self._project.uuid, self.uuid)
        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)

        return response

    def refresh(self):
        """Calls the REST API and populates the local object's properties from the server."""
        url = "project/{0}/segmenter/{1}/".format(self._project.uuid, self.uuid)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response


class SegmenterSet(BaseSet):
    """Base class for a segmenter object."""

    def __init__(self, connection, project, initialize_set=True):
        self._connection = connection
        self._project = project
        self._set = None
        self._objclass = Segmenter
        self._attr_key = "name"

        if initialize_set:
            self.refresh()

    @property
    def get_set_url(self):
        return "project/{0}/segmenter/".format(self._project.uuid)
