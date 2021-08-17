import datetime as dt
import pandas as pd
# nan is used in the "check_branded" method
# probably can be removed, we just need to check 
# if a list is empty, I'm sure there is a better way
from numpy import nan
import warnings

from .connect import Connection

class GoogleSearchConsole:
    """
    Google API Wrapper for Google Search Console
    REMEMBER your 'client_secret.json' file in your PATH

    Parameters
    auth: googleapiclient.discovery.Resource object 
            created from the Connection class by default
            no need to mess with this
    """

    def __init__(self, auth = Connection().gsc()):
        
        self.auth = auth

        # default values for dims and date values
        self._dims = ["page", "date"]
        self._s_date = dt.date.today() - dt.timedelta(days=7)
        self._e_date = dt.date.today()

        # Variables Assigned throughout the class

        # assigned using .set_sites()
        self._site_list = self.all_sites()
        # assigned using .set_branded()
        self._branded_dict = None
        # assigned using .set_filters()
        self._filter = None
        # assigned in .get_data()
        self._current_site = None
        self.output = None
        # assigned in .ctr() 
        self.my_ctr = None

    def set_sites(self, site_list:list) -> None:
        """
        site_list: list of sites we want to pull from GSC API
            type: list

        if not called, self._site_list = None from __init__
        """
        self._site_list = site_list


    def set_dimensions(self, dimensions:list) -> None:
        """
        d: what we want to break it down by
            type: list
            options: ['page','date','query', 'device','country']
        """
        self._dims = dimensions


    def set_filters(self, filter_object:list) -> None:
        """
        filters_list: list of filters formated as GSC requires
        example_filter = {
                        "dimension": string,
                        "operator": string,
                        "expression": string
                        }

        At this time the GSC api, only allows for dimension based filters

        If you would like a metric based filter, first pull all the data,
        then filter using pandas filtering/querying abilities
        """
        self._filter = filter_object


    def set_date(self,date:dt.date) -> None:
        """
        date: calls the start and end date as the same day
        """
        self._s_date = date
        self._e_date = date


    def set_start_date(self, start_date:dt.date) -> None:
        """
        start_date: the starting point (inclusive) 
                        for the API pull
            type: dt.datetime or dt.date

        declared by __init__ to be 7 days ago
        """
        self._s_date = start_date


    def set_end_date(self, end_date:dt.date) -> None:
        """
        end_date: the ending point (inclusive) 
                    for the API pull
            type: dt.datetime or dt.date

        declared by __init__ to be today
        """
        self._e_date = end_date


    def set_branded(self, branded_dictionary:dict) -> None:
        """
        pass in a dictionary object

        keys are GSC url properties
        values are a list of branded strings
        """
        self._branded_dict = branded_dictionary


    def all_sites(self, site_filters=None) -> list:
        """
        return a list of all verfied sites that you have in GSC.
        
        It will give you all by default, but if you pass in
        a list of words it will only return
        those properties that contain your set of words
        """
        site_list = self.auth.sites().list().execute()
        clean_list = [
            s["siteUrl"]
            for s in site_list["siteEntry"]
            if s["permissionLevel"] != "siteUnverifiedUser"
            and s["siteUrl"][:4] == "http"
        ]
        if site_filters is None:
            return clean_list
        elif isinstance(site_filters, list):
            return [s for s in clean_list if any(xs in s for xs in site_filters)]


    def build_request(self, agg_type="auto", limit=25000, start_row=0, pull=True) -> dict:
        """
        https://developers.google.com/webmaster-tools/
        search-console-api-original/v3/searchanalytics/query

        agg_type: auto is fine can be byPage or byProperty
            defaults "auto"
        limit: number of rows to return
            defaults 25000
        start_row: where to start, if need more than 25,000
            defaults 0
        pull: if we want to call the api and pull data
            defaults True
            pull is used for debugging and should be removed
            once finalized
        """

        request_data = {
            "startDate": self._s_date.strftime("%Y-%m-%d"),
            "endDate": self._e_date.strftime("%Y-%m-%d"),
            "dimensions": self._dims,
            "aggregationType": agg_type,
            "rowLimit": limit,
            "startRow": start_row,
            "dimensionFilterGroups": [{"filters": self._filter}],
        }
        if pull:
            return self.execute_request(request_data)
        else:
            return request_data


    def execute_request(self, request:dict) -> dict:
        """
        Executes a searchAnalytics.query request.

        property_uri: The site or app URI to request data for.
        request: The request to be executed.

        Returns an array of response rows.
        """
        return (
            self.auth.searchanalytics()
            .query(siteUrl=self._current_site, body=request)
            .execute()
        )


    def clean_resp(self, data:dict) -> pd.DataFrame:
        """
        Takes raw response, and cleans the data into a pd.Dataframe
        """
        df = pd.DataFrame(data["rows"])
        df.index.name = "idx"
        keys = df["keys"].apply(pd.Series)
        keys.columns = self._dims
        df = df.merge(keys, how="left", on="idx")
        df.drop(columns="keys", inplace=True)
        df.columns = df.columns.str.capitalize()

        # branded check
        if isinstance(self._branded_dict, dict) and "Query" in df.columns:
            df["Branded"] = self.check_branded(df["Query"])

        # convert to datetime
        if 'Date' in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])

        df[["Clicks", "Impressions"]] = df[["Clicks", "Impressions"]].astype(int)

        return df


    def check_branded(self, query_list:list) -> pd.Series:
        """
        Takes in a list of queries.

        Returns as pd.Series of Bool if the query is branded
        """
        try:
            branded_list = self._branded_dict[self._current_site]
        except KeyError:
            return False
        if branded_list in [nan,[],['']]:
            return False
        return pd.Series(query_list).str.contains(
            "|".join(branded_list), na=False
        )


    def get_data(self) -> dict:
        """
        will loop through the site list,
        grab the data from the api,
        clean it,
        and add it to a dictionary with the site as the key
        after completion
        returns the created dictionary of pd.DataFrame objects
        """
        # check to make sure self._site_list is declared
        if not self._site_list:
            raise AttributeError("Please declare self._site_list"\
                " using the .set_sites() method prior to running .get_data")
        data = {}
        for x in self._site_list:
            self._current_site = x
            start = 0
            row_limit = 25000
            temp_df = pd.DataFrame()
            # loop through the api grabbing the maximum rows possible
            while True:
                # get the data from the api
                response = self.build_request(limit=row_limit, start_row=start)
                # if rows is in keys, we have data
                if 'rows' in response.keys():
                    df = self.clean_resp(response)
                    temp_df = temp_df.append(df)
                    start += row_limit
                # if not, we have pulled the max, we need to break
                else:
                    break

            data[x] = temp_df

        # declare the data as output and save to class
        # this could be large, could have memory issues, need to
        # look into this
        self.output = data

        return data


    def ctr(self) -> dict:
        '''
        Used after we have called .get_data()
        Calulcates a custom click curve for the given data that you have pulled
        
        Returns
        a dictionary with the following keys:
            - "all"
                a general CTR given all the data
            - "branded"
                a CTR for only branded queries
            - "non-branded"
                a CTR for only non-branded queries

        There are a few things that throw off the custom CTR calculations:

        1) If "query" is included as a dimension when we pulled the data
            if not included, we will see weird numbers
            make sure that query is included in dimensions
            use .set_dimensions()

        2) If there are branded queries
            We tend to see branded queries experience a higher CTR, 
            and will thus inflate your numbers if we don't separate them
            declare branded queries using .set_branded()
        '''
        if not self.output:
            raise AttributeError("Please run .get_data() prior to running .ctr()")

        if 'query' not in self._dims:
            warnings.warn('"query" is not an active dimension in your data.'\
                ' CTR calulcations are heavily influcenced by queries.'\
                ' It is reccomented to use the "query" dimension to ensure accurate CTR numbers.')

        if not self._branded_dict:
            warnings.warn('You have not declared any branded queries using .set_branded(dict).'\
                ' CTR calulcations are heavily influcenced by branded queries.'\
                ' It is reccomented to assign brand words to ensure accurate CTR numbers.')

        # declare function to group by position and get CTR
        def calculate_ctr(df:pd.DataFrame,col:str) -> pd.DataFrame:
            '''
            this groups by position and gives us our CTR

            df: type: pd.DataFrame
                data from the .get_data() formated as a pd.DataFrame
                this will group all sites in self._site_list together
            col: type: str
                is the string name of the column to groupby
                normally this should be 'Pos'
                as declared in .ctr() scope
            '''
            ctr = df.groupby(col).sum()
            ctr['CTR'] = ctr['Clicks']/ctr['Impressions']
            
            if self._branded_dict:
                return ctr.drop(columns='Branded')

            return ctr

        # create the dataframe from response dictionary - .get_data() response
        df = pd.DataFrame()
        for x in self.output:
            df = df.append(self.output[x])
        # create the rounded position column
        df['Pos'] = df['Position'].round(0)

        # we only want to consider those queries in the top 100 positions
        # also, we only want Clicks, Impressions, and Pos, the rest doesn't matter
        if self._branded_dict:
            df = df.loc[df['Pos']<=100][['Clicks','Impressions','Pos','Branded']].copy()
        else:
            df = df.loc[df['Pos']<=100][['Clicks','Impressions','Pos']].copy()

        # create the first dictionary object including all data
        ctr_data = {'all':calculate_ctr(df,'Pos')}

        # if Branded is in the columns we will separate the click curves into
        # Branded vs Non-Branded and return both as well
        if self._branded_dict:
            # use that function to get our custom CTR
            ctr_b = calculate_ctr(df.loc[df['Branded']==True].copy(),'Pos')
            ctr_nb = calculate_ctr(df.loc[df['Branded']==False].copy(),'Pos')

            ctr_data["branded"] = ctr_b
            ctr_data["non-branded"] = ctr_nb

        self.my_ctr = ctr_data

        return ctr_data

