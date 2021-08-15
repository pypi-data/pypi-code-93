import time
import urllib.request
import json

from .step import Step
from yt_concate.settings import API_KEY


class GetVideoList(Step):
    def process(self, data, inputs, utils, log):
        log.info("=== Getting video list... ===")
        start = time.time()
        channel_id = inputs["channel_id"]

        if utils.video_list_file_exists(channel_id):
            log.info(f"Found existing video list file: {channel_id}")
            return self.read_file(utils.get_video_list_filepath(channel_id))

        base_video_url = 'https://www.youtube.com/watch?v='
        base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

        first_url = base_search_url + 'key={}&channelId={}&part=snippet,id&order=date&maxResults=25'.format(API_KEY,
                                                                                                            channel_id)

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
            except KeyError:
                log.error("KeyError when getting video list, but doesn't matter.")
                break
        self.write_to_file(video_links, utils.get_video_list_filepath(channel_id))

        end = time.time()
        if utils.video_list_file_exists(channel_id):
            log.info(f"Video list got: Took {end - start} secs.")

        return video_links

    @staticmethod
    def write_to_file(video_links, filepath):
        with open(filepath, "w") as f:
            for url in video_links:
                f.write(url + "\n")

    @staticmethod
    def read_file(filepath):
        video_links = []
        with open(filepath, "r") as f:
            for url in f:
                video_links.append(url.strip())
        return video_links
