""" SCBDATA module

This module contains the Scbdata class to manage files in the filesystem based on files that define patterns of paths for
each specific resource of the filesystem. At the creation, the information about the filesystem is collected to be used
in various ways.
    - The information of a file can be parsed given a specific path using the parse method or
    - For a collection of information the method get_path finds the paths that matches this information. Additionally,
      for data files, the information of the file is retrieved from a deployment id.

The main class can be run to perform one of the specific  options when the correct arguments are input.
To call the scbdata from the main class, users have four options

    - Get the path for a sepecific deployment id. Users can select a specific set of data mode and data levels or all
      as a default option
    - Find the information for a given path. This option is used when no deployment id is given and a input filename is provided

In fact the arguments taken from the main function are the following:
    -f,--definition_file: Path of the file containing the pattern descriptions. Default will look for local path in config folder
    -i,--input_file: Name of the file to be parsed. Only used when deployment id is not set.
    -d, --depid: Deployment id to be used to identify the path of the data.
The following options are used only when the plotting using the deployments ids is selected.
    -p, --data_product: Data product used for a specific deployment id. Default uses all available data levels (L0. L1 and L2)
    -m', --data_mode: Data mode used for a specific deployment id. Default uses all available data modes (rt, dt and dm)
    -t, --platform_type: Platform type used when plotting open deployments. None represents all available platforms. Default is glider.

"""
import os
import sys
import csv
import re
import json
import urllib
import urllib.request
from envbash import load_envbash
import argparse

__all__ = ["ScbData"]

##################
# Main Constants #
##################

path_script = os.path.dirname(os.path.abspath(__file__))
conf_path = os.path.join(path_script,'..','..','config')
fconf = os.path.join(conf_path,'env')
if os.path.isfile(fconf):
   try:
        load_envbash(fconf)
   except Exception as e:
        print('Environment variable is not set and failed to parse configuration file (' + fconf + ')')

DATA_FILESYSTEM_DEFINITION_FILE = os.environ['DATA_FILESYSTEM_DEFINITION_FILE'] if 'DATA_FILESYSTEM_DEFINITION_FILE' in os.environ else os.path.join(conf_path,'filesystem.def')
COLUMN_PATH_PATTERN_LABEL = os.environ['COLUMN_PATH_PATTERN_LABEL'] if 'COLUMN_PATH_PATTERN_LABEL' in os.environ else "path_pattern"
REGEX_KEY_EQUAL = '(.*)<<(.*)'

MANAGEMENT_API_REQUEST_BASE    = "http://management.ws.socib.es/rest_services/"
MANAGEMENT_API_REQUEST         = MANAGEMENT_API_REQUEST_BASE + "{}"
MANAGEMENT_FIELDS_RESULTS      = {
    "deployments": {
        "id": "deployment_id",
        "name": "deployment_name",
        "code": "deployment_code",
        "initial_date": "deployment_initial_date",
        "end_date": "deployment_end_date"
    },
    "instruments": {
        "id": "instrument_id",
        "name": "instrument_name",
        "model": "instrument_model"
    },
    "instrument_types": {},   # Used to check the platform type. Harcoded due to the mess with instrument and platform types
    "platforms": {
        "name": "platform_name",
        "type": "platform_type"
    },
    "cruises": {
        "name": "cruise_name"
    }
}
PLATFORM_TYPE_MAPPING = {
    "Research Vessel": "vessel",
    "Glider": "glider"
}

COLUMN_PATH_TYPE_LABEL="path_type"
DATAPRODUCT_LABELS = {
    "ori": "ori-{}",
    "raw": "raw-{}",
    "l0": "data-opendap",
    "l1": "data-opendap",
    "l2": "data-opendap",
    "figure": "figure-data",
    "figjson": "figure-json",
    "kmz": "data-kmz"
}

class ScbData(object):
    """
    The ScbData class is used to parse file information and get path from file information.

    Attributes:
        fsdef (str): Path of the pattern description file
        self.path_info (dict): Contains information collected for a given path
        self.patterns (dict): Records the information from fsdef. It contains four fields.
            "source": pattern as read in the file
            "row": information of the lines as read from the file in the form of dictionary
            "pattern_value": Same as source but replacing the information when it correspond to a particular value
            "regex": Same as source but replacing all attributes by (.*?) for generic regex search

    Raise:
        Exception: When description file does not exist

    """

    def __init__(self, fsdef=DATA_FILESYSTEM_DEFINITION_FILE):
        """
        Reads the description file and loads the information in the attributes

        :param fsdef: Path of the pattern description file
        :type fsdef: str
        """
        if not fsdef:
            fsdef = DATA_FILESYSTEM_DEFINITION_FILE
        if not os.path.isfile(fsdef):
            raise Exception("Filesystem definition file does not exist: " + fsdef)

        with open(fsdef) as csv_file:
            self.fsdef = csv.DictReader((line for line in csv_file if not line.startswith('#') and not line.isspace()), delimiter=',')
            self.path_info = {}

            self.patterns = {}
            self.pattern_sort = []

            for row in self.fsdef:
                pattern = row[COLUMN_PATH_PATTERN_LABEL]
                pattern_key = pattern
                pattern_value = pattern
                pattern_regex = pattern
                for pat in re.findall('\{(.*?)\}',pattern):
                    pattern_regex = pattern_regex.replace( "{" + pat + "}", "(.*?)")
                    if re.match(REGEX_KEY_EQUAL, pat):
                        key_value = re.search(REGEX_KEY_EQUAL,pat).group(2)
                        pattern_key = pattern_key.replace( "{" + pat + "}", key_value)
                        pattern_value = pattern_value.replace( "{" + pat + "}", key_value)
                    else:
                        pattern_key = pattern_key.replace( "{" + pat + "}", "(.*?)")

                self.patterns[pattern_key] = {"source": pattern, "row": row, "pattern_value": pattern_value, "regex": pattern_regex}
                self.pattern_sort.append(pattern_key)

    def get_pattern(self, path):
        """
        Finds the pattern that best matches a path among all collected in the description file

        :param path: Path to be checked
        :type path: str
        :return: found pattern
        :rtype: str
        """
        found_pattern = ""
        for pattern_key in self.pattern_sort:
            if re.match(pattern_key, path):
                found_pattern = self.patterns[pattern_key]

        return found_pattern

    def parse(self, path, pattern={}):
        """

        :param path: Path to be checked and of which information should be parsed
        :type path: str
        :param pattern: Specific pattern to be compared. Default will use get_pattern to find the appropriate one.
                        Pattern is a dictionary that must contain source, row and pattern values. Same as self.patterns
        :type pattern: dict
        :return: Dictionary containing the collected information
        :rtype: dict
        """
        if not pattern:
            pattern = self.get_pattern(path)

        pattern_keys_arr = re.findall('\{(.*?)\}', pattern["source"])
        pattern_values_arr = re.findall(pattern["regex"], path)
        pattern_values_arr = pattern_values_arr[0]

        self.path_info = {}
        for idx, key in enumerate(pattern_keys_arr):
            if re.match(REGEX_KEY_EQUAL, key):
                reg_res = re.search(REGEX_KEY_EQUAL, key)
                key_value = reg_res.group(2)
                key_name = reg_res.group(1)
                self.__add_key__(key_name, key_value, add_key=True)
            else:
                key_value = pattern_values_arr[idx]
                key_name_str = key
                if not key_name_str:
                    print("Error when checking key " + key)
                    continue # TODO: or break?
                key_name_list = key_name_str.split("|")
                key_name = key_name_list[0]
                key_name_list.pop(0)
                key_value = self.__convert_key_(key_value, key_name_list, invert=True)
                self.__add_key__(key_name, key_value, add_key=True)

        self.__fill_header_info_(pattern["row"])
        self.__fill_deployment_info_()

        return self.path_info

    def get_path_info(self, deployment_id, data_mode="rt", data_product="L1"):
        """
        Gets the path information of the input deployment id for the input data mode and product

        :param deployment_id: Deployment id
        :type deployment_id: int or str
        :param data_mode: Data mode to be added to the information
        :type data_mode: str
        :param data_product: Data product to be added to the information
        :type data_product: str
        :return:
        """
        if data_mode.lower() not in ["rt", "dt", "dm"]:
            raise Exception("Data mode " + data_mode + " is not recognized")
        if data_product.lower() not in DATAPRODUCT_LABELS:
            raise Exception("Data mode " + data_product + " is not recognized")
        data_mode = data_mode.lower()
        data_product_label = DATAPRODUCT_LABELS[data_product].format(data_mode)
        #data_product = data_product.lower() if data_mode != "dm" else data_product.lower() + "_corr"
        path_info = {COLUMN_PATH_TYPE_LABEL: data_product_label, "data_mode": data_mode, "data_level": data_product}

        request_url = MANAGEMENT_API_REQUEST.format("deployments") + "/" + str(deployment_id)
        deployment_info = self.__get_management_results__(request_url, add_key=False)
        if "deployment_id" not in deployment_info:
            return path_info

        path_info = {**path_info, **deployment_info}

        if "platform_type" in path_info:
            if path_info["platform_type"] in PLATFORM_TYPE_MAPPING:
                path_info["platform_type"] = PLATFORM_TYPE_MAPPING[path_info["platform_type"]]

        return path_info

    def get_path(self, path_info_list_or_deployment_id, data_mode_list=["rt", "dt", "dm"], data_product_list=["l0", "l1", "l2"]):
        """
        Get the list of paths for the input information

        :param path_info_list_or_deployment_id: A dictionary, list of dictionaries containing the information of the path. A deployment id could be given
        :type path_info_list_or_deployment_id: str, int, dict or list
        :param data_mode_list: List of data modes
        :type data_mode_list: list
        :param data_product_list: List of data products
        :type data_product_list: list
        :return:
        """
        self.path_info = {}
        if not isinstance(path_info_list_or_deployment_id, dict):  # This is the case of a deployment id
            path_info_list = []
            if not data_mode_list:
                data_mode_list = ["rt", "dt", "dm"]
            if not data_product_list:
                data_product_list = ["l0", "l1", "l2"]

            # Convert to list if input is a string
            if not isinstance(data_mode_list, list):
                data_mode_list = [data_mode_list]
            if not isinstance(data_product_list, list):
                data_product_list = [data_product_list]

            for data_mode in data_mode_list:
                for data_product in data_product_list:
                    current_path_info = self.get_path_info(path_info_list_or_deployment_id, data_mode=data_mode, data_product=data_product)
                    if current_path_info:
                        path_info_list.append(current_path_info)
        else:
            path_info_list = path_info_list_or_deployment_id if isinstance(path_info_list_or_deployment_id, list) else [path_info_list_or_deployment_id]

        found_path_list = []
        for path_info in path_info_list:
            current_found_path = self.__build_path_from_pattern__(path_info)
            if current_path_info:
                found_path_list.append(current_found_path)

        return found_path_list

    def __build_path_from_pattern__(self, path_info):
        """
        Checks all the available patterns in self.patterns, gets the best match for the path_info and builds the path

        :param path_info: Information of the path
        :type path_info: dict
        :return: Final path that matches path_info
        :rtype: str
        """
        found_path = ""
        for pattern_key in self.pattern_sort:
            pattern = self.patterns[pattern_key]

            # First check if the header info exists for this pattern
            if not self.__is_in_header_info(path_info, pattern["row"]):
                continue

            # Check if all the keys of the current pattern are in path_info
            pattern_keys_arr = re.findall('\{(.*?)\}', pattern["source"])
            current_path = pattern["source"]
            all_good = True
            for idx, key in enumerate(pattern_keys_arr):
                if re.match(REGEX_KEY_EQUAL, key):
                    reg_res = re.search(REGEX_KEY_EQUAL, key)
                    key_value = reg_res.group(2)
                    key_name_str = reg_res.group(1)
                else:
                    key_name_str = key
                    key_value = ""
                    if not key_name_str:
                        print("Error when checking key " + key)
                        break
                key_name_list = key_name_str.split("|")
                key_name = key_name_list[0]
                key_name = key_name.lower()
                if key_name not in path_info:
                    # That means that the key in the pattern is not recorded in the info of the deployment
                    all_good = False
                    break
                key_name_list.pop(0)
                path_info_value = self.__convert_key_(path_info[key_name], key_name_list, invert=False)
                if key_value and path_info_value != key_value:
                    # This case means that we have a pattern <<< with a value and does not match the value of the deployment
                    all_good = False
                    break
                current_path = current_path.replace("{" + key + "}", str(path_info_value))

            if all_good:
                found_path = current_path

        return found_path

    def __is_in_header_info(self, path_info, header_info):
        """
        Checks if the information of the path matches the information of the row using the header lables

        :param path_info: Path info
        :type path_info: dict
        :param header_info: Information of a specific row for the pattern that is being checked
        :type header_info: dict
        :return: True if it matches False otherwise
        :rtype: bool
        """
        for key in header_info:
            if key == COLUMN_PATH_PATTERN_LABEL:
                continue
            if not header_info[key]:
                continue
            if key not in path_info:
                return False
            if path_info[key] != header_info[key]:
                return False
        return True

    def __add_key__(self, key_name, key_value, add_key=True):
        """
        Gets a dictionary with the information of the checked key if it is succeptible to be added to self.path_info.
        It can also be added to self.path_info if add_key is set to True

        :param key_name: Name of an attribute to be checked
        :type key_name: str
        :param key_value: Value of an attribute to be checked
        :type key_value: str
        :param add_key: Define if the key is added to self.path_info
        :type add_key: bool
        :return: Dictionary containing the added key
        :rtype: dict
        """
        """ TODO doc - should check if keyword exist and manage conflicts"""
        path_info = {}
        if key_name in self.path_info:
            # TODO: the conflic is usually for dates since we may have the entire deployment date or just YYYY.
            #           Not sure how this can be handle but for now, we just look at the length of the string
            if isinstance(key_value, str) and len(key_value) < len(self.path_info[key_name]):
                return {}
            path_info[key_name.lower()] = key_value
            if add_key:
                self.path_info[key_name.lower()] = key_value
        else:
            path_info[key_name.lower()] = key_value
            if add_key:
                self.path_info[key_name.lower()] = key_value

        return path_info

    def __fill_header_info_(self, row):
        """
        Used to get the information of a specific row using the header values as the attribute names. It also adds the key
        to self.path_info using the __add_key__ method. When a list is used as an input it uses the header of the
        definition file that is loaded at initialization.

        :param row: Dictionary or list with the information of a specific row of the file definition .
        :rtype row: dict or list
        :return: Returns a dictionary with the info of the row.
        :rtype: dict
        """
        path_info = {}
        if isinstance(row, list):
            for idx, field in enumerate(self.fsdef.fieldnames):
                current_path_info = self.__add_key__(field, row[idx], add_key=True)
                path_info = {**path_info, **current_path_info}
        elif isinstance(row, dict):
            for field in row:
                current_path_info = self.__add_key__(field, row[field], add_key=True)
                path_info = {**path_info, **current_path_info}
        else:
            print("Error, input row must be of type list or dict")

        return path_info

    def __fill_deployment_info_(self):
        """
        Creates the request for the management webservice and calls self.__get_management_results__ to perform the request

        :return: the information of the request in the form of a dictionary
        :rtype: dict
        """
        request_url = MANAGEMENT_API_REQUEST.format("deployments")
        request_url = request_url + "?" + urllib.parse.urlencode(self.path_info)
        path_info = self.__get_management_results__(request_url)
        return path_info

    def __get_management_results__(self, request_url, add_key=True):
        """
        Performs the request of an url and recursively call uri from the result when specified. Specifications of
        keys to be called are in the MANAGEMENT_FIELDS_RESULTS dictionary.

        :param request_url: query
        :type request_url: str
        :param add_key: Indicates if the found information is added to self.path_info when calling __add_key__
        :return: the information of the request in the form of a dictionary
        :rtype: dict
        """
        path_info = {}
        if request_url is None:
            return {}
        if not request_url.startswith(MANAGEMENT_API_REQUEST_BASE):
            print("Error, request should be of type " + MANAGEMENT_API_REQUEST_BASE)
            return {}
        request_type = request_url[len(MANAGEMENT_API_REQUEST_BASE):]
        request_type = request_type.split("/")[0]
        request_type = request_type.split("?")[0]

        if request_type not in MANAGEMENT_FIELDS_RESULTS:
            print("Warning, request of type " + request_type + " are not mapped")
            return {}
        mapping_dict = MANAGEMENT_FIELDS_RESULTS[request_type]

        weburl = urllib.request.urlopen(request_url)
        if weburl.getcode() != 200:
            print("Error, could not extract platform from api call: " + request_url)
            return []

        try:
            request_result_str = weburl.read().decode('utf-8')
            request_result = json.loads(request_result_str)
            if "count" in request_result:  # in this case we assume that there could be more than one result. Otherwise, no
                request_count = request_result["count"]
                if request_count == 0:
                    print("No additional information for the current information")
                    return {}
                elif request_count > 1:
                    print("Too many deployments in the api response for the current information")
                    return {}
                request_result_dict = request_result["results"][0]
            else:
                request_result_dict = request_result

            for field in request_result_dict:
                # Hard coded the way to treat platform type until we clarify what is instrument_type and platform_type
                if field == "type" and request_type == "platforms":
                    platform_type_value = self.__treat_platform_type_case__(request_result_dict["type"])
                    current_path_info = self.__add_key__("platform_type", platform_type_value, add_key=add_key)
                elif field in mapping_dict:
                    current_field = mapping_dict[field]
                    current_path_info = self.__add_key__(current_field, request_result_dict[field], add_key=add_key)
                elif field in MANAGEMENT_FIELDS_RESULTS or field + "s" in MANAGEMENT_FIELDS_RESULTS:
                    if request_result_dict[field] is not None:
                        current_path_info = self.__get_management_results__(request_result_dict[field])
                else:
                    current_field = request_type if request_type[len(request_type)-1] != "s" else request_type[:len(request_type)-1]
                    current_field = current_field + "_" + field
                    current_path_info = self.__add_key__(current_field, request_result_dict[field], add_key=add_key)
                path_info = {**path_info, **current_path_info}

        except Exception as e:
            print("Error, when performing request parsing for requests " + request_url + ": " + e)

        return path_info

    # TODO: remove this when ws.management returns platform info
    def __treat_platform_type_case__(self, field_uri):
        """
        This treats the case of platform types. There is a confusion of platform and instrument types in the
        instrumentation database and this function is a harcoded fix to bypass the problem.

        :param field_uri: URI to the platform information using the manatment webservice
        :return: platform type string
        :rtype: str
        """
        current_path_info = self.__get_management_results__(field_uri)
        instrument_type_name_label = "instrument_type_name"
        if instrument_type_name_label not in current_path_info:
            return ""
        if current_path_info[instrument_type_name_label] == "Glider":
            return "glider"
        elif current_path_info[instrument_type_name_label] == "Research Vessel":
            return "vessel"
        elif "parent_type" in current_path_info and current_path_info["parent_type"] is not None:
            return self.__treat_platform_type_case__(current_path_info["parent_type"])
        else:
            return ""

    def __convert_key_(self, key_value, convert_list, invert=False):
        """
        Converts the value of the key using the conversion definitions in the input list
            - l: lower case
            - u: upper case
            - rxy: replaces character x by y
            - date formats

        :param key_value: Value of the key
        :type key_value: str
        :param convert_list: List of conversions
        :type convert_list: list
        :param invert: Defines the direction of the conversion. If set to True, the conversion is inverted and lower becomes upper for instance.
        :type invert: bool
        :return: the new value of the key
        :rtype: str
        """
        key_value_result = key_value

        for c in convert_list:
            if c == "l":  # to lower case
                key_value_result = key_value_result.lower() if not invert else key_value_result.upper()
            elif c == "u": # to upperer case
                key_value_result = key_value_result.upper() if not invert else key_value_result.lower()
            elif c[0] == "r": # replace character
                c1 = c[1] if not invert else c[2]
                c2 = c[2] if not invert else c[1]
                key_value_result = key_value_result.replace(c1, c2)
            # We assume for the following date conversion that input dates will be in the same form as in instrumentation db (e.g. 2020-07-29 09:00:00+00)
            elif c.upper() =="YYYY":
                key_value_result = key_value_result[0:4] if not invert else key_value_result
            elif c.upper() =="MM":
                key_value_result = key_value_result[5:7] if not invert else key_value_result
            elif c.upper() =="DD":
                key_value_result = key_value_result[8:10] if not invert else key_value_result
            elif c.upper() =="YYYY-MM":
                key_value_result = key_value_result[0:7] if not invert else key_value_result
            elif c.upper() =="MM-YYYY":
                key_value_result = key_value_result[5:7] + key_value_result[0:4] if not invert else key_value_result
            elif c.upper() =="YYYY-MM-DD":
                key_value_result = key_value_result[0:10] if not invert else key_value_result
            elif c.upper() =="YYYYMMDD":
                key_value_result = key_value_result[0:4] + key_value_result[5:7] + key_value_result[8:10] if not invert else key_value_result
            elif c.upper() =="YYYYMM":
                key_value_result = key_value_result[0:4] + key_value_result[5:7] if not invert else key_value_result
            elif c.upper() =="MMYYYY":
                key_value_result = key_value_result[5:7] + key_value_result[0:4] if not invert else key_value_result
            else:
                print ("Warning, unkwon conversion {} for {} value".format(c,key_value))

        return key_value_result

#################
# Main Function #
#################

# Main function to run module from command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create plots from input file')
    parser.add_argument('-d', '--depid', dest='dep_id', nargs="*",
                        help='Deployment id to be used to identify the path of the data.')
    parser.add_argument('-p', '--data_product', dest='data_product', nargs="*", default="",
                        help='Data product used to find the path for a specific deployment id. Default is l0 and l1.')
    parser.add_argument('-m', '--data_mode', dest='data_mode', nargs="*", default="",
                        help='Data mode used when calling plots for a specific deployment id. Default is rt, dt and dm.')
    parser.add_argument('-i', '--input_file', dest='fin', nargs=1,
                        help='Path of the file to parse. Only used when deployment id is not set.')
    parser.add_argument('-f', '--defintion_file', dest='fsdef', nargs=1, default=DATA_FILESYSTEM_DEFINITION_FILE,
                        help='Path of the definition file.')
    args = parser.parse_args()

    fsdef = args.fsdef[0] if "fdef" in args and args.fsdef is not None else DATA_FILESYSTEM_DEFINITION_FILE
    print("Pattern definition file: " + fsdef)
    scbdata_parse = ScbData(fsdef=fsdef)

    if "dep_id" in args and args.dep_id is not None:
        data_mode = args.data_mode
        data_product = args.data_product
        path_info = scbdata_parse.get_path(args.dep_id[0], data_mode_list=data_mode, data_product_list=data_product)
        if not path_info:
            print("No files identified for this deployment")
        else:
            print("Files matching deployment " + str(args.dep_id[0]))
            for pi in path_info:
                print("      - " + pi)
        sys.exit(0)


    ##########################
    # If we get here is that we used a specific file instead of deployment ids
    if "fin" not in args or args.fin is None:
        raise Exception("Input file is required (Use -i option)")
    fin = args.fin[0]

    if not os.path.isfile(fin):
        raise Exception("Input file does not exist (" + fin + ")")

    try:
        found_patterns = scbdata_parse.parse(fin)
        if found_patterns:
            print(found_patterns)
        else:
            print("No pattern found")
    except Exception as e:
        raise Exception(e)
        sys.exit(1)

    sys.exit(0)