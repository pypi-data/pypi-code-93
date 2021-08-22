import re
import requests
from bs4 import BeautifulSoup as soup

URL = "https://insta-stories.online"


class InstaViewer:
    def __init__(self, username, url=URL):
        self.url = url
        self.session = requests.Session()
        self.username = username
        self.user_id = None
        self.token = None
        self.setup()

    def setup(self):
        self.session.headers.update({"user-agent": "respect"})

        # get homepage
        response = self.session.get(f"{URL}/{self.username}")
        html = soup(response.text, "html.parser")

        # set csrf token
        csrftoken = html.find("meta", {"name": "csrf-token"})["content"]
        self.session.headers.update({"x-csrf-token": csrftoken})

        # save user id
        self.user_id = re.search(r"app_insta\.user_id = '(\d+)'", response.text).group(1)

        # save token
        #self.token = re.search(r"app_insta\.token = \"(\w+)\"", response.text).group(1)

    def get_stories(self, format=None):
        response = self.session.post(f"{URL}/search", data={
            "getStories": "true", 
            "userId": self.user_id,
            #"token": self.token
        })
        response.raise_for_status()
        if format == "json":
            return response.text
        return response.json()

    def get_posts(self, format=None):
        response = self.session.post(f"{URL}/search", data={
            "getPosts": "true", 
            "userId": self.user_id,
            #"token": self.token
        })
        response.raise_for_status()
        if format == "json":
            return response.text
        return response.json()
