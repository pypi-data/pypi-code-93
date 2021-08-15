head={
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'
}

#作品
class works(object):
    def __init__(self,id):
        import requests,json
        global head
        r=requests.get("https://code.xueersi.com/api/compilers/v2/{}?id={}".format(id,id),headers=head)
        r.encoding="utf-8"
        r=r.json()
        self.data={
            "作品id":r["data"]["id"],
            "作者id":r["data"]["user_id"],
            "作品名":r["data"]["name"],
            "作品语言":r["data"]["lang"],
            "发布时间":r["data"]["created_at"],
            "更新时间":r["data"]["updated_at"],
            "点赞":r["data"]["likes"],
            "点踩":r["data"]["unlikes"],
            "浏览":r["data"]["views"],
            "评论":r["data"]["comments"],
            "热度":r["data"]["popular_score"]
        }
    def works_id(self):
        return self.data["作品id"]
    def user_id(self):
        return self.data["作者id"]
    def works_name(self):
        return self.data["作品名"]
    def lang(self):
        return self.data["作品语言"]
    def created(self):
        return self.data["发布时间"]
    def update(self):
        return self.data["更新时间"]
    def like(self):
        return  self.data["点赞"]
    def unlike(self):
        return self.data["点踩"]
    def view(self):
        return self.data["浏览"]
    def comment(self):
        return self.data["评论"]
    def hot(self):
        return self.data["热度"]
def is_works(id):
    import requests,json
    global head
    r=requests.get("https://code.xueersi.com/api/compilers/v2/{}?id={}".format(id,id),headers=head)
    r.encoding="utf-8"
    r=r.json()
    try:
        if r["status_code"]=="404":
            return False
    except:
        return True
def is_like(id):
    import requests,json
    global head
    r=requests.get("https://code.xueersi.com/api/python/1/is_like?id={}&lang=code&form=python".format(id),headers=head)
    r.encoding="utf-8"
    r=r.json()
    return r["data"]
def is_unlike(id):
    import requests,json
    global head
    r=requests.get("https://code.xueersi.com/api/python/1/is_unlike?id={}&lang=code&form=python".format(id),headers=head)
    r.encoding="utf-8"
    r=r.json()
    return r["data"]

#作者
class user(object):
    def user(self,id):
        import requests,json
        global head
        r=requests.get("https://code.xueersi.com/api/space/profile?user_id={}".format(id),headers=head)
        r.encoding="utf-8"
        r=r.json()
        self.data={
            "作者id":r["data"]["id"],
            "作者名字":r["data"]["realname"],
            "签名":r["data"]["signature"],
            "粉丝":r["data"]["fans"],
            "关注":r["data"]["follows"]
        }
    def user_id(self):
        return self.data["作者id"]
    def user_name(self):
        return self.data["作者名字"]
    def signature(self):
        return self.data["签名"]
    def fans(self):
        return self.data["粉丝"]
    def follow(self):
        return  self.data["关注"]
def is_user(id):
    import requests,json
    global head
    r=requests.get("https://code.xueersi.com/api/space/profile?user_id={}".format(id),headers=head)
    r.encoding="utf-8"
    r=r.json()
    try:
        if r["status_code"]=="404":
            return False
    except:
        return True
def is_follow(id):
    import requests,json
    global head
    r=requests.get("https://code.xueersi.com/api/space/profile?user_id={}".format(id),headers=head)
    r.encoding="utf-8"
    r=r.json()
    return bool(r["data"]["is_follow"])