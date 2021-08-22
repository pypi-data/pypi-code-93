import requests, json, re

from PSAW import PSAWExceps


class PSAWConnect:
    def __init__(self, uname, pword):
        self.username = uname
        self.password = pword
        self._userlogin()

    def _userlogin(self):
        
       # Function to login(don't use this)
        
        global _client
        headers = {
            "x-csrftoken": "a",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
            "referer": "https://scratch.mit.edu",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        data = json.dumps({"username": self.username, "password": self.password})
        request = requests.post(f"https://scratch.mit.edu/login/", data=data, headers=headers)
        try:
            self.session_id = re.search('"(.*)"', request.headers["Set-Cookie"]).group()
            self.token = request.json()[0]["token"]
        except AttributeError:
            raise PSAWExceps.InvalidCredentials('Invalid Username or Password!')
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;",
            "referer": "https://scratch.mit.edu",
        }
        request = requests.get("https://scratch.mit.edu/csrf_token/", headers=headers)
        self.csrf_token = re.search("scratchcsrftoken=(.*?);", request.headers["Set-Cookie"]).group(1)
        _client = f"https://api.scratch.mit/users/{self.username}/"
        self.headers = {
            "x-csrftoken": self.csrf_token,
            "X-Token": self.token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken="
                      + self.csrf_token
                      + ";scratchlanguage=en;scratchsessionsid="
                      + self.session_id
                      + ";",
            "referer": "https://scratch.mit.edu",
        }

    def print_messages(self, all:bool=True, limit:int=10, filter:str="all", user:str=""):
        if user == "":
            res = requests.get(f"https://api.scratch.mit.edu/users/{self.username}/messages?x-token={self.token}&filter={filter}&limit={limit}")
            res = res.json()
            if all:
                for dict in res:
                    if dict["type"] == "addcomment":
                        _actor = dict["actor_username"]
                        _comment_frag = dict["comment_fragment"]
                        _comment_src = dict["comment_obj_title"]
                        print(f"{_actor} sent you a message: {_comment_frag} in {_comment_src}".replace('&#39;', '\''))
                    elif dict["type"] == "studioactivity":
                        _studio = dict["title"]
                        print(f"new activity in: {_studio}".replace('&#39;', '\''))
                    elif dict["type"] == "curatorinvite":
                        _actor = dict["actor_username"]
                        _studio = dict["title"]
                        print(f"{_actor} has invited you to {_studio}".replace('&#39;', '\''))
                    elif dict["type"] == "followuser":
                        _actor = dict["actor_username"]
                        print(f"{_actor} is now following you!".replace('&#39;', '\''))
                    print("\n")
            else:
                for dict in res in range(limit):
                    if dict["type"] == "addcomment":
                        _actor = dict["actor_username"]
                        _comment_frag = dict["comment_fragment"]
                        _comment_src = dict["comment_obj_title"]
                        print(f"{_actor} sent you a message: {_comment_frag} in {_comment_src}".replace('&#39;', '\''))
                    elif dict["type"] == "studioactivity":
                        _studio = dict["title"]
                        print(f"new activity in: {_studio}".replace('&#39;', '\''))
                    elif dict["type"] == "curatorinvite":
                        _actor = dict["actor_username"]
                        _studio = dict["title"]
                        print(f"{_actor} has invited you to {_studio}".replace('&#39;', '\''))
                    elif dict["type"] == "followuser":
                        _actor = dict["actor_username"]
                        print(f"{_actor} is now following you!".replace('&#39;', '\''))
                    print("\n")
        else:
            if self.user_exists(user):
                res = requests.get(f"https://api.scratch.mit.edu/users/{user}/messages?x-token={self.token}&filter={filter}&limit={limit}")
                res = res.json()
                if all:
                    for dict in res:
                        if dict["type"] == "addcomment":
                            _actor = dict["actor_username"]
                            _comment_frag = dict["comment_fragment"]
                            _comment_src = dict["comment_obj_title"]
                            print(f"{_actor} sent you a message: {_comment_frag} in {_comment_src}".replace('&#39;', '\''))
                        elif dict["type"] == "studioactivity":
                            _studio = dict["title"]
                            print(f"new activity in: {_studio}".replace('&#39;', '\''))
                        elif dict["type"] == "curatorinvite":
                            _actor = dict["actor_username"]
                            _studio = dict["title"]
                            print(f"{_actor} has invited you to {_studio}".replace('&#39;', '\''))
                        elif dict["type"] == "followuser":
                            _actor = dict["actor_username"]
                            print(f"{_actor} is now following you!".replace('&#39;', '\''))
                        print("\n")
                else:
                    for dict in res in range(limit):
                        if dict["type"] == "addcomment":
                            _actor = dict["actor_username"]
                            _comment_frag = dict["comment_fragment"]
                            _comment_src = dict["comment_obj_title"]
                            print(f"{_actor} sent you a message: {_comment_frag} in {_comment_src}".replace('&#39;', '\''))
                        elif dict["type"] == "studioactivity":
                            _studio = dict["title"]
                            print(f"new activity in: {_studio}".replace('&#39;', '\''))
                        elif dict["type"] == "curatorinvite":
                            _actor = dict["actor_username"]
                            _studio = dict["title"]
                            print(f"{_actor} has invited you to {_studio}".replace('&#39;', '\''))
                        elif dict["type"] == "followuser":
                            _actor = dict["actor_username"]
                            print(f"{_actor} is now following you!".replace('&#39;', '\''))
                        print("\n")
            else:
                raise Exception("That user does not exist!")

    def profilecomment(self, message:str="None", user:str="", commentee_id:str="", parent_id:str=""):

        content = {
            "commentee_id": commentee_id,
            "content": message,
            "parent_id": parent_id,
        }
        if self.user_exists(user):
            return requests.post(f"https://scratch.mit.edu/site-api/comments/user/{user}/add/",headers=self.headers,data=json.dumps(content))
    
    def number_of_messages(self, user:str):
        if user=="None":
            user = _client
        if self.user_exists(user):
            res = requests.get(f"https://api.scratch.mit.edu/users/{user}/messages/count").json()["count"]
            return res

    def user_exists(self, user:str):
        try:
            res = requests.get(f"scratch.mit.edu/users/{user}")
            print(res)
            return True
        except:
            raise PSAWExceps.InvalidUser("Invalid Username!")

    def follow(self, follow:str):
        if self.user_exists(follow):
            return requests.put(
                "https://scratch.mit.edu/site-api/users/followers/"+ follow + "/add/?usernames=" + self.username, headers=self.headers,
            )

    def unfollow(self, unfollow:str):
        if self.user_exists(unfollow):
            return requests.put(
                "https://scratch.mit.edu/site-api/users/followers/"+ unfollow + "/remove/?usernames=" + self.username, headers=self.headers,
            )

    def love(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.post(f"https://api.scratch.mit.edu/proxy/projects/{proj_id}/loves/user/{self.username}", headers=self.headers).json()
        
    def unlove(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.delete(f"https://api.scratch.mit.edu/proxy/projects/{proj_id}/loves/user/{self.username}", headers=self.headers).json()

    def get_project_loves(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.get(f"https://api.scratch.mit.edu/projects/{proj_id}/", headers=self.headers).json()["stats"]["loves"]

    def get_project_faves(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.get(f"https://api.scratch.mit.edu/projects/{proj_id}/", headers=self.headers).json()["stats"]["favorites"]

    def fave(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.post(f"https://api.scratch.mit.edu/proxy/projects/{proj_id}/favorites/user/{self.username}", headers=self.headers).json()

    def unfave(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.delete(f"https://api.scratch.mit.edu/proxy/projects/{proj_id}/favorites/user/{self.username}", headers=self.headers).json()

    def get_projects(self, user:str=""):
        if user == "":
            user = self.username
        else:
            if self.user_exists(user):
                pass
            else:
                raise Exception("That user does not exist!")
        
        return requests.get(f"https://api.scratch.mit.edu/users/{user}/projects/").json() #You can loop through what this returns btw

    def get_messages(self, limit:int=10, filter:str="all", user:str=""):
        if user == "":
            return requests.get(f"https://api.scratch.mit.edu/users/{self.username}/messages?x-token={self.token}&filter={filter}&limit={limit}").json()
        else:
            if self.user_exists(user):
                return requests.get(f"https://api.scratch.mit.edu/users/{user}/messages?x-token={self.token}&filter={filter}&limit={limit}").json()

    def get_project_views(self, proj_id:int):
        if self.project_exists(proj_id):
            return requests.get(f"https://api.scratch.mit.edu/projects/{proj_id}/", headers=self.headers).json()["stats"]["views"]

    def project_exists(self, proj_id:int):
        try:
            res = requests.get(f"https://api.scratch.mit.edu/projects/{proj_id}/", headers=self.headers)
        except:
            raise PSAWExceps.InvalidProjectID("Invalid Project ID!")

    def get_health(self):
        return requests.get("https://api.scratch.mit.edu/health".json())

    def get_news(self):
        return requests.get("https://api.scratch.mit.edu/news").json()

    def get_featured(self):
        return requests.get("https://api.scratch.mit.edu/proxy/featured").json()

    def get_followers(self, user:str="", all:bool=True, limit:int=50):
        if user == "":
            user = self.username
        
        if all:
            followers = []
            res = requests.get(f"https://api.scratch.mit.edu/users/{user}/followers/").json()
            for dict in res:
                followers.append(dict["username"])
            return followers
        else:
            followers = []
            res = requests.get(f"https://api.scratch.mit.edu/users/MelonMars/followers/?limit={limit}")
            for dict in res:
                followers.append(dict["username"])
            return followers

    def get_user_faves(self, user:str="", all:bool=True, limit:int=50):
        if all:
            res = requests.get(f"https://api.scratch.mit.edu/users/{user}/favorites").json()
            faves = {}
            for dict in res:
                faves[dict["title"]] = dict["id"]
            return faves
        else:
            res = requests.get(f"httpsL//api.scratch.mit.edu/users/{user}/favorites?limit={limit}").json()
            faves = {}
            for dict in res:
                faves[dict["title"]] = dict["id"]
            return faves
