import json
from pandas import DataFrame, Series

from sensiml.datamanager.clientplatformdescription import ClientPlatformDescription
import sensiml.base.utility as utility


class ClientPlatformDescriptions:
    """Base class for a collection of functions"""

    def __init__(self, connection):
        self._connection = connection
        self.build_platform_descriptions()

    def __getitem__(self, index):
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()

        df = self()
        for p in self.platform_list:
            if index not in df.index:
                continue
            if df.loc[index].equals(p().loc[0]):
                return p
        return None

    def refresh(self):
        self.build_platform_descriptions()

    def build_platform_descriptions(self):
        """Populates the platform_list property from the server."""
        self.platform_list = []
        self.platform_dict = {}

        platforms = self.get_platforms()
        for platform in platforms:
            self.platform_dict["{}".format(platform.name)] = platform
            self.platform_list.append(platform)

    def get_platform_by_name(self, name):
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()
        return self.platform_dict.get(name, None)

    def get_platform_by_id(self, id):
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()

        return next((x for x in self.platform_list if x.uuid == id), None)

    def get_platform_by_uuid(self, uuid):
        return self.get_platform_by_id(uuid)

    def _new_platform_description_from_dict(self, data):
        """Creates and populates a platform from a set of properties.

            Args:
                data (dict): contains properties of a platform

            Returns:
                platform
        """
        platform = ClientPlatformDescription(self._connection)
        platform.initialize_from_dict(data)
        return platform

    def get_platforms(self, function_type=""):
        """Gets all functions as function objects.

            Args:
                function_type (optional[str]): type of function to retrieve

            Returns:
                list of functions
        """
        url = "platforms/v2"
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        platformDescriptions = list()
        for platformdesc in response_data:
            platformDescriptions.append(
                self._new_platform_description_from_dict(platformdesc)
            )

        return platformDescriptions

    def __call__(self):
        return self.__str__()

    def __str__(self):
        all_platforms = self.get_platforms()
        if len(all_platforms) < 0:
            return DataFrame()
        ret = DataFrame(p.__dict__() for p in all_platforms)
        # for plat in all_platforms:
        #     ret = ret.append(plat(), ignore_index=True)
        return ret.sort_values(by="Id").set_index("Id", drop=True)
