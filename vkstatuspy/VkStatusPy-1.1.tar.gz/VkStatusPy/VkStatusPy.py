import requests


class VkStatusException(Exception):
    pass


class VkStatus():

    def __init__(self, token):
        self.token = token

    def set_status(self, text):

        token = self.token
        status = requests.get(f"https://api.vk.com/method/status.set?text={text}&v=5.52&access_token={token}").json()

        try:
            if status['response']:
                return 1

        except KeyError:

            if int(status['error']['error_code']) == 100:
                raise VkStatusException("Error [100]: invalid user_id")
            if int(status['error']['error_code']) == 221:
                raise VkStatusException("Error [221]: The user turned off the broadcast of audio titles in the status.")

    def set_status_group(self, text, group_id):

        token = self.token
        status = requests.get(f"https://api.vk.com/method/status.set?text={text}&group_id={group_id}&v=5.52&access_token={token}").json()

        try:
            if status['response']:
                return 1

        except KeyError:

            if int(status['error']['error_code']) == 15:
                raise VkStatusException("Error [15]: Access denied: no access to this group")

            if int(status['error']['error_code']) == 100:
                raise VkStatusException("Error [100]: invalid group_id")

            if int(status['error']['error_code']) == 221:
                raise VkStatusException("Error [221]: The user/group turned off the broadcast of audio titles in the status.")

    def get_status(self, user_id):

        token = self.token
        status = requests.get(f"https://api.vk.com/method/status.get?user_id={user_id}&v=5.52&access_token={token}").json()

        try:
            if status['response']['text']:
                return status['response']['text']

        except KeyError:
            if int(status['error']['error_code']) == 100:
                raise VkStatusException("Error [100]: invalid user_id")

    def get_status_group(self, group_id):

        token = self.token
        status = requests.get(f"https://api.vk.com/method/status.get?group_id={group_id}&v=5.52&access_token={token}").json()

        try:
            if status['response']['text']:
                return status['response']['text']

        except KeyError:

            if int(status['error']['error_code']) == 15:
                raise VkStatusException("Error [15]: Access denied: no access to this group")

            if int(status['error']['error_code']) == 100:
                raise VkStatusException("Error [100]: invalid group_id")
