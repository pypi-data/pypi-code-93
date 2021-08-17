import sensiml.base.utility as utility
from pandas import DataFrame


class Base(object):
    """
    Base class for all datamanger objects. 

    _data (dict): stores the data response from the server
    _fields (list): list of fields that the model has
    _read_only_fields (list): list of fields that are read only
    _field_map (dict): as some fields are named differently from the server
        we use a field map dict for backwards compantibility the field map 
        is a dictionary with the following format
        {'client_field_name':'server_field_name'}

    """

    _data = None
    _fields = []
    _read_only_fields = ["uuid", "created_at", "last_modified"]
    _field_map = {}

    def __init__(self, connection, **kwrags):
        """
        All objects take a connection first, followed by some kwargs
        """
        self._connection = connection

    @property
    def base_url(self):
        """ Overwrite this property in the subclass for its base url """

        return ""

    @property
    def detail_url(self):
        """ Overwrite this property in the subclass for its base url """

        return ""

    @property
    def fields(self):
        return self._fields

    @property
    def data(self):
        """
        Returns the server response data object or 
        generates the data object from locally stored 
        properties
        """
        if self._data is None:
            return [
                getattr(self, field)
                for field in self.fields.keys()
                if hasattr(self, field)
            ]

        return self._data

    def _to_representation(self):
        """
        converts the object into a representation for insert/update
        rest calls
        """
        return {
            self._field_map.get(field, field): getattr(self, field)
            for field in self.fields
            if hasattr(self, field) and field not in self._read_only_fields
        }

    def initialize_from_dict(self, data):
        """Reads a json dictionary and populates a single object.
           stores the results in _data as well

            Args:
                data (dict): server response data object
        """

        for field in self._fields:
            if hasattr(self, field):
                mapped_field = self._field_map.get(field, field)
                setattr(self, field, data.get(mapped_field, None))

        self._data = data

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

    def insert(self, path=None):
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        if path:
            response = self._connection.file_request(self.base_url, path, data, "rb")
        else:
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


class BaseSet(object):
    def __init__(self, connection, initialize_set=True, **kwargs):
        """Initialize a set object to store base objects

            _set (list): a list of objects that are part of the set
            _objclass (Class): the class obj stored in the set
            _attr_key (str): a key used to build out the to_dict

            Args:
                connection (connection) connection object to server
                initialze_set (bool) Default is True. If true will build the 
                 set of objects. 
        """

        self._connection = connection
        self._set = None
        self._objclass = Base
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def get_set_url(self):
        """
          replace this with the url to call to pull down the set objects
        """
        pass

    @property
    def objs(self):
        if self._set is None:
            self._set = self.get_set()

        return self._set

    def append(self, obj):
        if self._set is None:
            self._set = [obj]

        self._set.append(obj)

    def to_dict(self, key=None):
        if key is None:
            key = self._attr_key

        return {getattr(k, key): k for k in self.objs}

    def to_dataframe(self):
        return DataFrame([obj.data for obj in self.objs])

    def refresh(self):
        self._set = self.get_set()

    def get_set(self):
        """Calls the REST API to get the set of objects from the server."""
        url = self.get_set_url

        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err:
            raise Exception(err)

        # Populate each label from the server
        objs = []
        for obj in response_data:
            objs.append(self._new_obj_from_dict(obj))

        return objs

    def _new_obj_from_dict(self, data):
        """Creates a new object from the response data from the server.

            Args:
                data (dict): contains properties of the object

            Returns:
                obj of type _objclass

        """
        obj = self._objclass(self._connection, project=self._project)
        obj.initialize_from_dict(data)
        return obj
