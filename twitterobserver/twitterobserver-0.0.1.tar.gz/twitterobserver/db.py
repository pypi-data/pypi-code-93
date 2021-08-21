
import os.path
import sqlite3
import tweepy
from sqlite3 import Error

create_tables_sql_str = """

CREATE TABLE IF NOT EXISTS queries (
    queryId text PRIMARY KEY,
    trUserId text
);

CREATE TABLE IF NOT EXISTS users (
    userId text PRIMARY KEY,
    userURL text,
    userScreenName text,
    userName text,
    userFriends integer,
    userFollowers integer
);

CREATE TABLE IF NOT EXISTS qfRelation (
    qfId INTEGER PRIMARY KEY AUTOINCREMENT,
    relationType text,
    userId  text REFERENCES followers(userId),
    queryId text REFERENCES queries(queryId)
);

"""

def create_db(db_file, create_str):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        sql_str = create_str
        c.executescript(sql_str)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


class db_instance:
    def __init__(self, db_file):
        if os.path.isfile(db_file):
            print("File exist")
            self.dbFile = db_file
        else:
            create_db(db_file,create_tables_sql_str)
            self.dbFile = db_file


class user_instance:
    """
    note: I think the tweepy user can also be an dict with the ids of 
    each field.
    note2: It can not, got confused with JS. But we can make a single if
    and it should be ok.
    """
    def __init__(self,tweepy_user): ## maybe i could inherit here? tried, compl
        if isinstance(tweepy_user, dict):
            self.userId = tweepy_user['userId']
            self.userURL = tweepy_user['userURL']
            self.userScreenName = tweepy_user['userScreenName']
            self.userName = tweepy_user['userName']
            self.userFriends = tweepy_user['userFriends']
            self.userFollowers = tweepy_user['userFollowers']
        elif isinstance(tweepy_user, tweepy.models.User):
            self.userId = tweepy_user.id
            self.userURL = tweepy_user.url
            self.userScreenName = tweepy_user.screen_name
            self.userName = tweepy_user.name
            self.userFriends = tweepy_user.friends_count
            self.userFollowers = tweepy_user.followers_count
        else:
            raise TypeError("tweepy_user must be a tweepy.models.User or a dict")
    def export_tuple(self):
        tpl_out = (self.userId, self.userURL, self.userScreenName,self.userName,self.userFriends, self.userFollowers )
        return tpl_out



