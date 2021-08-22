
import time
import json
import os.path
import tweepy
import sqlite3
from sqlite3 import Error

def json2dict(filename):
    """
    read a json file and store it in a dictionary
    """
    with open(filename) as f:
        data = json.load(f)
    return data

def dict2json(filename, data):
    """
    Write out a dictionary to a json file
    """
    with open(filename, 'w') as f:
        json.dump(data, f)

class db_instance:
    def __init__(self, db_file):
        if os.path.isfile(db_file):
            print("File exist")
            self.dbFile = db_file
        else:
            raise ValueError("File does not exist")
    def create_state_file(self,state_file):
        """
        check if state file exists, if not, create a json file that will
        store the unique users and the last queryId
        """
        self.state_file = state_file
        if os.path.isfile(state_file):
            print("File exist")
            self.state = json2dict(state_file)
            ## note that this won't work if the file is half full
            ## meaning only people in the file will then be considered
            ## to start from scratch, delete the file.
        else:
            users_array = self.extract_unique_users()
            lq_array = [self.extract_last_query(i) for i in users_array]
            self.state = dict(zip(users_array, lq_array))
            dict2json(state_file, self.state)
    def update_state(self,username,lastQ):
        """
        Updates the state query for a given username
        """
        self.state[username] = lastQ
    def overwrite_state(self):
        """
        Overwrite the state file with the latest state
        """
        dict2json(self.state_file, self.state)
    def extract_unique_users(self):
        """
        Query the sqlite3 database and extract all users
        :return:
        """
        conn = sqlite3.connect(self.dbFile)
        c = conn.cursor()
        c.execute("SELECT DISTINCT trUserId FROM queries")
        rows = c.fetchall()
        conn.close()
        users_arr = [i[0] for i in rows]
        self.trackedusers = users_arr
        return users_arr
    def extract_last_query(self, username):
        """
        Obtain the last queryId that is stored for a given user
        """
        conn = sqlite3.connect(self.dbFile)
        c = conn.cursor()
        c.execute("SELECT MAX(queryId) FROM queries WHERE trUserId=?", (username,))
        rows = c.fetchall()
        conn.close()
        return rows[0][0]
    def obtain_list_friends(self, queryId):
        """
        For a given username and query, return the list of friends from the
        users table.
        """ 
        sql_str = "SELECT userId FROM qfRelation WHERE queryId=? AND relationType = 'friend'"
        conn = sqlite3.connect(self.dbFile)
        c = conn.cursor()
        c.execute(sql_str, (queryId,))
        rows = c.fetchall()
        conn.close()
        return [i[0] for i in rows]
    def get_user_screenName(self, userId):
        """
        From userId return userScreenName in the database
        """
        conn = sqlite3.connect(self.dbFile)
        c = conn.cursor()
        c.execute("SELECT userScreenName FROM users WHERE userId=?", (userId,))
        rows = c.fetchall()
        conn.close()
        return rows[0][0]

class api_client:
    def __init__(self, secrets_file):
        with open(secrets_file) as json_file:
            json_keys = json.load(json_file)
        # the auth in tweepy has 2 levels
        c_key = json_keys["c_key"]
        c_secret = json_keys["c_secret"]
        auth = tweepy.OAuthHandler(c_key, c_secret)
        # second level
        a_token = json_keys["a_token"]
        a_token_secret = json_keys["a_token_secret"]
        auth.set_access_token(a_token, a_token_secret)
        # we start the object api
        api = tweepy.API(auth,
                wait_on_rate_limit = True,
                wait_on_rate_limit_notify = True)
        self.api_obj = api
    def send_tweets(self, text_array, rate_limit_wait_time = 40):
        # https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits
        # as far as I can tell, the limit is 1 tweet every 40 seconds (36s)
        # ideally I would use Cursor here too but I can't figure out 
        # where the docs are so I am not adventorous.
        for i in text_array:
            self.api_obj.update_status(status = i)
            time.sleep(rate_limit_wait_time)

