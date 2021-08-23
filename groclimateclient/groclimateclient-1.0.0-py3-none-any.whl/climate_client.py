import os
import random
from fuzzywuzzy import fuzz
import pandas

from groclient import GroClient
from groclimateclient.constants import CLIMATE_METRICS,CLIMATE_ITEMS, CLIMATE_SOURCES,CMIP6_SOURCES
API_HOST = "api.gro-intelligence.com"

class GroClimateClient(object):
    def __init__(self, api_host=API_HOST, access_token=None):
        """Construct a GroClimateClient instance.

        Parameters
        ----------
        api_host : string, optional
            The API server hostname.
        access_token : string, optional
            Your Gro API authentication token. If not specified, the
            :code:`$GROAPI_TOKEN` environment variable is used. See
            :doc:`authentication`.

        Raises
        ------
            RuntimeError
                Raised when neither the :code:`access_token` parameter nor
                :code:`$GROAPI_TOKEN` environment variable are set.

        Examples
        --------
            >>> client = GroClient()  # token stored in $GROAPI_TOKEN

            >>> client = GroClient(access_token="your_token_here")
        """

        if access_token is None:
            access_token = os.environ.get("GROAPI_TOKEN")
            if access_token is None:
                raise RuntimeError("$GROAPI_TOKEN environment variable must be set when "
                                   "GroClimateClient is constructed without the access_token argument")
        self._api_host = api_host
        self._access_token = access_token
        self._client = GroClient(self._api_host, self._access_token)

    def get_sources(self):
        """Returns a list of all climate sources, as JSON.
            The schema for our climate sources is:
            ['description',
            'fileFormat',
            'historicalStartDate',
            'id',
            'language',
            'longName',
            'name',
            'regionalCoverage',
            'resolution',
            'sourceLag']
        """
        dict = self._client.lookup('sources', CLIMATE_SOURCES)
        return list(dict.values())

    def get_cmip6_sources(self) -> list:
        """Returns a list of all five CMIP6 sources, as list of dicts.
        Returns same schema as self.get_sources(...)
        """
        dict = self._client.lookup('sources', CMIP6_SOURCES)
        return list(dict.values())

    def get_metrics(self):
        """Returns a dictionary of available climate metrics
        key: metric_id (as an int)
        value: metric_name

        You can use the function to translate from metric_id to metric_name, e.g.
        get_metrics()[15852978] will return 'Variation of Precipitation'.
        """
        return CLIMATE_METRICS

    def get_items(self):
        """Returns a dictionary of available climate items
        key: item_id (as an int)
        value: item_name

        You can use the function to translate from item_id to item_name, e.g.
        get_items()[5113] will return 'Snow depth'
        """
        return CLIMATE_ITEMS

    def get_items_sample(self, size=5):
        """Returns a random sample of climate items.
        Call it multiple times to discover new items.
        """
        items_dict = list(self.get_items().items())
        size = min(len(items_dict), size)
        return random.sample(items_dict, size)

    def get_metrics_sample(self, size=5):
        """Returns a random sample of climate metrics.
        Call it multiple times to discover new metrics.
        """
        metrics_dict = list(self.get_metrics().items())
        size = min(len(metrics_dict), size)
        return random.sample(metrics_dict, size)

    def get_items_metrics_for_a_source(self, source_id):
        """Returns a set of item-metric for a given source, based on a source_id (int).
        Raises an exception if the source is not part of the climate tier.
        """
        if source_id not in CLIMATE_SOURCES:
            raise Exception('Source %d is not part of the climate tier.' % source_id)
        data_series = self._client.get_data_series(source_id=source_id)
        items_metrics = set()
        for ds in data_series:
            items_metrics.add(ds['item_name'] + ' – ' + ds['metric_name'])
        return sorted(list(items_metrics))

    def find_data_series(self, **kwargs):
        """Find data series from the climate tier matching a combination of entities specified by
        name and yield them ranked by coverage.

        Parameters
        ----------
        metric : string, optional
        item : string, optional
        region : string, optional
        partner_region : string, optional
        start_date : string, optional
            YYYY-MM-DD
        end_date : string, optional
            YYYY-MM-DD

        e.g. dataseries_gen = client.find_data_series(item="Temperature (max)", metric="Temperature", region="Alaska")
            for i in range(5):
            print(next(dataseries_gen))
        """
        dataseries_gen = self._client.find_data_series(**kwargs)
        while True:
            result = next(dataseries_gen)
            if result['source_id'] in CLIMATE_SOURCES:
                yield result

    def get_data_series(self, **kwargs):
        """Get available data series for the given selections from the climate tier.

        https://developers.gro-intelligence.com/data-series-definition.html

        Parameters
        ----------
        metric_id : integer, optional
        item_id : integer, optional
        region_id : integer, optional
        partner_region_id : integer, optional
        source_id : integer, optional
        frequency_id : integer, optional

        Returns
        -------
        list of dicts

            Example::

                [{ 'metric_id': 2020032, 'metric_name': 'Seed Use',
                    'item_id': 274, 'item_name': 'Corn',
                    'region_id': 1215, 'region_name': 'United States',
                    'source_id': 24, 'source_name': 'USDA FEEDGRAINS',
                    'frequency_id': 7,
                    'start_date': '1975-03-01T00:00:00.000Z',
                    'end_date': '2018-05-31T00:00:00.000Z'
                }, { ... }, ... ]

        """
        dataseries = self._client.get_data_series(**kwargs)
        filtered_dataseries=[series for series in dataseries if series['source_id'] in CLIMATE_SOURCES]
        return filtered_dataseries

    def get_data_points(self, **selections):
        """Gets all the data points for a given selection within the climate tier.

        Parameters
        ----------
        metric_id : integer or list of integers
            How something is measured. e.g. "Export Value" or "Area Harvested"
        item_id : integer or list of integers
            What is being measured. e.g. "Corn" or "Rainfall"
        region_id : integer or list of integers
            Where something is being measured e.g. "United States Corn Belt" or "China"
        partner_region_id : integer or list of integers, optional
            partner_region refers to an interaction between two regions, like trade or
            transportation. For example, for an Export metric, the "region" would be the exporter
            and the "partner_region" would be the importer. For most series, this can be excluded
            or set to 0 ("World") by default.
        source_id : integer
        frequency_id : integer
        unit_id : integer, optional
        start_date : string, optional
            All points with end dates equal to or after this date
        end_date : string, optional
            All points with start dates equal to or before this date
        reporting_history : boolean, optional
            False by default. If true, will return all reporting history from the source.
        complete_history : boolean, optional
            False by default. If true, will return complete history of data points for the selection. This will include
            the reporting history from the source and revisions Gro has captured that may not have been released with an official reporting_date.
        insert_null : boolean, optional
            False by default. If True, will include a data point with a None value for each period
            that does not have data.
        at_time : string, optional
            Estimate what data would have been available via Gro at a given time in the past. See
            :sample:`at-time-query-examples.ipynb` for more details.
        include_historical : boolean, optional
            True by default, will include historical regions that are part of your selections
        available_since : string, optional
            Fetch points since last data retrieval where available date is equal to or after this date
        """
        if 'source_id' not in selections:
            raise Exception('a valid climate source_id MUST be selected')
        if selections['source_id'] not in CLIMATE_SOURCES:
            raise Exception('Source %d is not part of the climate tier' % selections['source_id'])
        return self._client.get_data_points(**selections)

    def get_ancestor_regions(
      self,
      entity_id,
      distance=None,
      include_details=True,
      ancestor_level=None,
      include_historical=True,
      ):
        """Given a region, returns all its ancestors i.e.
        regions that "contain" in the given region.

        Parameters
        ----------
        entity_id : integer
        distance: integer, optional
            Return all entities that contain the entity_id at maximum distance. If provided along
            with `ancestor_level`, this will take precedence over `ancestor_level`.
            If not provided, get all ancestors.
        include_details : boolean, optional
            True by default. Will perform a lookup() on each ancestor to find name,
            definition, etc. If this option is set to False, only ids of ancestor
            entities will be returned, which makes execution significantly faster.
        ancestor_level : integer, optional
            The region level of interest. See REGION_LEVELS constant. This should only be specified
            if the `entity_type` is 'regions'. If provided along with `distance`, `distance` will
            take precedence. If not provided, and `distance` not provided, get all ancestors.
        include_historical : boolean, optional
            True by default. If False is specified, regions that only exist in historical data
            (e.g. the Soviet Union) will be excluded.

        """
        return self._client.get_ancestor(
            'regions', entity_id,
            distance=distance, include_details=include_details,
            ancestor_level=ancestor_level, include_historical=include_historical)

    def get_descendant_regions(
        self,
        entity_id,
        distance=None,
        include_details=True,
        descendant_level=None,
        include_historical=True,
    ):
        """Given a region, returns all its descendants i.e. entities that are "contained" in the given region.

        The `distance` parameter controls how many levels of child entities you want to be returned.
        Additionally, if you are getting the descendants of a given region, you can specify the
        `descendant_level`, which will return only the descendants of the given `descendant_level`.
        However, if both parameters are specified, `distance` takes precedence over
        `descendant_level`.

        Parameters
        ----------
        entity_id : integer
        distance: integer, optional
            Return all entities that contain the entity_id at maximum distance. If provided along
            with `descendant_level`, this will take precedence over `descendant_level`.
            If not provided, get all ancestors.
        include_details : boolean, optional
            True by default. Will perform a lookup() on each descendant  to find name,
            definition, etc. If this option is set to False, only ids of descendant
            entities will be returned, which makes execution significantly faster.
        descendant_level : integer, optional
            The region level of interest. See REGION_LEVELS constant. This should only be specified
            if the `entity_type` is 'regions'. If provided along with `distance`, `distance` will
            take precedence. If not provided, and `distance` not provided, get all ancestors.
        include_historical : boolean, optional
            True by default. If False is specified, regions that only exist in historical data
            (e.g. the Soviet Union) will be excluded.
        """
        return self._client.get_descendant(
            'regions', entity_id,
            distance=distance, include_details=include_details,
            descendant_level=descendant_level, include_historical=include_historical)

    def get_geo_centre(self, region_id):
        """Given a region_id (int), returns the geographic centre in degrees lat/lon.
        """
        return self._client.get_geo_centre(region_id)

    def get_geojson(self, region_id, zoom_level=7):
        """Given a region ID, return shape information in geojson.
        """
        return self._client.get_geojson(region_id, zoom_level=zoom_level)

    def search(self, entity_type, search_terms, num_results=10):
        """Searches for the given search term. Better matches appear first.
        Search for the given search terms and look up their details.
        For each result, yield a dict of the entity and its properties.
        """
        if entity_type is 'regions':
            for result in self._client.search_and_lookup('regions', search_terms, num_results=num_results):
                yield result

        if entity_type is 'metrics':
            ranked_results = sorted( [ (k[0], k[1], fuzz.token_set_ratio(search_terms, k[1])) for k in list(self.get_metrics().items())], key=lambda x:x[2], reverse=True)
            for result in ranked_results:
                yield { 'metric_id': result[0], 'metric_name': result[1], 'score': result[2] }

        if entity_type is 'items':
            ranked_results = sorted([(k[0], k[1], fuzz.token_set_ratio(search_terms, k[1])) for k in list(self.get_items().items())], key=lambda x:x[2], reverse=True)
            for result in ranked_results:
                yield { 'item_id': result[0], 'item_name': result[1], 'score': result[2] }

        return "N/A"

    def get_top_region_match(self, query: str) -> dict:
        """
        Simple wrapper for self.search(...), returns the top region match for a string query
        """
        searchResults=list(self.search('regions', query, num_results=1))

        if len(searchResults)==0:
            raise Exception("No region match for query "+query)
        return searchResults[0]

    def add_single_data_series(self, data_series: dict) -> None:
        """Save a data series object to the GroClient's data_series_list.

        For use with :meth:`~.get_df`.

        Parameters
        ----------
        data_series : dict
            A single data_series object, as returned by :meth:`~.get_data_series` or
            :meth:`~.find_data_series`.
            See https://developers.gro-intelligence.com/data-series-definition.html

        Returns
        -------
        None

        """
        if data_series['source_id'] not in CLIMATE_SOURCES:
            raise Exception("Can't add the following data series, not in the climate tier: "+str(data_series))
        self._client.add_single_data_series(data_series)

    def clear_data_series_list(self) -> None:
        """
        Clear the list of saved data series which have been added with add_single_data_series(...)
        """
        self._client._data_series_list = set()
        self._client._data_series_queue = []
        self._client._data_frame = pandas.DataFrame()

    def get_df(self, **kwargs):
        """Call :meth:`~.get_data_points` for each saved data series and return as a combined
        dataframe.

        Note you must have first called either :meth:`~.add_data_series` or
        :meth:`~.add_single_data_series` to save data series into the GroClient's data_series_list.
        You can inspect the client's saved list using :meth:`~.get_data_series_list`.

        See https://developers.gro-intelligence.com/api.html#groclient.GroClient.get_df for full documentation
        """

        return self._client.get_df(**kwargs)