import os
import random

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
                                   "GroClient is constructed without the access_token argument")
        self.api_host = api_host
        self.access_token = access_token
        self.client = GroClient(self.api_host, self.access_token)

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
        dict = self.lookup('sources', CLIMATE_SOURCES)
        return list(dict.values())

    def get_cmip6_sources(self) -> list:
        """Returns a list of all five CMIP6 sources, as list of dicts.
        Returns same schema as self.get_sources(...)
        """
        dict = self.lookup('sources', CMIP6_SOURCES)
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
        data_series = self.client.get_data_series(source_id=source_id)
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
        dataseries_gen = self.client.find_data_series(**kwargs)
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
        dataseries = self.client.get_data_series(**kwargs)
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
        return self.client.get_data_points(**selections)