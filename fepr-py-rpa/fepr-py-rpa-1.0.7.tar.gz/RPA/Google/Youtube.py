import pickle
from googleapiclient.discovery import Resource, build
import os


class ChannelErr(Exception):
    """チャンネルの情報を取得できない場合に発生。
    大概はそのチャンネルが存在しないことがおおい。
    """


class Channel(object):
    def __init__(self) -> None:
        API_SERVICE_NAME = "youtube"
        API_VERSION = "v3"
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                cred = pickle.load(token)

        self.__channel: Resource = build(API_SERVICE_NAME, API_VERSION, credentials=cred)

    def get_info(self, channel_id: str) -> dict:
        try:
            channel_response = self.__channel.channels().list(
                part = 'snippet,statistics',
                id = channel_id
                ).execute()
        except:
            raise ChannelErr(f'指定したチャンネル {channel_id} は存在しません')
        
        return channel_response