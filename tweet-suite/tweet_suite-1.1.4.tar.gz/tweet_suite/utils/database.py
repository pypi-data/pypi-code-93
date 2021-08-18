"""Contains the Database class which controls the set up and
access to the SQLite database where tweet data is saved.

When first called it will setup the database if a database
with the same name does not already exist. 
"""

import sqlite3
from sqlite3 import Error
import logging
import os
import pandas as pd

from utils.text_processing import process_text, vader

logger = logging.getLogger(__name__)


class Database:
    """Class to represent the SQLite database and manage connections to it."""

    def __init__(self, db):
        self.db = db
        self.setup_database()

    def setup_database(self):
        """Establish if the database exists, and if it doesn't then create it."""
        if not os.path.exists(self.db):
            self.create_tweets_tables()
            logger.info("Database created, named {}".format(self.db))
        else:
            logger.info("Using existing database named {}".format(self.db))

    def create_connection(self):
        """ Create a database connection to the SQLite database
            specified by db
        :param db: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db)
        except Error as e:
            logger.warning(e)

        return conn

    @staticmethod
    def create_table(conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            logger.warning(e)

    def create_tweets_tables(self):
        """Create the tables we need for places and tweets in the SQLite3 database."""

        sql_create_places_table = """CREATE TABLE IF NOT EXISTS places (
                                        id text PRIMARY KEY,
                                        added TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                        country text,
                                        country_code text,
                                        full_name text,
                                        geo_bbox text,
                                        name text,
                                        place_type text
                                    );"""

        sql_create_tweets_table = """CREATE TABLE IF NOT EXISTS tweets (
                                        id integer PRIMARY KEY,
                                        added TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                        tweet_id integer UNIQUE,
                                        author_id text NOT NULL,
                                        created_at text NOT NULL,
                                        tweet_text text NOT NULL,
                                        simple_text text,
                                        vader_pos real,
                                        vader_neg real,
                                        vader_neu real,
                                        vader_comp real,
                                        lang text,
                                        place_id text,
                                        like_count integer,
                                        quote_count integer,
                                        reply_count integer,
                                        retweet_count integer,
                                        referenced_tweet text,
                                        referenced_type text,
                                        FOREIGN KEY (place_id) REFERENCES places (id)
                                    ); """

        sql_create_matchedplaces_table = """CREATE TABLE IF NOT EXISTS matchedplaces (
                                        id integer PRIMARY KEY,
                                        added TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                        place_id text UNIQUE,
                                        lsoa text,
                                        lsoa_name text,
                                        lsoa_match real,
                                        FOREIGN KEY (place_id) REFERENCES places (id)
                                    ); """

        # create a database connection
        conn = self.create_connection()
        # create tables
        if conn is not None:
            # create places table
            self.create_table(conn, sql_create_places_table)
            # create tweets table
            self.create_table(conn, sql_create_tweets_table)
            # create table for geo matched
            self.create_table(conn, sql_create_matchedplaces_table)

            logger.info(
                "Tables tweets, places and matchedplaces have been created in the database {}".format(
                    self.db
                )
            )

        else:
            logger.warning("Error! cannot create the database connection.")

    @staticmethod
    def create_place(conn, place):
        """
        Create a new place in the places table
        :param conn:
        :param place:
        :return: place id
        """
        sql = """ INSERT OR IGNORE INTO places(id,country,country_code,full_name,geo_bbox,name,place_type)
                VALUES(?,?,?,?,?,?,?) """
        cur = conn.cursor()
        cur.execute(sql, place)
        conn.commit()
        return cur.lastrowid

    @staticmethod
    def create_tweet(conn, tweet):
        """
        Create a new tweet
        :param conn:
        :param task:
        :return:
        """

        sql = """ INSERT OR IGNORE INTO tweets(tweet_id,author_id,created_at,tweet_text,simple_text,
                vader_pos,vader_neg,vader_neu,vader_comp,lang,place_id,like_count,quote_count,
                reply_count,retweet_count,referenced_tweet,referenced_type)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """

        cur = conn.cursor()
        cur.execute(sql, tweet)
        conn.commit()
        return cur.lastrowid

    def add_tweet_json(self, data):
        """Adds tweets to the database from the json object they are returned as.
        """
        # create a database connection
        conn = self.create_connection()

        with conn:

            # create new places
            for place in data["includes"]["places"]:
                new_place = (
                    place["id"],
                    place["country"],
                    place["country_code"],
                    place["full_name"],
                    str(place["geo"]["bbox"]),
                    place["name"],
                    place["place_type"],
                )
                self.create_place(conn=conn, place=new_place)

            for tweet in data["data"]:
                vader_sentiment = vader(tweet["text"])
                try:
                    new_tweet = (
                        tweet["id"],
                        tweet["author_id"],
                        tweet["created_at"],
                        tweet["text"],
                        process_text(tweet["text"]),
                        vader_sentiment["pos"],
                        vader_sentiment["neg"],
                        vader_sentiment["neu"],
                        vader_sentiment["compound"],
                        tweet["lang"],
                        tweet["geo"]["place_id"],
                        tweet["public_metrics"]["like_count"],
                        tweet["public_metrics"]["quote_count"],
                        tweet["public_metrics"]["reply_count"],
                        tweet["public_metrics"]["retweet_count"],
                        tweet["referenced_tweets"][0]["id"],
                        tweet["referenced_tweets"][0]["type"],
                    )
                except KeyError:  # In the case that there is no referenced tweet
                    new_tweet = (
                        tweet["id"],
                        tweet["author_id"],
                        tweet["created_at"],
                        tweet["text"],
                        process_text(tweet["text"]),
                        vader_sentiment["pos"],
                        vader_sentiment["neg"],
                        vader_sentiment["neu"],
                        vader_sentiment["compound"],
                        tweet["lang"],
                        tweet["geo"]["place_id"],
                        tweet["public_metrics"]["like_count"],
                        tweet["public_metrics"]["quote_count"],
                        tweet["public_metrics"]["reply_count"],
                        tweet["public_metrics"]["retweet_count"],
                        None,
                        None,
                    )

                self.create_tweet(conn=conn, tweet=new_tweet)

    def get_latest_tweet(self):
        """
        Query to get the most recent tweet in the db.
        :param db: name of the db to connect to
        """

        # create a database connection
        conn = self.create_connection()
        cur = conn.cursor()

        # Run a query to get the time of the latest ID from the tweets in the database
        cur.execute("SELECT tweet_id, MAX(created_at) FROM tweets;")
        latest_tweet = cur.fetchone()

        # Return the time
        if latest_tweet[0] is None:
            return None
        else:
            return latest_tweet

    def get_unmatched_places(self):
        """Returns a pandas dataframe of all the places that
        aren't matched in the matchedplaces table."""

        # Query to return the info of all places without a matchedplace
        sql = """SELECT places.id,places.geo_bbox,places.full_name FROM places 
                    LEFT JOIN matchedplaces ON places.id = matchedplaces.place_id 
                    WHERE matchedplaces.place_id IS NULL;"""

        # create a database connection
        conn = self.create_connection()

        return pd.read_sql(sql, conn)

    def write_matched_places(self, matchedplaces):
        """Collect the matched places and write them back to the database"""

        # Get just the cols we want
        data = pd.concat(
            [
                matchedplaces["id"],
                matchedplaces["lad19cd"],
                matchedplaces["lad19nm"],
                matchedplaces["likelihood"],
            ],
            axis=1,
            keys=["place_id", "lsoa", "lsoa_name", "lsoa_match"],
        )

        # create a database connection
        conn = self.create_connection()

        # Write these to the db
        data.to_sql(
            name="matchedplaces", con=conn, if_exists="append", index=False,
        )

        logger.info(
            "Total of {} newly matched places written to matchplaces table.".format(
                data.shape[0]
            )
        )

