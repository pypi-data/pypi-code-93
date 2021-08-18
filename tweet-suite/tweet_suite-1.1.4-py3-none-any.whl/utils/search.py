"""Module containing FullArchiveSearch class which controls access to
the Twitter Full Archive Search API. 

Requires an environment variable with a bearer token called 
`SEARCHTWEETS_BEARER_TOKEN`.

It will search with the query defined in FullArchiveSearch.get_tweets()
which dynamically updates the dates of the search so the end time is 
always 23.59 yesterday.

The start datetime will be 7 days previous if it is running for the first
time, otherwise it will be the time of the most recent tweet.
"""

import requests
import os
from retry import retry
import logging

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from utils.database import Database


class FullArchiveSearch:
    """Class to implement a full archive search using the V2 Twitter API, and save the data
    to the database provided via the Database object."""

    def __init__(self, database: Database):
        self.bearer_token = os.environ.get("SEARCHTWEETS_BEARER_TOKEN")
        self.search_url = "https://api.twitter.com/2/tweets/search/all"
        self.database = database

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FullArchiveSearchPython"
        return r

    @retry(Exception, tries=3, delay=3, backoff=5)
    def connect_to_endpoint(self, params):
        response = requests.request(
            "GET", self.search_url, auth=self.bearer_oauth, params=params
        )
        if response.status_code == 429:
            raise Exception("Rate limited")
        if response.status_code != 200:
            raise Exception("Didn't get a 200 response...")
        return response.json()

    def fetch_twitter_data(self, query_params):
        # Get the json response from Twitter
        json_response = self.connect_to_endpoint(query_params)
        # Add the data to the database
        self.database.add_tweet_json(json_response)

        # Whilst there is a next token option in the response, paginate through.
        while "next_token" in json_response["meta"]:
            query_params["next_token"] = json_response["meta"]["next_token"]
            json_response = self.connect_to_endpoint(query_params)
            self.database.add_tweet_json(json_response)

    def start_time(self):
        """Get the time that the query needs to start from."""

        # Get the time of the most recent tweet in the dataframe
        latest_tweet = self.database.get_latest_tweet()

        # If there is no latest tweet then we need 7 days of data.
        if latest_tweet is None:
            # Set start time as midnight yesterday minus one week
            start_time = (self.yesterday() - timedelta(weeks=1)).strftime(
                "%Y-%m-%dT"
            ) + ("23:59:00Z")
            logger.info(
                "First run of scheduler - will collect 7 days of tweets since {}".format(
                    start_time
                )
            )
        else:  # Otherwise, set the start time as the most recent date in the database
            start_time = latest_tweet[1]
            logger.info("Updated start time is set as {}".format(start_time))

        return start_time

    @staticmethod
    def yesterday():
        """Get the datetime for yesterday"""

        return datetime.now().date() - timedelta(days=1)

    def get_tweets(self):

        start = self.start_time()
        # The end time must be at least 10 seconds before the request time, so take 30 seconds.
        end = self.yesterday().strftime("%Y-%m-%dT") + ("23:59:00Z")

        # Get the tweets between the start time we've set and now.
        query = {
            "query": "place_country:GB place:Wales",
            "start_time": start,
            "end_time": end,
            "tweet.fields": "id,created_at,author_id,text,public_metrics,geo,lang,referenced_tweets",
            "place.fields": "country,country_code,full_name,geo,id,name,place_type",
            "expansions": "geo.place_id",
            "max_results": 500,
        }

        # Now, pass this query to the function that actually fetches the data.
        self.fetch_twitter_data(query)

        logger.info("Tweets successfully collected.")

