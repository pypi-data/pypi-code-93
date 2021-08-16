import os
import requests
import mimetypes
from ..logger import logger


class Chatwork(object):
    def __init__(self, token):
        self.token = token

    def post_message(self, room_id, post_text):
        post_message_api_url = f'https://api.chatwork.com/v2/rooms/{room_id}/messages'
        header = {'X-ChatWorkToken': self.token}
        param = {'body': post_text}

        logger.info({
            "action": "post_message",
            "status": "running",
            "message":{
                "room_id": room_id,
                "post_text": post_text
            }
        })

        requests.post(post_message_api_url, headers=header, params=param)

        logger.info({
            "action": "post_message",
            "status": "Success!"
        })

    def post_file(self, room_id: str, file_path: str, post_text: str):
        mime = mimetypes.guess_type(file_path)[0]
        file_name = os.path.basename(file_path)
        url = f'https://api.chatwork.com/v2/rooms/{room_id}/files'
        file_bin = open(file_path, 'rb').read()

        logger.info({
            "action": "post_file",
            "status": "running",
            "message": {
                "room_id": room_id,
                "file_path": file_path,
                "post_text": post_text
            }
        })
        headers = {'X-ChatWorkToken': self.token}
        files = {
            'file': (file_name, file_bin, mime),
            'message': post_text,
        }
        requests.post(url, headers=headers, files=files)

        logger.info({
            "action": "post_file",
            "status": "Success!",
        })