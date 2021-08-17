import os
import json
from sensiml.base import utility
from sensiml.datamanager.base import Base, BaseSet


class CustomFunction(Base):
    """Base class for a transform object"""

    _uuid = ""
    _type = None
    _name = None
    _description = ""
    _input_contract = ""
    _output_contract = ""
    _subtype = ""
    _path = ""
    _unit_tests = None
    _logs = ""
    _task_result = ""
    _c_function_name = ""
    _library_pack = ""

    _fields = [
        "uuid",
        "name",
        "transform_type",
        "description",
        "input_contract",
        "output_contract",
        "subtype",
        "unit_tests",
        "logs",
        "task_results",
        "c_function_name",
        "library_pack",
        "task_status",
    ]

    _read_only_fields = [
        "uuid",
        "created_at",
        "last_modified",
        "logs",
        "task_result",
        "task_status",
    ]

    _field_map = {"transform_type": "type"}

    def __init__(self, connection, uuid=None):
        self._connection = connection
        if uuid:
            self.uuid = uuid
            self.refresh()

    @property
    def base_url(self):
        return "custom-transform/"

    @property
    def detail_url(self):
        return "custom-transform/{uuid}".format(uuid=self.uuid)

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, value):
        self._subtype = value

    @property
    def transform_type(self):
        return "Feature Generator"

    @transform_type.setter
    def transform_type(self, value):
        self._transform_type = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def c_function_name(self):
        return self._c_function_name

    @c_function_name.setter
    def c_function_name(self, value):
        self._c_function_name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def input_contract(self):
        return json.dumps(self._input_contract)

    @input_contract.setter
    def input_contract(self, value):
        self._input_contract = value

    @property
    def output_contract(self):
        return json.dumps(self._output_contract)

    @output_contract.setter
    def output_contract(self, value):
        self._output_contract = value

    @property
    def unit_tests(self):
        return json.dumps(self._unit_tests)

    @unit_tests.setter
    def unit_tests(self, value):
        self._unit_tests = value

    @property
    def logs(self):
        print(self._logs)

    @logs.setter
    def logs(self, value):
        self._logs = value

    @property
    def task_results(self):
        return self._task_results

    @task_results.setter
    def task_results(self, value):
        self._task_results = value

    @property
    def library_pack(self):
        return self._library_pack

    @library_pack.setter
    def library_pack(self, value):
        self._library_pack = value

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

    def insert(self, path):
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        response = self._connection.file_request(self.base_url, path, data, "rb")

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def update(self, path):
        """Calls the REST API to insert a new object."""

        data = self._to_representation()

        data.pop("library_pack")

        response = self._connection.file_request(
            self.detail_url, path, data, "rb", "put"
        )

        response_data, err = utility.check_server_response(response)

        if err is False:
            self.initialize_from_dict(response_data)

        return response


class CustomFunctionSet(BaseSet):
    def __init__(self, connection, initialize_set=True):
        """Initialize a custom transform set object.

            Args:
                connection
        """
        self._connection = connection
        self._set = None
        self._objclass = CustomFunction
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def library_packs(self):
        return self.objs

    @property
    def get_set_url(self):
        return "custom-transform/"

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
