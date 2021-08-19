"""This module implments a client for the Intelligent Plant Data Core API"""
__author__ = "Ross Kelso"
__docformat__ = 'reStructuredText'

import urllib.parse as urlparse

import json
import intelligent_plant.http_client as http_client

def normalise_tag_map(tags):
    for entry in tags.items():
        if isinstance(entry[1], str):
            tags[entry[0]] = [entry[1]]

    return tags

class DataCoreClient(http_client.HttpClient):
    """Access the Intelligent Plant Data Core API"""

    def __init__(self, base_url = "https://appstore.intelligentplant.com/gestalt/datacore/", **kwargs):
        """
        Initialise a data core client with the specified authoriation haeder value and base URL.
        It is recommended that you use AppStoreClient.get_data_core_client(..) rather than calling this directly.

        :param authorization_header: The authorization header that will be used for all requests.
        :param base_url: The base URL to make requests from. The default value is "https://appstore.intelligentplant.com/gestalt/datacore/" (the app store data api)
        """
        super().__init__(base_url, **kwargs)
    
    def get_data_sources(self):
        """
        Get the list of available data sources

        :return: The available data sources as a parsed JSON object.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        params = {}
        
        return self.get_json("api/data/datasources", params)

    def get_tags(self, dsn, page = 1, page_size = 20, filters = {}):
        """
        Search the provided data source fo tags.

        :param dsn: The fully qualified name of the data source. seealso::get_data_sources
        :param page: The number of the current page of results. Default: 1.
        :param page_size: The number of results to return on a page. Default: 20.
        :param filters: A dictionary of filters where the key is the field name (e.g. name, description, unit)
            and the value is the filter to apply.

        :return: The available tags as a parsed JSON object.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        params = filters.copy()
        params["page"] = page
        params["pageSize"] = page_size
        
        return self.get_json("api/data/tags/" + dsn, params)

    def get_snapshot_data(self, tags):
        """
        Get the snapshot values of the provided tags.

        :param tags: A dictionary where the keys are the fully qualified data source names and the values are lists of tags.

        :return: A dictionary of data source names, containg dictionarys of tag names whos values are tag values.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        return self.post_json("api/data/v2/snapshot", json={"tags": normalise_tag_map(tags)})

    def get_raw_data(self, tags, start_time, end_time, point_count):
        """
        Get raw data for the provided tags.

        :param tags: A dictionary where the keys are the fully qualified data source names and the values are lists of tags.
        :param start_time: The absolute or relative quiery start time.
        :param end_time: The absolute or relative quiery end time.
        :param point_count: The maximum number of point to return. Set to 0 for as many as possible.

        :return: A dictionary of data source names, containg dictionarys of tag names whos values are historical tag values.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        req = {
            "tags": normalise_tag_map(tags),
            "startTime": start_time,
            "endTime": end_time,
            "pointCount": point_count
        }

        return self.post_json("api/data/v2/raw", json=req)

    def get_plot_data(self, tags, start_time, end_time, intervals):
        """
        Get raw data for the provided tags.

        :param tags: A dictionary where the keys are the fully qualified data source names and the values are lists of tags.
        :param start_time: The absolute or relative quiery start time.
        :param end_time: The absolute or relative quiery end time.
        :param intervals: How many intervals to divide the rtequest range into. Must be greater than 0

        :return: A dictionary of data source names, containg dictionarys of tag names whos values are historical tag values.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        req = {
            "tags": normalise_tag_map(tags),
            "startTime": start_time,
            "endTime": end_time,
            "intervals": intervals
        }

        return self.post_json("api/data/v2/plot", json=req)

    def get_processed_data(self, tags, start_time, end_time, sample_interval, data_function):
        """
        Get processed data for the provided tags.

        :param tags: A dictionary where the keys are the fully qualified data source names and the values are lists of tags.
        :param start_time: The absolute or relative quiery start time.
        :param end_time: The absolute or relative quiery end time.
        :param sample_interval: The length of a sample interval
        :param data_function: The data function to use. Normal values are "interp", "avg", "min" and "max"

        :return: A dictionary of data source names, containg dictionarys of tag names whos values are historical tag values.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        req = {
            "tags": normalise_tag_map(tags),
            "startTime": start_time,
            "endTime": end_time,
            "sampleInterval": sample_interval,
            "dataFunction": data_function
        }

        return self.post_json("api/data/v2/processed", json=req)

    def get_data_at_times(self, tags, utc_sample_times):
        """
        Get the value of the provided tags at the specified times.

        :param tags: A dictionary where the keys are the fully qualified data source names and the values are lists of tags.
        :param utc_sample_times: The time stamps to retrieve the values for,

        :return: A dictionary of data source names, containg dictionarys of tag names whos values are historical tag values.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """
        req = {
            "tags": normalise_tag_map(tags),
            "utcSampleTimes": utc_sample_times
        }

        return self.post_json("api/data/v2/history-at-times", json=req)

    def write_snapshot_values(self, dsn, values):
        """
        Write a set of tag values into the specified datasource.

        :param dsn: The data source name the values are to be written to.
        :param values: A list of TagValue Objects that specifiy the values and the time stamps they are to be written at.

        :return: A dictionary of tag names, containg dictionarys of Write Results detailing the success of the write.
        :raises: :class:`HTTPError`, if one occurred.
        :raises: An exception if JSON decoding fails.
        """

        return self.put_json(urlparse.urljoin("api/data/v2/snapshot/", dsn), json=values)