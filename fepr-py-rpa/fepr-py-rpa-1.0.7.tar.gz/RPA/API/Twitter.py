import tweepy
from tweepy.api import API

class Twitter(object):
    """tweepyをユーザーデータ取得のみを簡易操作するためのクラスです。
    """
    def __init__(self, CONSUMER_KEY: str, CONSUMER_SECRET: str, ACCESS_TOKEN: str, ACCESS_TOKEN_SECRET: str):
        """入力されたトークンをセットし、APIを操作するための状態を整えます。

        Args:
            CONSUMER_KEY (str): カスタマーキー
            CONSUMER_SECRET (str): カスタマーシークレット
            ACCESS_TOKEN (str): アクセストークン
            ACCESS_TOKEN_SECRET (str): アクセストークンシークレット
        
        Note:
            トークンの発行はこちらから
            https://developer.twitter.com/en/portal/projects-and-apps
        """
        self.__CONSUMER_KEY = CONSUMER_KEY
        self.__CONSUMER_SECRET = CONSUMER_SECRET
        self.__ACCESS_TOKEN = ACCESS_TOKEN
        self.__ACCESS_TOKEN_SECRET = ACCESS_TOKEN_SECRET

        self.__auth = tweepy.OAuthHandler(self.__CONSUMER_KEY, self.__CONSUMER_SECRET)
        self.__auth.set_access_token(self.__ACCESS_TOKEN, self.__ACCESS_TOKEN_SECRET)
        self.__api: API = tweepy.API(self.__auth,wait_on_rate_limit = True)
    
    def load_user_data(self, screen_name):
        user = self.__api.get_user(screen_name)
        
        return user