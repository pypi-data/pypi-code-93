from requests import Session

class AYBSession(Session):

    def urljoiner(self,url):
        result = self.prefix_url
        if not url.beginswith('/'):
            result+='/'
        result+=url
        return 


    def __init__(self, prefix_url=None, *args, **kwargs):
        super(AYBSession, self).__init__(*args, **kwargs)
        if prefix_url.endswith('/'):
            prefix_url = prefix_url[:-1]    
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = self.urljoiner(url)
        return super(AYBSession, self).request(method, url, *args, **kwargs)