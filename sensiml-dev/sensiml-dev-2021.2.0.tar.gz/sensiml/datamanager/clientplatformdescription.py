import os
import json
from pandas import DataFrame, Series

from sensiml.base import utility


class ArchitectureDescription(object):
    def __init__(self, name=""):
        self._name = name

    @property
    def name(self):
        return self._name


class CompilerDescription(object):
    """Base class for compiler object"""

    def __init__(self):
        self._compiler_version = ""
        self._name = ""
        self._uuid = ""

    @property
    def name(self):
        return self._name

    @property
    def uuid(self):
        return self._uuid

    @property
    def compiler_version(self):
        return self._compiler_version

    def initialize_from_dict(self, init_dict):
        self._uuid = init_dict.get("uuid", "")
        self._compiler_version = init_dict.get("compiler_version", "")
        self._name = init_dict.get("name", "")

    def __dict__(self):
        ret = {
            "Id": self.uuid,
            "Name": self.name,
            "Version": self.compiler_version,
        }
        return ret

    def __call__(self):
        pd_dict = self.__dict__()
        pseries = Series(pd_dict, index=pd_dict.keys())
        df = DataFrame()
        df = df.append(pseries, ignore_index=True)
        return df


class ProcessorDescription(object):
    """Base Class for Processor object"""

    def __init__(self):
        self._uuid = ""
        self._architecture = ArchitectureDescription()
        self._display_name = ""
        self._manufacturer = ""
        self._float_options = dict()
        self._profiling_enabled = False

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def float_options(self):
        return self._float_options

    @float_options.setter
    def float_options(self, value):
        self._float_options = value

    @property
    def profiling_enabled(self):
        return self._profiling_enabled

    @profiling_enabled.setter
    def profiling_enabled(self, value):
        self._profiling_enabled = value

    def initialize_from_dict(self, init_dict):
        self._uuid = init_dict.get("uuid", "")
        self.float_options = init_dict.get("float_options", list)
        self.manufacturer = init_dict.get("manufacturer", "")
        self.display_name = init_dict.get("display_name", "")
        self.architecture = ArchitectureDescription(
            name=init_dict.get("architecture", "")
        )
        self.profiling_enabled = init_dict.get("profiling_enabled", False)

    def __dict__(self):
        ret = {
            "Id": self.uuid,
            "Name": self.display_name,
            "Manufacturer": self.manufacturer,
            "Float Options": self.float_options,
            "Architecture": self.architecture,
            "Profiling Enabled": self.profiling_enabled,
        }
        return ret

    def __call__(self):
        pd_dict = self.__dict__()
        pseries = Series(pd_dict, index=pd_dict.keys())
        df = DataFrame()
        df = df.append(pseries, ignore_index=True)
        return df


class ClientPlatformDescription(object):
    """Base class for a PlatformDescription object"""

    def __init__(self, connection):
        self._connection = connection
        self._uuid = ""
        self._name = ""
        self._hardware_accelerators = dict()
        self._can_build_binary = False
        self._processors = list()
        self._platform_versions = list()
        self._description = ""
        self._supported_outputs = dict()
        self._supported_compilers = list()
        self._supported_source_drivers = dict()
        self._applications = dict()
        self._default_selections = dict()

    @property
    def name(self):
        return self._name

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def uuid(self):
        return self._uuid

    @property
    def id(self):
        return self._uuid

    @property
    def hardware_accelerators(self):
        return self._hardware_accelerators

    @property
    def can_build_binary(self):
        return self._can_build_binary

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def supported_compilers(self):
        return self._supported_compilers

    @property
    def supported_outputs(self):
        return self._supported_outputs

    @property
    def supported_source_drivers(self):
        return self._supported_source_drivers

    @property
    def processors(self):
        return self._processors

    @property
    def default_selections(self):
        return self._default_selections

    @property
    def platform_versions(self):
        return self._platform_versions

    @property
    def applications(self):
        return self._applications

    def get_by_processor_by_uuid(self, uuid):
        for p in self._processors:
            if str(p.uuid) == str(uuid):
                return p
        return None

    def get_config(
        self,
        test_data="",
        debug=False,
        target_processor=None,
        target_compiler=None,
        target_application=None,
        float_options=None,
        platform_version="",
    ):
        """ Generates a default configuration dictionary for downloading a knowledgepack using this platform progrmatically

            Args:
                test_data (str): name of test data file to load onto knowledge pack,
                debug (bool): Build option for knowledge pack. Debug mode will have extra printouts to help with debugging issues.

        """

        if self.supported_outputs:
            outputs = self.supported_outputs[0]
        else:
            outputs = ["serial"]

        config = {
            "target_platform": self.uuid,
            "test_data": test_data,
            "debug": debug,
            "output_options": outputs,
        }

        if target_application is None:
            config["application"] = list(self.applications.keys())[0]
        else:
            if target_application not in self.applications.keys():
                raise Exception("Invalid application")
            config["application"] = target_application

        if target_processor is None:
            config["target_processor"] = self.processors[0].uuid
        else:
            if sum([target_processor == x.uuid for x in self.processors]) != 1:
                raise Exception("Invalid target process")
            config["target_processor"] = target_processor

        if target_compiler is None:
            config["target_compiler"] = self.supported_compilers[0].uuid
        else:
            if sum([target_compiler == x.uuid for x in self.supported_compilers]) != 1:
                raise Exception("Invalid target compiler")

            config["target_compiler"] = target_compiler

        config["float_options"] = self.get_by_processor_by_uuid(
            config["target_processor"]
        ).float_options.get(self.default_selections.get("float", ""), "")

        if platform_version:
            if platform_version not in self.platform_versions:
                raise Exception("Invalid Platform Version")
        else:
            if self.platform_versions:
                platform_version = self.platform_versions[0]
        config["selected_platform_version"] = platform_version

        return config

    def refresh(self):
        """Calls the REST API and populates the local object properties from the server."""
        url = "platforms/{0}/".format(self.id)
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._uuid = response_data["uuid"]
            self._name = response_data["name"]
            self._hardware_accelerators = response_data["hardware_accelerators"]
            self._platform_versions = response_data["platform_versions"]
            self._description = response_data["description"]
            self._can_build_binary = response_data["can_build_binary"]
            self._supported_source_drivers = response_data["supported_source_drivers"]
            self._applications = response_data["applications"]
            self._default_selections = response_data.get("default_selections", {})
            self._processors = list()
            for processor in response_data.get("processors", []):
                test = set(self._processors)
                p = ProcessorDescription()
                p.initialize_from_dict(processor)
                if p not in test:
                    self._processors.append(p)

            self._supported_compilers = list()
            for compiler in response_data.get("supported_compilers", []):
                test = set(self._supported_compilers)
                c = CompilerDescription()
                c.initialize_from_dict(compiler)
                if c not in test:
                    self._supported_compilers.append(c)

    def initialize_from_dict(self, input_dictionary):
        """Populates a single transform object from a dictionary of properties from the server.
        """
        self._uuid = input_dictionary["uuid"]
        self._name = input_dictionary["name"]
        self._hardware_accelerators = input_dictionary["hardware_accelerators"]
        self._platform_versions = input_dictionary["platform_versions"]
        self._description = input_dictionary["description"]
        self._can_build_binary = input_dictionary["can_build_binary"]
        self._applications = input_dictionary["applications"]
        self._default_selections = input_dictionary.get("default_selections", {})
        self._supported_source_drivers = input_dictionary.get(
            "supported_source_drivers",
            {
                "Motion": [200, 100, 50, 25],
                "Audio": [16000],
                "Default": ["Motion", 100],
                "Custom": [],
            },
        )
        for processor in input_dictionary.get("processors", list()):
            proc = ProcessorDescription()
            proc.initialize_from_dict(processor)
            self._processors.append(proc)

        for compiler in input_dictionary.get("supported_compilers", list()):
            comp = CompilerDescription()
            comp.initialize_from_dict(compiler)
            self._supported_compilers.append(comp)

    def __dict__(self):
        def _get_unique_dict_list(in_dict):
            maps = map(dict, set(tuple(sorted(d.__dict__().items())) for d in in_dict))
            inner_ret = list()
            for m in maps:
                inner_ret.append(dict(m))
            return inner_ret

        ret = {
            "Id": self.uuid,
            "Name": self.name,
            "Hardware Accelerated": "Yes"
            if len(self.hardware_accelerators.items()) > 0
            else "No",
            "Processors Supported": self.processors,
            "Compilers Supported": self.supported_compilers,
            "Description": self.description,
        }
        return ret

    def __call__(self):
        pd_dict = self.__dict__()
        pseries = Series(pd_dict, index=pd_dict.keys())
        df = DataFrame()
        df = df.append(pseries, ignore_index=True)
        return df.drop(labels=["Id"], axis=1)
