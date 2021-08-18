class TikTokApi:
    """
    Uses functionalities from the TikTokApi
    package and makes them more user friendly.
    """
    def __init__(self):
        from TikTokApi import TikTokApi
        self.ttapi = TikTokApi(debug=True)
        global ttapi
        ttapi = self.ttapi
        self.Music = music
        self.TikTok = tiktok
        self.User = userData
class userData:
    def __init__(self,username:str):
        self.obj = dict(ttapi.get_user(username))
        self.name = username
    def getDesc(self):
        obj = self.obj
        e = userData.getseoProps(obj).get("metaParams").get("description")
        return e
    def getKeywords(self):
        obj = self.obj
        e=userData.getseoProps(obj).get("metaParams").get("keywords")
        for i in e.split(","):
            yield i
    def getName(self):
        obj = self.obj
        e = userData.getseoProps(obj).get("metaParams").get("name")
        return e
    def getseoProps(self):
        obj = self.obj
        return obj.get("seoProps")
    def getUniqueID(self):
        obj = self.obj
        obj.get("uniqueId")
    def getItems(self):
        obj = self.obj
        return str(obj.items())
class music:
    def __init__(self,title:str):
        self.term = title
    def search(self):
        term = self.term
        A=ttapi.search_for_music(term)
        return A
class tiktok:
    def __init__(self,url:str):
        self.url = url
        self.ttapi = ttapi
        self.data = ttapi.get_tiktok_by_url(self.url)
    def null(self):
        o = self.data.copy()
        print(o)