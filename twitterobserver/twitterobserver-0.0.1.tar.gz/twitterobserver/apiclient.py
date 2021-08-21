

import time
import tweepy
import json
import sqlite3
from sqlite3 import Error
from datetime import datetime
from twitterobserver.db import db_instance, user_instance 

class api_client:
    def __init__(self, secrets_file, username, db_file):
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
        self.username = username
        self.db_obj = db_instance(db_file)
        my_date = datetime.now()
        self.query_date = my_date.isoformat()
    ## these 2 fucntions we could re-factor but lazy now.
    def get_friends(self):
        res_flw = tweepy.Cursor(self.api_obj.friends_ids,
                                screen_name = self.username,
                                count = 5000)
        local_users = self.get_all_user_ids()
        result_ids = [str(i) for i in res_flw.items()]
        # has to be a faster way to do this
        new_users = [i for i in result_ids if i not in local_users]
        old_users = [i for i in result_ids if i in local_users]
        print("# of DB users detected: {}".format(len(local_users)))
        print("# of old users detected: {}".format(len(old_users)))
        print("# of new users detected: {}".format(len(new_users)))
        #print(new_users)
        new_users_instances = self.get_api_user_info(new_users)
        old_users_instances = self.get_local_user_info(old_users)
        self.friends = new_users_instances + old_users_instances
    def get_followers(self):
        res_flw = tweepy.Cursor(self.api_obj.followers_ids,
                        screen_name = self.username,
                        count = 5000)
        local_users = self.get_all_user_ids()
        # has to be a faster way to do this
        new_users = [i for i in res_flw.items() if i not in local_users]
        old_users = [i for i in res_flw.items() if i in local_users]
        new_users_instances = self.get_api_user_info(new_users)
        old_users_instances = self.get_local_user_info(old_users)
        self.followers = new_users_instances + old_users_instances
    def get_all_user_ids(self):
        """
        From the database, extract all the user ids
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_obj.dbFile)
            c = conn.cursor()
            sql_str = """
            SELECT userId FROM users;
            """
            c.execute(sql_str)
            user_ids = c.fetchall()
            all_array = [i[0] for i in user_ids] 
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
        return all_array
    def get_local_user_info(self, user_id):
        conn = None
        try:
            conn = sqlite3.connect(self.db_obj.dbFile)
            c = conn.cursor()
            # '92631963'  '92632733'
            list_users =  user_id
            # from here https://stackoverflow.com/a/283801
            placeholder= '?'
            placeholders= ', '.join([placeholder for unused in list_users])
            sql_str = 'SELECT * FROM users WHERE userId IN ({})'.format(placeholders)
            c.execute(sql_str,list_users)
            all_users_tuple = c.fetchall()
            all_users_instances = []
            for i in all_users_tuple:
                tmp_dict = {
                    "userId": i[0],
                    "userURL": i[1],
                    "userScreenName" : i[2],
                    "userName" : i[3],
                    "userFriends": i[4],
                    "userFollowers": i[5]
                }
                all_users_instances.append(user_instance(tmp_dict))
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
        return all_users_instances
    def get_api_user_info(self, user_id):
        """
        Note: See that this function uses the endpoints of the api
        GET users/show -> rate limie of 1 per second  
        https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits
        # here I also thing I cannot use the cursor because there is not
        # pagination?   
        """
        if len(user_id) == 0:
            return []
        else:
            user_array = []
            for i in user_id:
                try:
                    user_inst = self.api_obj.get_user(i)
                    user_array.append(user_instance(user_inst))
                    time.sleep(1.5)
                except tweepy.error.TweepError as e:
                    print(user_id)
                    print(e)
                    continue
            return user_array
    def update_query_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_obj.dbFile)
            c = conn.cursor()
            sql_str = """
            INSERT OR IGNORE INTO queries (queryId,trUserId) VALUES(?,?);
            """
            ## not sure about the extra comma
            c.execute(sql_str, (self.query_date,self.username))
            print('We have inserted', c.rowcount, 'records to the table.')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    def update_relation_db(self):
        relat_arr = []
        if hasattr(self,"followers"):
            for i in self.followers:
                r_tpl = ("follower", i.userId, self.query_date)
                relat_arr.append(r_tpl)
        if hasattr(self,"friends"):
            for i in self.friends:
                r_tpl = ("friend", i.userId, self.query_date)
                relat_arr.append(r_tpl)
        # now I have all the items
        conn = None
        try:
            conn = sqlite3.connect(self.db_obj.dbFile)
            c = conn.cursor()
            sql_str = """
             INSERT OR IGNORE INTO qfRelation (relationType,userId,queryId) VALUES(?,?,?);
             """
            c.executemany(sql_str, relat_arr)
            print('We have inserted', c.rowcount, 'records to the table.')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    def update_users_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_obj.dbFile)
            c = conn.cursor()
            sql_str = """
             INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?);
             """
            if hasattr(self,"followers"):
                records_fll = [i.export_tuple() for i in self.followers]
            else:
                records_fll = []
            if hasattr(self,"friends"):
                records_friends = [i.export_tuple() for i in self.friends]
            else:
                records_friends = []
            # this is weird -> https://stackoverflow.com/questions/1720421
            all_records = records_fll + records_friends
            c.executemany(sql_str, all_records)
            print('We have inserted', c.rowcount, 'records to the table.')
            conn.commit()
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    def update_db(self):
        self.update_query_db()
        self.update_users_db()
        self.update_relation_db()



