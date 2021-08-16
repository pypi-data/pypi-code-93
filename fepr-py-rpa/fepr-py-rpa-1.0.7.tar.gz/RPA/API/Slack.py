import requests
from logging import getLogger

logger = getLogger(__name__)


class SlackBOT(object):
    def __init__(self, hubot_token: str):
        self.token = hubot_token

    def post_message(self, channel_id: str, post_text: str) -> requests.post:
        slack_message_api_url = "https://slack.com/api/chat.postMessage"
        param = {
            'token': self.token,
            'channel': channel_id,
            'text': post_text,
            'as_user': True,
        }
        requests.post(url=slack_message_api_url, params=param)
        logger.info(f"action:post_message, message:{post_text}")

    def post_file(self, channel_id, file_path: str, post_message: str) -> requests.post:
        slack_post_file_api_url = "https://slack.com/api/files.upload"
        files = {'file': open(file_path, 'rb')}
        param = {
            'token': self.token,
            'channels': channel_id,
            'initial_comment': post_message,
        }
        return requests.post(url=slack_post_file_api_url, params=param, files=files)
