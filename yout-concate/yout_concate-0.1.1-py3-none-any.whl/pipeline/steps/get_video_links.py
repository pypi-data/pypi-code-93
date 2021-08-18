import urllib.request
import json
from yt_concate.settings import API_KEY
from yt_concate.pipeline.steps.step import Step
import logging


class GetVideoLinks(Step):

    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        channel_id = inputs["channel_id"]
        if utils.check_video_list_exists(channel_id):
            video_links = self.read_file(utils, channel_id)
            logger.warning('Video list already existed.')
            return video_links



        base_video_url = 'https://www.youtube.com/watch?v='
        base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

        first_url = base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(API_KEY, channel_id)

        video_links = []
        url = first_url
        while True:
            inp = urllib.request.urlopen(url)
            resp = json.load(inp)

            for i in resp['items']:
                if i['id']['kind'] == "youtube#video":
                    video_links.append(base_video_url + i['id']['videoId'])

            try:
                next_page_token = resp['nextPageToken']
                url = first_url + '&pageToken={}'.format(next_page_token)
            except:
                break

        self.write_to_file(video_links, utils, channel_id)
        return video_links

    @staticmethod
    def write_to_file(video_list, utils, channel_id):
        path = utils.get_video_list_path(channel_id)
        with open(path, 'w', encoding='utf-8') as fp:
            for url in video_list:
                fp.write(url+'\n')


    def read_file(self, utils, channel_id):
        video_links = []
        path = utils.get_video_list_path(channel_id)
        with open(path,'r') as fp:
            for url in fp:
                video_links.append(url.rstrip('\n'))
        return video_links
