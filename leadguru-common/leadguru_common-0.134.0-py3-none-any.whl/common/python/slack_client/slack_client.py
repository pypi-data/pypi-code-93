import requests
import aiohttp
import asyncio
import websockets
import json
import io
from urllib import parse

from websockets.client import WebSocketClientProtocol

from .methods import SlackMethods


class SlackClient:
    base_url = 'https://slack.com/api/'
    token: str
    cookies: dict
    socket: WebSocketClientProtocol

    def __init__(self, token: str, cookies):
        self.token = token

        if isinstance(cookies, list):
            self.cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        else:
            self.cookies = cookies

    def join_channels(self, channels):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = asyncio.gather(*[self.join_channel_async(channel) for channel in channels])
        results = loop.run_until_complete(tasks)
        loop.close()
        return results

    def leave_channels(self, channels):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = asyncio.gather(*[self.leave_channel_async(channel) for channel in channels])
        results = loop.run_until_complete(tasks)
        loop.close()
        return results

    async def join_channel_async(self, channel):
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}{SlackMethods.conversations_join}?{self.__channel_payload(channel)}'
            async with session.post(url=url, cookies=self.cookies) as response:
                return await response.json()

    async def leave_channel_async(self, channel):
        async with aiohttp.ClientSession() as session:
            url = f'{self.base_url}{SlackMethods.conversations_leave}?{self.__channel_payload(channel)}'
            async with session.post(url=url, cookies=self.cookies) as response:
                return await response.json()

    def get_profile(self, user_id: str = None):
        url = f'{self.base_url}{SlackMethods.profile_get}?{self.__token_payload()}'
        if user_id:
            url += f"&user={user_id}"

        return requests.get(url=url, cookies=self.cookies).json()

    def update_profile(self, profile):
        url = f'{self.base_url}{SlackMethods.profile_set}?{self.__update_profile_payload(profile)}'
        return requests.post(url=url, cookies=self.cookies).json()

    def update_profile_photo(self, photo_url):
        url = f'{self.base_url}{SlackMethods.profile_set_photo}'
        with requests.get(photo_url) as img_resp:
            if img_resp.status_code != 200:
                raise Exception(f"Invalid url: {photo_url}")
            image = io.BytesIO(img_resp.content)

            files = {"image": image}
            headers = {"Authorization": f"Bearer {self.token}"}

            return requests.post(url=url, files=files, headers=headers, cookies=self.cookies, verify=False).json()

    def get_conversations_list(self):
        url = f'{self.base_url}{SlackMethods.conversations_list}?' \
              f'{self.__conversation_list_payload(["public_channel"])}'
        return requests.get(url=url, cookies=self.cookies).json()

    def get_im_list(self):
        url = f'{self.base_url}{SlackMethods.conversations_list}?{self.__conversation_list_payload(["im"])}'
        return requests.get(url=url, cookies=self.cookies).json()

    def im_open(self, user: str):
        url = f'{self.base_url}{SlackMethods.conversations_open}?{self.__im_open_payload(user)}'
        return requests.post(url=url, cookies=self.cookies).json()

    def delete_message(self, channel: str, ts: str):
        url = f'{self.base_url}{SlackMethods.chat_delete}?{self.__delete_message_payload(channel, ts)}'
        return requests.post(url=url, cookies=self.cookies).json()

    def update_message(self, channel: str, ts: str, text: str):
        url = f'{self.base_url}{SlackMethods.chat_update}?{self.__update_message_payload(channel, ts, text)}'
        return requests.post(url=url, cookies=self.cookies).json()

    def conversations_history(self, channel: str, ts: str=None):
        url = f'{self.base_url}{SlackMethods.conversations_history}?{self.__channel_payload(channel, ts)}'
        return requests.get(url=url, cookies=self.cookies).json()

    def conversations_replies(self, channel: str, ts: str):
        url = f'{self.base_url}{SlackMethods.conversations_replies}?{self.__ts_payload(channel, ts)}'
        return requests.get(url=url, cookies=self.cookies).json()

    def get_presense(self, user: str=None):
        url = f'{self.base_url}{SlackMethods.users_get_presence}?{self.__presense_payload(user)}'
        return requests.get(url=url, cookies=self.cookies).json()

    def post_message(self, channel: str, text: str):
        url = f'{self.base_url}{SlackMethods.chat_post_message}?{self.__post_message_payload(channel, text)}'
        return requests.post(url=url, cookies=self.cookies).json()

    def users_list(self, cursor=None, limit: int=1000):
        url = f'{self.base_url}{SlackMethods.users_list}?{self.__token_payload()}'
        if cursor:
            url += f'&cursor={cursor}'

        if limit:
            url += f'&limit={limit}'

        return requests.get(url=url, cookies=self.cookies).json()

    def user_info(self, user: str):
        url = f'{self.base_url}{SlackMethods.users_info}?{self.__user_info_payload(user)}'
        return requests.get(url=url, cookies=self.cookies).json()

    def get_reactions(self, channel: str, ts: str):
        url = f'{self.base_url}{SlackMethods.reactions_get}?{self.__get_reactions_payload(channel, ts)}'
        return requests.get(url=url, cookies=self.cookies).json()


    def rtm_connect(self, callback):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.__consumer(callback))
        loop.run_forever()

    async def __consumer(self, callback):
        url = f'{self.base_url}{SlackMethods.rtm_connect}?{self.__token_payload()}'
        response = requests.get(url=url, cookies=self.cookies).json()
        web_socket_url = response['url']
        async with websockets.connect(uri=web_socket_url) as websocket:
            self.socket = websocket
            async for message in websocket:
                await callback(json.loads(message))

    def __token_payload(self):
        return parse.urlencode({'token': self.token})

    def __user_info_payload(self, user):
        payload = {
            'token': self.token,
            'user': user
        }
        return parse.urlencode(payload)

    def __post_message_payload(self, channel, text):
        payload = {
            'token': self.token,
            'channel': channel,
            'text': text
        }
        return parse.urlencode(payload)

    def __update_message_payload(self, channel, ts, text):
        payload = {
            'token': self.token,
            'channel': channel,
            'ts': ts,
            'text': text
        }
        return parse.urlencode(payload)

    def __delete_message_payload(self, channel, ts):
        payload = {
            'token': self.token,
            'channel': channel,
            'ts': ts
        }
        return parse.urlencode(payload)

    def __conversation_list_payload(self, types: list):
        payload = {
            'token': self.token,
            'types': ','.join(types)
        }
        return parse.urlencode(payload)

    def __im_open_payload(self, user: str):
        payload = {
            'token': self.token,
            'users': user,
            'types': 'im'
        }
        return parse.urlencode(payload)

    def __update_profile_payload(self, profile):
        payload = {
            'token': self.token,
            'profile': profile
        }
        return parse.urlencode(payload)

    def __channel_payload(self, channel, ts=None):
        payload = {
            'token': self.token,
            'channel': channel
        }

        if ts:
            payload["ts"] = ts
            payload["limit"] = 1
            payload["inclusive"] = True

        return parse.urlencode(payload)

    def __presense_payload(self, user: str=None):
        payload = {
            'token': self.token,
        }

        if user:
            payload["user"] = user
        return parse.urlencode(payload)

    def __ts_payload(self, channel: str, ts: str):
        payload = {
            'token': self.token,
            'channel': channel,
            'ts': ts
        }
        return parse.urlencode(payload)

    def __get_reactions_payload(self, channel, ts):
        payload = {
            'token': self.token,
            'full': True,
            'channel': channel,
            'timestamp': ts
        }
        return parse.urlencode(payload)
