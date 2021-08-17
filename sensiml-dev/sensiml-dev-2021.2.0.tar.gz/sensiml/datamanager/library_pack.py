import os
import json
from sensiml.base import utility
from sensiml.datamanager.base import Base, BaseSet


class LibraryPack(Base):
    """Base class for a library pack object"""

    _uuid = ""
    _name = ""
    _build_version = None
    _maintainer = ""
    _description = ""

    _fields = [
        "uuid",
        "name",
        "build_version",
        "description",
        "maintainer",
    ]

    _read_only_fields = ["uuid", "build_version"]

    def __init__(self, connection, uuid=None):
        self._connection = connection
        if uuid:
            self.uuid = uuid
            self.refresh()

    @property
    def base_url(self):
        return "library-pack/"

    @property
    def detail_url(self):
        return "library-pack/{uuid}/".format(uuid=self.uuid)

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def build_version(self):
        print(self._build_version)

    @build_version.setter
    def build_version(self, value):
        self._build_version = value

    @property
    def maintainer(self):
        return self._maintainer

    @maintainer.setter
    def maintainer(self, value):
        self._maintainer = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def refresh(self):
        """Calls the REST API and populates the local object properties from the server."""

        response = self._connection.request("get", self.detail_url)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def delete(self):
        """Calls the REST API and populates the local object properties from the server."""

        response = self._connection.request("delete", self.detail_url)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def insert(self):
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        response = self._connection.request("post", self.base_url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def update(self):
        """Calls the REST API and updates the object on the server."""

        data = self._to_representation()

        response = self._connection.request("put", self.detail_url, data)

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response


class LibraryPackSet(BaseSet):
    def __init__(self, connection, initialize_set=True):
        """Initialize a libraryPack object.

            Args:
                connection
        """
        self._connection = connection
        self._set = None
        self._objclass = LibraryPack
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def library_packs(self):
        return self.objs

    @property
    def get_set_url(self):
        return "library-pack/"

    def _new_obj_from_dict(self, data):
        """Creates a new object from the response data from the server.

            Args:
                data (dict): contains properties of the object

            Returns:
                obj of type _objclass

        """
        obj = self._objclass(self._connection)
        obj.initialize_from_dict(data)
        return obj
